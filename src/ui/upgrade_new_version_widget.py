from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QDialogButtonBox, QPushButton, QWidget

from ..utils.decorator import run_in_thread
from ..utils.log import logger
from ..utils.mysignal import global_ms as ms
from ..utils.upgrade import upgrade
from .upgrade_new_version import Ui_Form


class UpgradeNewVersionWidget(QWidget):
    """更新新版本"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icon/buzhihuo.jpg"))

        self.ui.textBrowser.setOpenLinks(False)  # 禁用内部链接处理
        self.ui.textBrowser.anchorClicked.connect(self._open_external_browser)

        button_update = QPushButton("下载更新", self)
        button_download = QPushButton("仅下载", self)
        button_cancel = QPushButton("忽略本次", self)

        self.ui.buttonBox.addButton(button_update, QDialogButtonBox.ButtonRole.AcceptRole)
        self.ui.buttonBox.addButton(button_download, QDialogButtonBox.ButtonRole.AcceptRole)
        self.ui.buttonBox.addButton(button_cancel, QDialogButtonBox.ButtonRole.RejectRole)
        self.ui.progressBar.hide()

        button_update.clicked.connect(self.button_update_clicked_func)
        button_download.clicked.connect(self._button_download_clicked_handle)
        button_cancel.clicked.connect(self.close)

        ms.upgrade_new_version.progress_text_update.connect(self._update_progress_text_handle)
        ms.upgrade_new_version.progressBar_update.connect(self._update_progressBar_handle)
        ms.upgrade_new_version.close_ui.connect(self.close)

        text = self.convert_to_markdown(upgrade.new_version, upgrade.new_version_info)
        self.ui.textBrowser.setMarkdown(text)
        logger.info(f"[upgrade new version]\n{text}")

    def _open_external_browser(self, url):
        QDesktopServices.openUrl(url)

    def _update_progress_text_handle(self, text: str):
        """更新文件进度信息

        参数:
            text (str): 文本内容
        """
        self.ui.label.setText(text)

    def _update_progressBar_handle(self, value: int):
        """更新进度条

        参数:
            value (int): 百分比
        """
        self.ui.progressBar.setValue(value)

    def _show_progressBar_handle(self):
        if self.ui.progressBar.isHidden():
            self.ui.progressBar.show()

    def button_update_clicked_func(self):
        self._show_progressBar_handle()
        upgrade.ui_update_func()

    @run_in_thread
    def _button_download_clicked_handle(self):
        self._show_progressBar_handle()
        # upgrade.ui_download_func()
        url = "https://dldir1v6.qq.com/qqfile/qq/QQNT/Windows/QQ_9.9.20_250626_x64_01.exe"
        upgrade.file = url.split("/")[-1]
        upgrade.download_upgrade_zip(url)

    def downgrade_headings(self, text):
        """
        将Markdown文本中的所有标题降一级（如# 标题 → ## 标题）
        最多处理到六级标题，超过六级保持不变
        """
        lines = text.split("\n")
        processed_lines = []
        for line in lines:
            stripped = line.lstrip("#")
            # 计算原标题级别
            level = len(line) - len(stripped)

            if level > 0 and stripped.startswith(" "):
                # 降级处理（但不超过6级）
                new_level = min(level + 1, 6)
                processed_lines.append("#" * new_level + stripped)
            else:
                processed_lines.append(line)
        return "\n".join(processed_lines)

    def convert_to_markdown(self, new_version, new_version_info):
        markdown_lines = []

        # 添加版本标题
        markdown_lines.append(f"# {new_version}")
        markdown_lines.append("")  # 空行

        # 处理并添加更新内容
        body = new_version_info
        # 替换Windows换行符为通用换行符
        body = body.replace("\r\n", "\n")
        # 移除行尾空白
        body = body.strip()

        # 对内容中的所有标题进行降级处理
        processed_body = self.downgrade_headings(body)

        # 添加到Markdown内容
        markdown_lines.append(processed_body)
        markdown_lines.append("")  # 空行分隔

        return "\n".join(markdown_lines)
