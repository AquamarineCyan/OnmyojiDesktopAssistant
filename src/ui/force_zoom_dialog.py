from PySide6.QtCore import Qt
from qfluentwidgets import CheckBox, Dialog

from ..utils.config import config


class ForceZoomDialog(Dialog):
    """游戏窗口大小不匹配时，强制缩放提示弹窗"""

    def __init__(self, parent=None):
        super().__init__(
            "游戏窗口大小不匹配",
            "是否强制缩放？\n"
            "如不缩放，请自行将窗口调整至 1136×640，\n"
            "或参考 帮助文档 在 data/myresource 文件夹中添加对应素材。",
            parent,
        )

        self.yesButton.setText("确定")
        self.cancelButton.setText("取消")

        # 按钮宽度自适应
        self.buttonLayout.setStretch(self.buttonLayout.indexOf(self.yesButton), 0)
        self.buttonLayout.setStretch(self.buttonLayout.indexOf(self.cancelButton), 0)

        self.remember_checkbox = CheckBox("不再提醒", self.buttonGroup)
        self.remember_checkbox.setChecked(config.user.remember_force_zoom_choice)
        self.buttonLayout.insertWidget(0, self.remember_checkbox, 0, Qt.AlignVCenter)

    def _save_choice(self, accepted: bool):
        """保存“不再提醒”选择"""
        if self.remember_checkbox.isChecked():
            config.update("remember_force_zoom_choice", True)
            config.update("force_zoom_accepted", accepted)

    def accept(self):
        """用户选择强制缩放"""
        self._save_choice(True)
        super().accept()

    def reject(self):
        """用户拒绝强制缩放"""
        self._save_choice(False)
        super().reject()
