from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    CardWidget,
    ComboBox,
    ExpandGroupSettingCard,
    FluentIcon,
    HyperlinkLabel,
    IconWidget,
    IndicatorPosition,
    PushButton,
    ScrollArea,
    SubtitleLabel,
    SwitchButton,
)

from ..utils.application import (
    HELP_DOC_LINK,
    HOME_PAGE_LINK,
    QQ_GROUP_LINK,
)
from ..utils.config import config, default_config


class AppCard(CardWidget):
    def __init__(self, icon, title, content, parent=None):
        super().__init__(parent)
        self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(title, self)
        self.contentLabel = CaptionLabel(content, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(73)
        self.iconWidget.setFixedSize(16, 16)
        self.contentLabel.setTextColor("#606060", "#d2d2d2")

        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.iconWidget)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.addStretch(1)


class SettingLanguageCard(AppCard):
    """设置项-游戏服务器"""

    def __init__(self, parent=None):
        super().__init__(FluentIcon.LANGUAGE, "游戏服务器", "重启后生效", parent)

        self.combobox = ComboBox()
        self.combobox.addItems(default_config.game_language)
        self.combobox.setFixedWidth(120)
        self.combobox.currentIndexChanged.connect(self._config_update)

        self.hBoxLayout.addWidget(self.combobox)

    def _config_update(self):
        text = self.combobox.currentText()
        if text != config.user.game_language:
            config.update("game_language", text)


class SettingXuanshangfengyinCard(AppCard):
    """设置项-悬赏封印"""

    def __init__(self, parent=None):
        super().__init__(FluentIcon.GAME, "悬赏封印", "长时间运行时可切换至忽略状态", parent)

        self.combobox = ComboBox()
        self.combobox.addItems(default_config.xuanshangfengyin)
        self.combobox.setFixedWidth(120)
        self.combobox.currentIndexChanged.connect(self._config_update)

        self.hBoxLayout.addWidget(self.combobox)

    def _config_update(self):
        text = self.combobox.currentText()
        if text != config.user.xuanshangfengyin:
            config.update("xuanshangfengyin", text)


class SettingRememberLastChoiceCard(AppCard):
    """设置项-记住上次选择的功能"""

    def __init__(self, parent=None):
        super().__init__(FluentIcon.APPLICATION, "记住上次选择的功能", "每次启动软件后自动选择上次选择的功能", parent)

        self.switch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)  # 文本在左侧
        self.switch.setOnText("启用")
        self.switch.setOffText("禁用")
        self.switch.setChecked(default_config.remember_last_choice)
        self.switch.checkedChanged.connect(self._config_update)

        self.hBoxLayout.addWidget(self.switch)

    def _config_update(self):
        status = self.switch.isChecked()
        choice = 0 if status else -1
        if choice != config.user.remember_last_choice:
            config.update("remember_last_choice", choice)


class SettingShortcutStartStopCard(AppCard):
    """设置项-快捷键"""

    def __init__(self, parent=None):
        super().__init__(FluentIcon.APPLICATION, "快捷键", "启动/停止快捷键", parent)

        self.combobox = ComboBox()
        self.combobox.addItems(default_config.shortcut_start_stop)
        self.combobox.setFixedWidth(120)
        self.combobox.currentIndexChanged.connect(self._config_update)

        self.hBoxLayout.addWidget(self.combobox)

    def _config_update(self):
        text = self.combobox.currentText()
        if text != config.user.shortcut_start_stop:
            config.update("shortcut_start_stop", text)


class SettingWinToastCard(AppCard):
    """设置项-系统通知"""

    def __init__(self, parent=None):
        super().__init__(FluentIcon.RINGER, "系统通知", "使用Windows系统通知推送关键事件", parent)

        self.switch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)  # 文本在左侧
        self.switch.setOnText("启用")
        self.switch.setOffText("禁用")
        self.switch.setChecked(default_config.win_toast)
        self.switch.checkedChanged.connect(self._config_update)

        self.hBoxLayout.addWidget(self.switch)

    def _config_update(self):
        status = self.switch.isChecked()
        if status != config.user.win_toast:
            config.update("win_toast", status)


class SettingInteractionModeCard(ExpandGroupSettingCard):
    """设置项-交互模式"""

    def __init__(self, parent=None):
        super().__init__(FluentIcon.APPLICATION, "交互模式", "", parent)

        self.mode_combobox = ComboBox()
        self.mode_combobox.addItems(default_config.interaction_mode["mode"])
        self.mode_combobox.setFixedWidth(120)
        self.mode_combobox.currentIndexChanged.connect(self._config_update)

        self.frontend_force_window_switch = SwitchButton()
        self.frontend_force_window_switch.setOnText("")
        self.frontend_force_window_switch.setOffText("")
        self.frontend_force_window_switch.setChecked(default_config.interaction_mode["frontend"]["force_window"][0])
        self.frontend_force_window_switch.checkedChanged.connect(self._config_update)

        self.backend_prevent_sleep_switch = SwitchButton()
        self.backend_prevent_sleep_switch.setOnText("")
        self.backend_prevent_sleep_switch.setOffText("")
        self.backend_prevent_sleep_switch.setChecked(default_config.interaction_mode["backend"]["prevent_sleep"][0])
        self.backend_prevent_sleep_switch.checkedChanged.connect(self._config_update)

        self.backend_screenshot_combobox = ComboBox()
        self.backend_screenshot_combobox.addItems(default_config.interaction_mode["backend"]["screenshot_method"])
        self.backend_screenshot_combobox.currentIndexChanged.connect(self._config_update)

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.addGroup(FluentIcon.APPLICATION, "交互模式", "", self.mode_combobox)
        self.addGroup(FluentIcon.APPLICATION, "前台运行时前置游戏窗口", "", self.frontend_force_window_switch)
        self.addGroup(FluentIcon.APPLICATION, "后台运行时禁止系统休眠", "", self.backend_prevent_sleep_switch)
        self.addGroup(
            FluentIcon.APPLICATION,
            "后台截图模式",
            "切换后可在窗口管理处预览是否能够正常截图显示",
            self.backend_screenshot_combobox,
        )

        self.setExpand(True)

        text = self.mode_combobox.currentText()
        disabled = True if text == "前台" else False
        self.frontend_force_window_switch.setDisabled(not disabled)
        self.backend_prevent_sleep_switch.setDisabled(disabled)
        self.backend_screenshot_combobox.setDisabled(disabled)

    def _config_update(self):
        text = self.mode_combobox.currentText()
        disabled = True if text == "前台" else False
        self.frontend_force_window_switch.setDisabled(not disabled)
        self.backend_prevent_sleep_switch.setDisabled(disabled)
        self.backend_screenshot_combobox.setDisabled(disabled)
        if text != config.user.interaction_mode.mode:
            config.update("interaction_mode.mode", text)

        status = self.frontend_force_window_switch.isChecked()
        if status != config.user.interaction_mode.frontend.force_window:
            config.update("interaction_mode.frontend.force_window", status)

        status = self.backend_prevent_sleep_switch.isChecked()
        if status != config.user.interaction_mode.backend.prevent_sleep:
            config.update("interaction_mode.backend.prevent_sleep", status)

        text = self.backend_screenshot_combobox.currentText()
        if text != config.user.interaction_mode.backend.screenshot_method:
            config.update("interaction_mode.backend.screenshot_method", text)


class SettingUpdateCard(ExpandGroupSettingCard):
    """设置项-软件更新"""

    def __init__(self, parent=None):
        super().__init__(FluentIcon.UPDATE, "软件更新", "", parent)

        self.mode_switch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)  # 文本在左侧
        self.mode_switch.setOnText("自动更新")
        self.mode_switch.setOffText("关闭更新")
        self.mode_switch.setChecked(default_config.auto_update)
        self.mode_switch.checkedChanged.connect(self._config_update)

        self.download_combobox = ComboBox()
        self.download_combobox.addItems(default_config.update_download)
        self.download_combobox.setFixedWidth(135)
        self.download_combobox.currentIndexChanged.connect(self._config_update)

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.addGroup(FluentIcon.UPDATE, "自动更新", "在应用程序启动时检查更新", self.mode_switch)
        self.addGroup(FluentIcon.DOWNLOAD, "下载站点", "使用镜像源可加快下载速度", self.download_combobox)

    def _config_update(self):
        status = self.mode_switch.isChecked()
        if status != config.user.auto_update:
            config.update("auto_update", status)

        text = self.download_combobox.currentText()
        if text != config.user.update_download:
            config.update("update_download", text)


class SettingAboutCard(QWidget):
    """设置项-关于"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.home_page_label = HyperlinkLabel("项目主页")
        self.home_page_label.setUrl(HOME_PAGE_LINK)
        self.help_doc_label = HyperlinkLabel("帮助文档")
        self.help_doc_label.setUrl(HELP_DOC_LINK)
        self.qq_group_label = HyperlinkLabel("QQ群")
        self.qq_group_label.setUrl(QQ_GROUP_LINK)

        self.short_cut_button = PushButton("创建快捷方式")
        self.app_restart_button = PushButton("重启应用程序")
        self.update_record_button = PushButton("查看更新记录")

        self.hBoxLayout1 = QHBoxLayout()
        self.hBoxLayout1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout1.addWidget(self.short_cut_button)
        self.hBoxLayout1.addWidget(self.app_restart_button)
        self.hBoxLayout1.addWidget(self.update_record_button)

        self.hBoxLayout2 = QHBoxLayout()
        self.hBoxLayout2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout2.addWidget(self.home_page_label)
        self.hBoxLayout2.addWidget(BodyLabel("|"))
        self.hBoxLayout2.addWidget(self.help_doc_label)
        self.hBoxLayout2.addWidget(BodyLabel("|"))
        self.hBoxLayout2.addWidget(self.qq_group_label)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addLayout(self.hBoxLayout1)
        self.vBoxLayout.addLayout(self.hBoxLayout2)


class SettingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("Setting")

        self.setting_label = SubtitleLabel("设置")
        font = self.setting_label.font()
        font.setWeight(QFont.Weight.Normal)  # 字体不加粗
        self.setting_label.setFont(font)

        self.language_card = SettingLanguageCard()
        self.xuanshangfengyin_card = SettingXuanshangfengyinCard()
        self.interaction_mode_card = SettingInteractionModeCard()
        self.remember_last_choice_card = SettingRememberLastChoiceCard()
        self.shortcut_start_stop_card = SettingShortcutStartStopCard()
        self.win_toast_card = SettingWinToastCard()
        self.group_update = SettingUpdateCard()

        self.about_label = SubtitleLabel("关于")
        font = self.about_label.font()
        font.setWeight(QFont.Weight.Normal)  # 字体不加粗
        self.about_label.setFont(font)
        self.about_card = SettingAboutCard()

        self._widget = QWidget()
        self._layout = QVBoxLayout(self._widget)
        self._layout.addWidget(self.setting_label)
        self._layout.addWidget(self.language_card)
        self._layout.addWidget(self.xuanshangfengyin_card)
        self._layout.addWidget(self.interaction_mode_card)
        self._layout.addWidget(self.remember_last_choice_card)
        self._layout.addWidget(self.shortcut_start_stop_card)
        self._layout.addWidget(self.win_toast_card)
        self._layout.addWidget(self.group_update)
        self._layout.addWidget(self.about_label)
        self._layout.addWidget(self.about_card)

        self.scroll_area = ScrollArea()
        self.scroll_area.setWidgetResizable(True)  # 使滚动区域可调整大小以适应内容
        self.scroll_area.setWidget(self._widget)

        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
