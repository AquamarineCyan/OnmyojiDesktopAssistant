from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CaptionLabel, ComboBox, PushButton

from ..utils.mysignal import global_ms as ms


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

        self.apply_button = PushButton("应用")
        self.apply_button.setFixedWidth(80)
        self.apply_button.setDisabled(True)

        self.preview_image = QLabel(self)
        self.preview_image.setFixedSize(400, 300)

        self.capture_size_label = CaptionLabel(self)
        self.capture_time_label = CaptionLabel(self)

        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(10)
        self.hBoxLayout.addWidget(self.comboBox)
        self.hBoxLayout.addWidget(self.preview_button)
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

        ms.main.window_update.connect(self.update_window_status)
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
