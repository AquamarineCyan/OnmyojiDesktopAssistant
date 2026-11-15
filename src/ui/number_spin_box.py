from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSpinBox
from qfluentwidgets import CompactSpinBox
from qfluentwidgets.components.widgets.spin_box import CompactSpinButton


class SplitStepButton(CompactSpinButton):
    """右侧步进按钮：上半区加一、下半区减一，不再弹出浮层"""

    def __init__(self, spin_box: "CustomCompactSpinBox"):
        super().__init__(spin_box)
        self._spin_box = spin_box
        self._step_up: bool = True
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.clicked.connect(self._step)

    def mousePressEvent(self, event):
        # 记录本次按下的是上半区还是下半区，按住自动重复时沿用同一方向
        self._step_up = event.position().y() < self.height() / 2
        super().mousePressEvent(event)

    def _step(self):
        if self._step_up:
            self._spin_box.stepUp()
        else:
            self._spin_box.stepDown()


class CustomCompactSpinBox(CompactSpinBox):
    """CompactSpinBox 的单次点击版本

    外观与 CompactSpinBox 一致，但点击右侧箭头上半区直接加一、
    下半区直接减一，并跳过聚焦时自动弹出的上下按钮浮层。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hBoxLayout.removeWidget(self.compactSpinButton)
        self.compactSpinButton.deleteLater()
        self.compactSpinButton = SplitStepButton(self)
        self.compactSpinButton.setAutoRepeat(True)
        self.hBoxLayout.addWidget(self.compactSpinButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def focusInEvent(self, event):
        # 跳过 CompactSpinBoxBase 的自动浮层，保留正常输入焦点
        QSpinBox.focusInEvent(self, event)
