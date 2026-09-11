from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import TextBrowser

from ..utils.application import ICO_RESOURCE_PATH
from ..utils.log import logger
from ..utils.markdown import autolink_urls, downgrade_headings
from ..utils.update import update_manager


class UpdateRecordWindow(QWidget):
    """更新记录窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(ICO_RESOURCE_PATH))
        self.setWindowTitle("更新记录")
        self.resize(600, 500)

        self.text_browser = TextBrowser(self)
        self.text_browser.setOpenLinks(False)  # 禁用内部链接处理
        self.text_browser.anchorClicked.connect(QDesktopServices.openUrl)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.text_browser)

        update_info = update_manager.get_local_update_record()
        text = self.convert_to_markdown(update_info)
        self.text_browser.setMarkdown(text)
        logger.info(f"[update record]\n{text}")

    def convert_to_markdown(self, update_info: list[dict]):
        # 按版本号降序排序（最新版本在前）
        sorted_info = sorted(
            update_info,
            key=lambda x: tuple(map(int, x["version"].split("."))),
            reverse=True,
        )

        markdown_lines = []
        for item in sorted_info:
            # 添加版本标题
            markdown_lines.append(f"# {item['version']}")
            markdown_lines.append("")  # 空行

            # 处理并添加更新内容
            body: str = item["body"]
            # 替换Windows换行符为通用换行符
            body = body.replace("\r\n", "\n")
            # 移除行尾空白
            body = body.strip()
            # 将裸 URL 转为超链接，与 GitHub 渲染一致
            body = autolink_urls(body)

            # 对内容中的所有标题进行降级处理
            processed_body = downgrade_headings(body)

            # 添加到Markdown内容
            markdown_lines.append(processed_body)
            markdown_lines.append("")  # 空行分隔
            markdown_lines.append("---")  # 分隔线
            markdown_lines.append("")  # 空行

        # 移除最后多余的分隔线和空行
        return "\n".join(markdown_lines[:-2])
