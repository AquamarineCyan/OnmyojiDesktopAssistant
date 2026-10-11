from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from qfluentwidgets import MessageBox, PushButton

from ..utils.application import HELP_DOC_LINK


class MumuEmulatorMessageBox(MessageBox):
    """启用 MuMu 模拟器支持前的提示弹窗"""

    def __init__(self, parent=None):
        super().__init__(
            "温馨提示",
            "模拟器内的阴阳师版本需要从模拟器的游戏中心下载。\n自行安装APK文件的方式会导致ESC退出方式不可用。",
            parent,
        )

        self.help_btn = PushButton("帮助文档")
        self.help_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(HELP_DOC_LINK)))

        # 文档按钮固定最左，确定/取消靠右（按钮宽度自适应）
        self.buttonLayout.setStretch(self.buttonLayout.indexOf(self.yesButton), 0)
        self.buttonLayout.setStretch(self.buttonLayout.indexOf(self.cancelButton), 0)
        self.buttonLayout.insertWidget(0, self.help_btn, 0, Qt.AlignVCenter)
        self.buttonLayout.insertStretch(1, 1)

        self.yesButton.setText("确定")
        self.cancelButton.setText("取消")
