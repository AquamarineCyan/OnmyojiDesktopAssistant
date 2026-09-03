import subprocess

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from qfluentwidgets import CheckBox, MessageBox, PushButton

from ..utils.application import APP_NAME, HELP_DOC_LINK, LOG_DIR_PATH
from ..utils.log import logger


class FirstUseMessageBox(MessageBox):
    """首次使用提示弹窗"""

    def __init__(self, parent=None):
        super().__init__(
            "温馨提示",
            "首次使用，建议先阅读帮助文档。未正确使用所产生的一切后果自负，保持您的肝度与日常无较大差距，本程序目前仅兼容桌面版。MuMu专版教程在帮助文档中。\n\n本软件完全免费，严禁私自倒卖，收费，用于任何商业用途。\n\n反馈问题，请附上日志文件。",
            parent,
        )

        self.log_btn = PushButton("打开日志文件夹")
        self.log_btn.clicked.connect(self._open_log_folder)
        self.help_btn = PushButton("帮助文档")
        self.help_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(HELP_DOC_LINK)))
        self.exit_btn = PushButton("退出")
        self.exit_btn.setStyleSheet(
            "PushButton { background-color: #D32F2F; color: white; border: none; border-radius: 5px; padding: 5px 12px; }"
            "PushButton:hover { background-color: #E53935; }"
            "PushButton:pressed { background-color: #B71C1C; }"
        )
        self.exit_btn.clicked.connect(self._exit_app)
        # 先隐藏取消按钮：其内部会在布局最前插入 stretch，必须先于复选框插入执行
        self.hideCancelButton()

        # 复选框：勾选后"确定"按钮才可点击
        self.check_box = CheckBox("我已知晓上述内容")
        self.buttonLayout.insertWidget(0, self.check_box)
        self.buttonLayout.removeWidget(self.yesButton)

        self.buttonLayout.addWidget(self.log_btn)
        self.buttonLayout.addWidget(self.help_btn)
        self.buttonLayout.addWidget(self.yesButton)
        self.buttonLayout.addWidget(self.exit_btn)
        self.yesButton.setText("确定")
        self.yesButton.setEnabled(False)
        self.check_box.stateChanged.connect(
            lambda state: self.yesButton.setEnabled(int(state) == Qt.CheckState.Checked.value)
        )

        self.yesButton.clicked.connect(lambda: logger.info("用户确认温馨提示，关闭首次启动提示弹窗"))

    def _open_log_folder(self):
        """打开日志文件夹并选中当前日志文件（Windows 资源管理器）"""
        log_file = LOG_DIR_PATH / f"{APP_NAME}.log"
        if log_file.is_file():
            # 打开文件夹并高亮选中当前使用的日志文件
            subprocess.Popen(f'explorer.exe /select,"{log_file}"')
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(LOG_DIR_PATH)))

    def _exit_app(self):
        """退出程序"""
        logger.info("用户选择退出程序（温馨提示）")
        self.close()
        window = self.window()
        if window is not None and window is not self:
            window.close()
