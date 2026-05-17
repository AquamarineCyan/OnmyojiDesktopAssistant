from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CaptionLabel, ComboBox, PushButton


class WindowManagerWidget(QWidget):
    """窗口管理"""

    _label = "检测到游戏窗口："

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("WindowManagerWidget")

        self.label = BodyLabel()

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
        self.vBoxLayout.addWidget(self.label)
        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.vBoxLayout.addWidget(self.preview_image)
        self.vBoxLayout.addWidget(self.capture_size_label)
        self.vBoxLayout.addWidget(self.capture_time_label)

        self.vBoxLayout.addStretch()

        self.update_label(0)

    def update_label(self, number: int):
        """更新标题里的窗口数量

        Args:
            number (int): 窗口数量
        """
        if number > 0:
            self.label.setText(f"{self._label[:-1]}({number}个){self._label[-1]}")
        else:
            self.label.setText(f"{self._label[:-1]}(无){self._label[-1]}")

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
