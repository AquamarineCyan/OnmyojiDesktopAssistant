from PySide6.QtCore import QSize
from PySide6.QtWidgets import QHBoxLayout, QListWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, ListWidget, PushButton, SubtitleLabel


class EffectiveEntryAnalysisWidget(QWidget):
    """有效词条分析"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("EffectiveEntryAnalysisWidget")

        self.list_widget = ListWidget()
        self.list_widget.setFixedSize(400, 350)
        self.list_widget.setStyleSheet("border: 1px solid #d0d0d0; QListWidget::item { height: 24px; }")

        warning_label = BodyLabel("该功能将在2026年8月31日后弃用，请优先使用系统内置的有效词条分析功能。")
        warning_label.setStyleSheet("color: #dc3545;")

        self.button = PushButton("分析")
        self.button.setFixedWidth(80)

        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.setSpacing(10)
        self.hBoxLayout.addWidget(self.list_widget)
        self.hBoxLayout.addWidget(self.button)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.addWidget(SubtitleLabel("有效词条分析"))
        self.vBoxLayout.addWidget(BodyLabel("使用方法：式神录 -> 御魂方案 -> 新增御魂方案 -> 选择御魂"))
        self.vBoxLayout.addWidget(warning_label)
        self.vBoxLayout.addLayout(self.hBoxLayout)

        self.vBoxLayout.addStretch()

    def add_item(self, text: str):
        item = QListWidgetItem(text)
        base_size = item.sizeHint()
        item.setSizeHint(QSize(base_size.width(), 20))
        self.list_widget.addItem(item)

    def clear(self):
        self.list_widget.clear()
