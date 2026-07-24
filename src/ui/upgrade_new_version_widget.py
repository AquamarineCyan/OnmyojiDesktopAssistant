from threading import Thread

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QDialogButtonBox, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, ProgressBar, PushButton, TextBrowser

from ..utils.application import ICO_RESOURCE_PATH
from ..utils.log import logger
from ..utils.mysignal import global_ms as ms
from ..utils.upgrade import upgrade


class UpgradeNewVersionWidget(QWidget):
    """更新新版本"""

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(ICO_RESOURCE_PATH))
        self.setWindowTitle("更新新版本")
        self.resize(500, 400)

        self.text_browser = TextBrowser()
        self.text_browser.setOpenLinks(False)  # 禁用内部链接处理
        self.text_browser.anchorClicked.connect(self._open_external_browser)

        self.update_button = PushButton("下载更新")
        self.download_button = PushButton("仅下载")
        self.cancel_button = PushButton("忽略本次")

        self.progress_bar = ProgressBar()

        self.progress_percent_label = BodyLabel()
        self.download_info_label = BodyLabel()

        self.button_box = QDialogButtonBox()

        self.button_box.addButton(self.update_button, QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_box.addButton(self.download_button, QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_box.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)

        self.update_button.clicked.connect(self._update_button_handle)
        self.download_button.clicked.connect(self._download_button_handle)
        self.cancel_button.clicked.connect(self.close)

        ms.upgrade_new_version.progress_text_update.connect(self._download_info_update_handle)
        ms.upgrade_new_version.progressBar_update.connect(self._progress_update_handle)
        ms.upgrade_new_version.close_ui.connect(self.close)

        self.progress_hBoxLayout = QHBoxLayout()
        self.progress_hBoxLayout.addWidget(self.download_info_label, alignment=Qt.AlignmentFlag.AlignLeft)
        self.progress_hBoxLayout.addWidget(self.progress_percent_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.addWidget(self.text_browser)
        self.vBoxLayout.addWidget(self.progress_bar)
        self.vBoxLayout.addLayout(self.progress_hBoxLayout)
        self.vBoxLayout.addWidget(self.button_box)

        self.progress_bar.hide()
        text = self.convert_to_markdown(upgrade.new_version, upgrade.new_version_info)
        self.text_browser.setMarkdown(text)
        logger.info(f"[upgrade new version]\n{text}")

    def _open_external_browser(self, url):
        QDesktopServices.openUrl(url)

    def _download_info_update_handle(self, text: str):
        """更新文件进度信息

        Args:
            text (str): 文本内容
        """
        self.download_info_label.setText(text)

    def _progress_update_handle(self, value: int):
        """更新进度条

        Args:
            value (int): 百分比
        """
        self.progress_bar.setValue(value)
        self.progress_percent_label.setText(f"{value}%")

    def _progress_bar_show_handle(self):
        if self.progress_bar.isHidden():
            self.progress_bar.show()

    def _update_button_handle(self):
        self._progress_bar_show_handle()
        upgrade.ui_update_handle()

    def _download_button_handle(self):
        self._progress_bar_show_handle()
        Thread(target=upgrade.ui_download_handle, name="upgrade.ui_download_handle", daemon=True).start()

    def downgrade_headings(self, text: str):
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
        body: str = new_version_info
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
