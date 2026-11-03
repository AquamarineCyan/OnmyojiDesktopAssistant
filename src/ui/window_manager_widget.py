from PySide6.QtCore import Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    ComboBox,
    LineEdit,
    MessageBoxBase,
    PushButton,
    SubtitleLabel,
)

from ..utils.signals import signal_manager
from ..utils.window import STANDARD_CLIENT_HEIGHT, STANDARD_CLIENT_WIDTH


class ResizeWindowDialog(MessageBoxBase):
    """自定义窗口宽高的缩放弹窗"""

    def __init__(self, parent=None, window_label: str = "", width: int = 0, height: int = 0):
        """初始化缩放弹窗

        Args:
            parent: 父级窗口
            window_label: 当前选择窗口的显示文本
            width: 当前客户区宽度，不足以正数时使用默认值
            height: 当前客户区高度，不足以正数时使用默认值
        """
        super().__init__(parent)
        self.viewLayout.setSpacing(20)
        title = "缩放游戏窗口"
        self.titleLabel = SubtitleLabel(title, self)
        self.tipLabel = BodyLabel(f"请输入目标宽高（默认 {STANDARD_CLIENT_WIDTH}x{STANDARD_CLIENT_HEIGHT}）", self)
        self.line_edit_width = LineEdit(self)
        self.line_edit_height = LineEdit(self)
        self.line_edit_width.setText(str(width if width > 0 else STANDARD_CLIENT_WIDTH))
        self.line_edit_height.setText(str(height if height > 0 else STANDARD_CLIENT_HEIGHT))
        self.line_edit_width.setPlaceholderText(str(STANDARD_CLIENT_WIDTH))
        self.line_edit_height.setPlaceholderText(str(STANDARD_CLIENT_HEIGHT))
        self.widthLabel = BodyLabel("宽度", self)
        self.heightLabel = BodyLabel("高度", self)
        self.separatorLabel = BodyLabel("×", self)

        self.windowLabel = BodyLabel(f"选定窗口：{window_label}", self)
        self.warningLabel = BodyLabel("请输入正确的宽高", self)
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))
        self.warningLabel.hide()

        # 宽高输入框横排：宽度 [输入框] × 高度 [输入框]
        self.sizeLayout = QHBoxLayout()
        self.sizeLayout.setContentsMargins(0, 0, 0, 0)
        self.sizeLayout.setSpacing(8)
        self.sizeLayout.addWidget(self.widthLabel)
        self.sizeLayout.addWidget(self.line_edit_width, 1)
        self.sizeLayout.addWidget(self.separatorLabel)
        self.sizeLayout.addWidget(self.heightLabel)
        self.sizeLayout.addWidget(self.line_edit_height, 1)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.windowLabel)
        self.viewLayout.addWidget(self.tipLabel)
        self.viewLayout.addLayout(self.sizeLayout)
        self.viewLayout.addWidget(self.warningLabel)

        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")
        self.widget.setMinimumWidth(350)

    def validate(self) -> bool:
        """校验输入是否为正整数；宽高都为空时按默认值处理"""
        width_text = self.line_edit_width.text().strip()
        height_text = self.line_edit_height.text().strip()
        if not width_text and not height_text:
            isValid = True
        else:
            isValid = width_text.isdigit() and height_text.isdigit()
            if isValid:
                isValid = int(width_text) > 0 and int(height_text) > 0
        self.warningLabel.setHidden(isValid)
        self.line_edit_width.setError(not isValid)
        self.line_edit_height.setError(not isValid)
        return isValid

    def values(self) -> tuple[int, int]:
        """返回宽高输入值；空值使用基准客户区尺寸"""
        width = int(self.line_edit_width.text().strip() or STANDARD_CLIENT_WIDTH)
        height = int(self.line_edit_height.text().strip() or STANDARD_CLIENT_HEIGHT)
        return width, height


class WindowManagerWidget(QWidget):
    """窗口管理"""

    _window_count_text = "检测到的游戏窗口"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("WindowManagerWidget")

        self.screen_resolution_label = BodyLabel(self)
        self.current_window_label = BodyLabel(self)
        self.window_count_label = BodyLabel()

        self.comboBox = ComboBox(self)
        self.comboBox.setDisabled(True)

        self.preview_button = PushButton("预览")
        self.preview_button.setFixedWidth(80)
        self.preview_button.setDisabled(True)

        self.resize_button = PushButton("缩放")
        self.resize_button.setFixedWidth(80)
        self.resize_button.setDisabled(True)

        self.apply_button = PushButton("应用")
        self.apply_button.setFixedWidth(80)
        self.apply_button.setDisabled(True)

        self.preview_image = QLabel(self)
        self.preview_image.setFixedSize(400, 300)

        self.capture_size_label = BodyLabel(self)
        self.capture_time_label = BodyLabel(self)

        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(10)
        self.hBoxLayout.addWidget(self.comboBox)
        self.hBoxLayout.addWidget(self.preview_button)
        self.hBoxLayout.addWidget(self.resize_button)
        self.hBoxLayout.addWidget(self.apply_button)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.addWidget(self.screen_resolution_label)
        self.vBoxLayout.addWidget(self.current_window_label)
        self.vBoxLayout.addWidget(self.window_count_label)
        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.vBoxLayout.addWidget(self.preview_image)
        self.vBoxLayout.addWidget(self.capture_size_label)
        self.vBoxLayout.addWidget(self.capture_time_label)

        self.vBoxLayout.addStretch()

        signal_manager.main.window_status_changed.connect(self.update_window_status)
        self.update_window_status(0, "")

    @Slot(int, str)
    def update_window_status(self, number: int, current_text: str = ""):
        """更新窗口状态显示

        Args:
            number (int): 窗口数量
            current_text (str): 当前选中的窗口
        """
        if number > 0:
            self.window_count_label.setText(f"{self._window_count_text}：({number}个)")
        else:
            self.window_count_label.setText(f"{self._window_count_text}：(无)")
        if current_text:
            self.current_window_label.setText(f"当前窗口：{current_text}")
        else:
            self.current_window_label.clear()

    def update_capture_size_label(self, size: str):
        """更新捕获尺寸标签

        Args:
            size (str): 捕获尺寸
        """
        self.capture_size_label.setText(f"捕获尺寸：{size}")

    def update_capture_time_label(self, time: str):
        """更新捕获时间标签

        Args:
            time (str): 捕获时间
        """
        self.capture_time_label.setText(f"捕获时间：{time}")

    def update_screen_resolution(self, width: int, height: int):
        """更新屏幕分辨率标签

        Args:
            width (int): 屏幕宽度
            height (int): 屏幕高度
        """
        self.screen_resolution_label.setText(f"屏幕分辨率：{width}x{height}")
