from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QWidget

from ..utils.log import logger
from ..utils.update import get_local_update_record
from .update_record_ui import Ui_Form


class UpdateRecordWindow(QWidget):
    """更新记录窗口"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icon/buzhihuo.jpg"))

        self.ui.textBrowser.setOpenLinks(False)  # 禁用内部链接处理
        self.ui.textBrowser.anchorClicked.connect(self._open_external_browser)

        update_info = get_local_update_record()
        text = self.convert_to_markdown(update_info)
        self.ui.textBrowser.setMarkdown(text)
        logger.info(f"[update record]\n{text}")

    def _open_external_browser(self, url):
        QDesktopServices.openUrl(url)

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

    def convert_to_markdown(self, update_info):
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
            body = item["body"]
            # 替换Windows换行符为通用换行符
            body = body.replace("\r\n", "\n")
            # 移除行尾空白
            body = body.strip()

            # 对内容中的所有标题进行降级处理
            processed_body = self.downgrade_headings(body)

            # 添加到Markdown内容
            markdown_lines.append(processed_body)
            markdown_lines.append("")  # 空行分隔
            markdown_lines.append("---")  # 分隔线
            markdown_lines.append("")  # 空行

        # 移除最后多余的分隔线和空行
        return "\n".join(markdown_lines[:-2])
