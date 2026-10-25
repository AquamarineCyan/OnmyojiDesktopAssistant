import time
from threading import Thread

from PIL.Image import Image
from PIL.ImageQt import ImageQt
from PySide6.QtCore import QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSizePolicy,
    QSplitter,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CheckBox,
    FluentIcon,
    HeaderCardWidget,
    InfoBar,
    InfoBarPosition,
    PushButton,
    SpinBox,
    TableWidget,
)

from ..utils.log import logger
from ..utils.ocr_engine import OcrData, ocr_manager
from ..utils.screenshot import ScreenShot
from ..utils.window import window_manager

BOX_COLOR = QColor(255, 59, 48)
"""识别框颜色"""


class PreviewLabel(QLabel):
    """截图预览标签：按控件尺寸缩放图像并绘制识别框"""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(220, 160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setText("点击「识别当前界面」查看识别结果")

        self._pixmap: QPixmap = None
        self._boxes: list[OcrData] = []

    def set_preview(self, pixmap: QPixmap, boxes: list[OcrData]) -> None:
        """设置预览图像与识别框

        Args:
            pixmap (QPixmap): 原始截图
            boxes (list[OcrData]): 需要绘制的识别结果
        """
        self._pixmap = pixmap
        self._boxes = boxes
        # QLabel 同时设置文本与 pixmap 会叠加显示，这里先清掉占位文本
        self.setText("")
        self._refresh()

    def clear_preview(self, text: str = "") -> None:
        """清空预览并显示占位文本"""
        self._pixmap = None
        self._boxes = []
        self.clear()
        self.setText(text)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh()

    def _refresh(self) -> None:
        """按当前尺寸重绘预览图"""
        if self._pixmap is None or self._pixmap.isNull():
            return
        if self.width() <= 0 or self.height() <= 0:
            return

        scaled = self._pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        if scaled.isNull():
            return

        if self._boxes:
            painter = QPainter(scaled)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            fx = scaled.width() / self._pixmap.width()
            fy = scaled.height() / self._pixmap.height()

            font = painter.font()
            font.setPointSize(9)
            painter.setFont(font)
            metrics = painter.fontMetrics()

            for index, item in enumerate(self._boxes, 1):
                rect = QRectF(
                    item.x1 * fx,
                    item.y1 * fy,
                    (item.x2 - item.x1) * fx,
                    (item.y2 - item.y1) * fy,
                )
                painter.setPen(QPen(BOX_COLOR, 2))
                painter.drawRect(rect)

                # 序号标签放在识别框左上角，避免框过小看不清
                text = str(index)
                text_width = metrics.horizontalAdvance(text) + 4
                text_height = metrics.height()
                label_rect = QRectF(rect.left(), max(0.0, rect.top() - text_height), text_width, text_height)
                painter.fillRect(label_rect, BOX_COLOR)
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, text)

            painter.end()

        self.setPixmap(scaled)


class OcrResultCard(HeaderCardWidget):
    """识别结果卡片"""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setTitle("识别结果")
        self.setBorderRadius(8)
        self.viewLayout.setContentsMargins(12, 8, 12, 12)

        self.table = TableWidget(self)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(6)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["#", "识别文本", "置信度", "区域 (x1, y1, x2, y2)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self._vBoxLayout = QVBoxLayout()
        self._vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self._vBoxLayout.addWidget(self.table, 1)
        self.viewLayout.addLayout(self._vBoxLayout)

        self._ocr_ms: float | None = None

    def set_results(self, results: list[OcrData], ocr_ms: float | None = None) -> None:
        """刷新结果表格与标题（数量、识别耗时）

        Args:
            results (list[OcrData]): 当前展示的识别结果
            ocr_ms (float): 本次识别耗时，不传则沿用上次
        """
        if ocr_ms is not None:
            self._ocr_ms = ocr_ms

        if self._ocr_ms is None:
            self.setTitle(f"识别结果（{len(results)} 条）")
        else:
            self.setTitle(f"识别结果（{len(results)} 条 · 耗时 {self._ocr_ms:.0f} ms）")

        self.table.setRowCount(0)
        self.table.setRowCount(len(results))

        for row, item in enumerate(results):
            values = [
                str(row + 1),
                item.text,
                f"{item.score:.2f}",
                f"({item.x1}, {item.y1}, {item.x2}, {item.y2})",
            ]
            for column, value in enumerate(values):
                cell = QTableWidgetItem(value)
                if column in (0, 2):
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, column, cell)


class OcrDetectionWidget(QWidget):
    """文字识别页面：识别当前游戏窗口界面并显示结果"""

    recognition_finished = Signal(object, object, float, float)
    """识别完成

    Args:
        image (Image): 截图（PIL Image）
        results (list[OcrData]): 识别结果
        capture_ms (float): 截图耗时（毫秒）
        ocr_ms (float): 文字识别耗时（毫秒）
    """

    recognition_failed = Signal(str)
    """识别失败

    Args:
        message (str): 失败原因
    """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self.setObjectName("OcrDetection")

        self._busy: bool = False
        self._pixmap: QPixmap = None
        self._results: list[OcrData] = []
        self._ocr_ms: float | None = None

        # 工具栏
        self.recognize_button = PushButton(FluentIcon.SEARCH, "识别当前界面")
        self.recognize_button.clicked.connect(self.start_recognition)

        self.auto_checkbox = CheckBox("自动识别")
        self.auto_checkbox.toggled.connect(self._auto_checkbox_toggled_handle)

        self.interval_label = BodyLabel("间隔")
        self.interval_spinbox = SpinBox()
        self.interval_spinbox.setRange(1, 60)
        self.interval_spinbox.setValue(2)
        self.interval_spinbox.setSuffix(" 秒")
        self.interval_spinbox.setFixedWidth(130)
        self.interval_spinbox.valueChanged.connect(self._auto_interval_changed_handle)

        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setSpacing(10)
        self.toolbar_layout.addWidget(self.auto_checkbox)
        self.toolbar_layout.addWidget(self.interval_label)
        self.toolbar_layout.addWidget(self.interval_spinbox)
        self.toolbar_layout.addStretch(1)
        self.toolbar_layout.addWidget(self.recognize_button)

        # 截图预览
        self.preview_card = HeaderCardWidget()
        self.preview_card.setTitle("截图预览")
        self.preview_card.setBorderRadius(8)
        self.preview_card.viewLayout.setContentsMargins(12, 8, 12, 12)
        self.preview_label = PreviewLabel()
        self._preview_vBoxLayout = QVBoxLayout()
        self._preview_vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self._preview_vBoxLayout.addWidget(self.preview_label, 1)
        self.preview_card.viewLayout.addLayout(self._preview_vBoxLayout)

        # 识别结果
        self.result_card = OcrResultCard()

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self.preview_card)
        self.splitter.addWidget(self.result_card)
        self.splitter.setSizes([280, 240])

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.addLayout(self.toolbar_layout)
        self.vBoxLayout.addWidget(self.splitter, 1)

        # 自动识别定时器
        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.start_recognition)

        self.recognition_finished.connect(self._recognition_finished_handle)
        self.recognition_failed.connect(self._recognition_failed_handle)

    def start_recognition(self) -> None:
        """开始一次识别（异步执行，避免阻塞界面）"""
        if self._busy:
            return
        self._busy = True
        self.recognize_button.setEnabled(False)
        Thread(target=self._recognition_task, name="ocr_detection", daemon=True).start()

    def _recognition_task(self) -> None:
        """截图并执行文字识别"""
        try:
            if window_manager.current is None:
                raise RuntimeError("未检测到游戏窗口，请先在「窗口管理」中检测并应用窗口")

            if not ocr_manager.is_initialized():
                ocr_manager.init()

            screenshot = ScreenShot()
            image = screenshot.get_image()
            if image is None:
                raise RuntimeError("截图失败，请检查游戏窗口状态")
            bgr = screenshot.get_bgr()
            if bgr is None:
                raise RuntimeError("截图数据为空")
            capture_ms = getattr(screenshot, "time_cost", 0.0)

            ocr_start = time.perf_counter()
            results: list[OcrData] = []
            for item in ocr_manager.detect(bgr):
                if not isinstance(item, dict):
                    continue
                if item.get("Score", 0.0) <= 0 or not item.get("Text", ""):
                    continue
                results.append(OcrData(item))

            # 按阅读顺序排序：先上后下，同一行内先左后右
            results.sort(key=lambda data: (data.y1, data.x1))
            ocr_ms = (time.perf_counter() - ocr_start) * 1000
            logger.debug(f"截图耗时 {capture_ms:.1f} ms，识别耗时 {ocr_ms:.1f} ms")
            self.recognition_finished.emit(image, results, capture_ms, ocr_ms)
        except Exception as e:
            self.recognition_failed.emit(str(e))

    def _recognition_finished_handle(
        self,
        image: Image,
        results: list[OcrData],
        capture_ms: float,
        ocr_ms: float,
    ) -> None:
        """识别完成，刷新预览与结果"""
        self._busy = False
        self.recognize_button.setEnabled(True)

        self._results = results
        self._pixmap = QPixmap.fromImage(ImageQt(image))
        # 截图尺寸、截图时间、截图耗时放在预览标题括号内
        self.preview_card.setTitle(
            f"截图预览（{image.size[0]} x {image.size[1]} - {time.strftime('%H:%M:%S')} - 耗时 {capture_ms:.1f} ms）"
        )

        self._ocr_ms = ocr_ms
        self._render_results()

    def _recognition_failed_handle(self, message: str) -> None:
        """识别失败，恢复按钮并提示"""
        self._busy = False
        self.recognize_button.setEnabled(True)
        self.auto_checkbox.setChecked(False)
        logger.error(f"文字识别失败: {message}")
        InfoBar.warning(
            title="识别失败",
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            duration=3000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self,
        )

    def _render_results(self) -> None:
        """刷新预览与表格"""
        if self._pixmap is None:
            return

        self.result_card.set_results(self._results, self._ocr_ms)
        self.preview_label.set_preview(self._pixmap, self._results)

    def _auto_checkbox_toggled_handle(self, checked: bool) -> None:
        """自动识别开关"""
        if checked:
            self.auto_timer.start(self.interval_spinbox.value() * 1000)
            self.start_recognition()
        else:
            self.auto_timer.stop()

    def _auto_interval_changed_handle(self, value: int) -> None:
        """自动识别间隔变化，运行中则立即按新间隔重新计时"""
        if self.auto_timer.isActive():
            self.auto_timer.start(value * 1000)
