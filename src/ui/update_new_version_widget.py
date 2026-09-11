from threading import Thread

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QDialogButtonBox, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    ComboBox,
    ProgressBar,
    PushButton,
    SingleDirectionScrollArea,
    TextBrowser,
    TransparentPushButton,
)

from ..utils.application import ICO_RESOURCE_PATH, VERSION
from ..utils.config import config, default_config
from ..utils.log import logger
from ..utils.markdown import autolink_urls, downgrade_headings
from ..utils.mysignal import global_ms as ms
from ..utils.update import compare_versions, update_manager


def _process_body(body: str) -> str:
    """处理更新内容：统一换行符、去空白、裸链接化、标题降级"""
    # 替换Windows换行符为通用换行符
    body = body.replace("\r\n", "\n")
    # 移除行尾空白
    body = body.strip()
    # 将裸 URL 转为超链接，与 GitHub 渲染一致
    body = autolink_urls(body)
    # 对内容中的所有标题进行降级处理
    return downgrade_headings(body)


def _create_browser() -> TextBrowser:
    """创建自适应高度、无内部滚动条的只读文本浏览器"""
    browser = TextBrowser()
    browser.setOpenLinks(False)  # 禁用内部链接处理
    browser.anchorClicked.connect(QDesktopServices.openUrl)
    browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def _fit_height(_size):
        """根据文档内容高度自适应控件高度，避免出现嵌套滚动条"""
        height = int(browser.document().documentLayout().documentSize().height())
        height += browser.frameWidth() * 2
        if browser.height() != height:
            browser.setFixedHeight(height)

    browser.document().documentLayout().documentSizeChanged.connect(_fit_height)
    return browser


class CollapsibleBox(CardWidget):
    """可展开/收起的版本更新卡片"""

    def __init__(self, version: str, body: str, parent=None):
        super().__init__(parent)
        self._version = version
        self._expanded = False

        self.toggle_button = TransparentPushButton(f"▶ 版本 {version} 更新内容")
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self._on_toggle)

        self.body_browser = _create_browser()
        self.body_browser.setMarkdown(_process_body(body))
        self.body_browser.hide()

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(12, 8, 12, 8)
        self.vBoxLayout.setSpacing(4)
        self.vBoxLayout.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(self.body_browser)

    def _on_toggle(self, checked: bool):
        """切换卡片展开/收起状态"""
        self._expanded = checked
        arrow = "▼" if checked else "▶"
        self.toggle_button.setText(f"{arrow} 版本 {self._version} 更新内容")
        self.body_browser.setVisible(checked)


class UpdateNewVersionWidget(QWidget):
    """更新新版本"""

    _SHOWN_VERSION_LIMIT = 5
    """最多展示的版本数量上限"""

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(ICO_RESOURCE_PATH))
        self.setWindowTitle("更新新版本")
        self.resize(600, 500)

        self.update_button = PushButton("下载更新")
        self.download_button = PushButton("仅下载")
        self.cancel_button = PushButton("忽略本次")

        self.download_route_combobox = ComboBox()
        self.download_route_combobox.addItems(default_config.update_download)
        self.download_route_combobox.setCurrentText(config.user.update_download)
        self.download_route_combobox.setToolTip("Mirror酱线路需先在设置中填写CDK")
        self.download_route_combobox.currentIndexChanged.connect(self._route_changed_handle)

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

        ms.update_new_version.progress_text_update.connect(self._download_info_update_handle)
        ms.update_new_version.progressBar_update.connect(self._progress_update_handle)
        ms.update_new_version.close_ui.connect(self.close)

        # 主内容区：最新版本默认展开 + 其余版本折叠卡片
        _markdown = self._build_shown_markdown()
        self.text_browser = _create_browser()
        self.text_browser.setMarkdown(_markdown)
        logger.info(f"[update new version]\n{_markdown}")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.content_layout.addWidget(self.text_browser)
        for item in self._get_collapsed_versions():
            self.content_layout.addWidget(CollapsibleBox(item["version"], item["body"]))

        self.scroll_area = SingleDirectionScrollArea()
        self.scroll_area.setWidgetResizable(True)  # 使滚动区域可调整大小以适应内容
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.content_widget)

        self.progress_hBoxLayout = QHBoxLayout()
        self.progress_hBoxLayout.addWidget(self.download_info_label, alignment=Qt.AlignmentFlag.AlignLeft)
        self.progress_hBoxLayout.addWidget(self.progress_percent_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.route_hBoxLayout = QHBoxLayout()
        self.route_hBoxLayout.addWidget(BodyLabel("下载线路:"), alignment=Qt.AlignmentFlag.AlignLeft)
        self.route_hBoxLayout.addWidget(self.download_route_combobox, alignment=Qt.AlignmentFlag.AlignLeft)
        self.route_hBoxLayout.addStretch(1)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.addWidget(self.scroll_area)
        self.vBoxLayout.addLayout(self.route_hBoxLayout)
        self.vBoxLayout.addWidget(self.progress_bar)
        self.vBoxLayout.addLayout(self.progress_hBoxLayout)
        self.vBoxLayout.addWidget(self.button_box)

        self.progress_bar.hide()

    def _route_changed_handle(self):
        text = self.download_route_combobox.currentText()
        if text != config.user.update_download:
            config.update("update_download", text)

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
        update_manager.ui_update_handle()

    def _download_button_handle(self):
        self._progress_bar_show_handle()
        Thread(target=update_manager.ui_download_handle, name="update_manager.ui_download_handle", daemon=True).start()

    def _split_versions(self, version_history: list[dict]) -> tuple[list[dict], list[dict]]:
        """拆分默认展示与折叠的版本

        仅保留高于当前版本且不超过数量上限的发布；
        最新版本默认展开，其余版本默认折叠。

        返回:
            (默认展示的版本列表, 需要折叠的版本列表)
        """
        display_versions = [item for item in version_history if compare_versions(item["version"], VERSION)][
            : self._SHOWN_VERSION_LIMIT
        ]
        return display_versions[:1], display_versions[1:]

    def _get_collapsed_versions(self) -> list[dict]:
        """获取需要折叠展示的版本列表"""
        if not update_manager.version_history:
            return []
        _, collapsed_versions = self._split_versions(update_manager.version_history)
        return collapsed_versions

    def _build_shown_markdown(self) -> str:
        """构建默认展开的版本更新内容（最新版本）"""
        if not update_manager.version_history:
            version_history = [{"version": update_manager.new_version, "body": update_manager.new_version_info}]
        else:
            version_history = update_manager.version_history

        shown_versions, _ = self._split_versions(version_history)

        markdown_lines = []
        for index, item in enumerate(shown_versions):
            # 最新版本用一级标题，其余默认展示的版本用二级标题
            heading = "#" if index == 0 else "##"
            markdown_lines.append(f"{heading} {item['version']}")
            markdown_lines.append("")  # 空行

            # 处理并添加更新内容
            markdown_lines.append(_process_body(item["body"]))
            markdown_lines.append("")  # 空行分隔
            if index < len(shown_versions) - 1:
                markdown_lines.append("---")  # 分隔线
                markdown_lines.append("")  # 空行

        return "\n".join(markdown_lines)
