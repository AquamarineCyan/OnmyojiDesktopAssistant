from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import CheckBox, PushButton, TextBrowser

from ..utils.announcement import mark_as_read
from ..utils.application import ICO_RESOURCE_PATH
from ..utils.markdown import autolink_urls, downgrade_headings

MAX_ANNOUNCEMENTS: int = 5
"""最多展示的公告数（即最大页数）"""


class AnnouncementWindow(QWidget):
    """公告窗口"""

    def __init__(self, announcements: list[dict]):
        super().__init__()
        # 最新公告在前，最多展示 MAX_ANNOUNCEMENTS 条
        self.announcements = sorted(announcements, key=lambda x: x["id"], reverse=True)[:MAX_ANNOUNCEMENTS]
        self.page: int = 0
        self.total_pages: int = max(1, len(self.announcements))

        self.setWindowIcon(QIcon(ICO_RESOURCE_PATH))
        self.setWindowTitle("公告")
        self.resize(600, 500)

        self.text_browser = TextBrowser(self)
        self.text_browser.setOpenLinks(False)  # 禁用内部链接处理
        self.text_browser.anchorClicked.connect(QDesktopServices.openUrl)

        # 翻页控件
        self.prev_button = PushButton("上一页")
        self.next_button = PushButton("下一页")
        self.page_label = QLabel()

        self.pager_layout = QHBoxLayout()
        self.pager_layout.setContentsMargins(10, 5, 10, 5)
        self.pager_layout.addWidget(self.prev_button)
        self.pager_layout.addStretch()
        self.pager_layout.addWidget(self.page_label)
        self.pager_layout.addStretch()
        self.pager_layout.addWidget(self.next_button)

        # 已读确认控件（仅最后一页显示）
        self.read_checkbox = CheckBox("我已经阅读上述公告")
        self.confirm_button = PushButton("确认")
        self.confirm_button.setEnabled(False)

        self.confirm_layout = QHBoxLayout()
        self.confirm_layout.setContentsMargins(10, 5, 10, 5)
        self.confirm_layout.addWidget(self.read_checkbox)
        self.confirm_layout.addStretch()
        self.confirm_layout.addWidget(self.confirm_button)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.text_browser, 1)
        self.vBoxLayout.addLayout(self.pager_layout)
        self.vBoxLayout.addLayout(self.confirm_layout)

        self.prev_button.clicked.connect(self._prev_page)
        self.next_button.clicked.connect(self._next_page)
        self.read_checkbox.toggled.connect(self.confirm_button.setEnabled)
        self.confirm_button.clicked.connect(self._confirm_read)

        self._update_page()

    def _prev_page(self):
        """上一页"""
        if self.page > 0:
            self.page -= 1
            self._update_page()

    def _next_page(self):
        """下一页"""
        if self.page < self.total_pages - 1:
            self.page += 1
            self._update_page()

    def _update_page(self):
        """更新当前页显示"""
        start = self.page
        end = self.page + 1
        page_items = self.announcements[start:end]

        self.text_browser.setMarkdown(self._page_to_markdown(page_items))
        self.page_label.setText(f"第 {self.page + 1}/{self.total_pages} 页")
        self.prev_button.setEnabled(self.page > 0)
        self.next_button.setEnabled(self.page < self.total_pages - 1)

        # 已读确认仅最后一页显示
        is_last_page = self.page == self.total_pages - 1
        self.read_checkbox.setVisible(is_last_page)
        self.confirm_button.setVisible(is_last_page)
        if not is_last_page:
            self.read_checkbox.setChecked(False)
            self.confirm_button.setEnabled(False)

    @staticmethod
    def format_id(announcement_id: int) -> str:
        """将整数日期 id 格式化为日期字符串"""
        return f"{announcement_id // 10000}-{announcement_id % 10000 // 100:02d}-{announcement_id % 100:02d}"

    def _page_to_markdown(self, page_items: list[dict]) -> str:
        """将一页公告转换为 Markdown 文本"""
        markdown_lines = []
        for item in page_items:
            # id 即标题，使用一级标题渲染
            markdown_lines.append(f"# {self.format_id(item['id'])}")
            markdown_lines.append("")

            body: str = item["content"]
            body = body.replace("\r\n", "\n")
            body = body.strip()
            body = autolink_urls(body)
            body = downgrade_headings(body)

            markdown_lines.append(body)
            markdown_lines.append("")
            markdown_lines.append("---")
            markdown_lines.append("")

        return "\n".join(markdown_lines[:-2])

    def _confirm_read(self):
        """确认已读：更新本地已读 id 并关闭窗口"""
        if self.announcements:
            # 已按最新在前排序，首个即最新 id
            mark_as_read(self.announcements[0]["id"])
        self.close()
