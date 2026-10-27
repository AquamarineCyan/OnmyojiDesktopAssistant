from pathlib import Path

from PIL import Image, ImageQt
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QResizeEvent
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CaptionLabel

from ..utils.log import logger
from ..utils.signals import signal_manager


class DebugPreviewWindow(QWidget):
    """匹配结果预览窗口（非阻塞，同一窗口反复刷新）"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("图像匹配结果预览")
        self.resize(800, 600)

        self._pixmap: QPixmap | None = None
        self._activated = False  # 只在首次显示时抢焦点，后续刷新不打断操作

        self.title_label = BodyLabel(self)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(1, 1)
        self.info_label = CaptionLabel(self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(12, 12, 12, 12)
        self.vBoxLayout.setSpacing(6)
        self.vBoxLayout.addWidget(self.title_label)
        self.vBoxLayout.addWidget(self.image_label, 1)
        self.vBoxLayout.addWidget(self.info_label)

    def show_image(self, image: Image.Image, title: str = "") -> None:
        """显示/刷新预览

        Args:
            image (Image.Image): 待预览图像（RGB，已画出匹配框）
            title (str): 标题，一般为素材名称
        """
        self._pixmap = QPixmap.fromImage(ImageQt.ImageQt(image))
        if title:
            self.title_label.setText(title)
        self.info_label.setText(f"{image.width} x {image.height}")
        self.show()
        if not self._activated:
            self._activated = True
            self.raise_()
            self.activateWindow()
        self._update_pixmap()

    def _update_pixmap(self) -> None:
        """按窗口大小等比缩放预览图"""
        if self._pixmap is None:
            return
        self.image_label.setPixmap(
            self._pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._update_pixmap()


def show_debug_preview(image: Image.Image, title: str = "图像匹配结果", save_path: str | Path | None = None) -> None:
    """请求显示匹配结果截图

    Args:
        image (Image.Image): 待预览图像（RGB，已画出匹配框）
        title (str): 标题
        save_path (str | Path | None): 调试截图落盘路径
    """
    if save_path is not None:
        image.save(str(save_path))
        logger.info(f"[DEBUG] 调试截图已保存: {save_path}")

    if QApplication.instance() is not None:
        # 由主窗口在主线程接收并显示，可跨线程安全调用
        signal_manager.main.debug_preview_requested.emit(image, title)
