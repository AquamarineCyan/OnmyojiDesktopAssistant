from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon, FluentWindow, NavigationItemPosition

from ..utils.application import ICO_RESOURCE_PATH
from .home_widget import HomeWidget
from .setting_widget import SettingWidget
from .window_manager_widget import WindowManagerWidget


class Window(FluentWindow):
    """主窗口

    基于 qfluentwidgets 的 FluentWindow：标题栏（FluentTitleBar）、导航栏、
    内容面板的深浅主题样式由 qfluentwidgets 官方 QSS 自动管理，无需自写样式。
    """

    def __init__(self):
        super().__init__()
        # 关闭 Win11 Mica 材质，使用随主题切换的纯色背景
        self.setMicaEffectEnabled(False)

        self.homeInterface = HomeWidget(self)
        self.windowManagerInterface = WindowManagerWidget(self)
        self.settingInterface = SettingWidget(self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FluentIcon.HOME, "首页")
        self.addSubInterface(self.windowManagerInterface, FluentIcon.ZOOM, "窗口管理")
        # 底部顶格
        self.addSubInterface(self.settingInterface, FluentIcon.SETTING, "设置", NavigationItemPosition.BOTTOM)

        self.switchTo(self.homeInterface)

    def initWindow(self):
        self.resize(800, 600)
        self.setWindowIcon(QIcon(ICO_RESOURCE_PATH))
        self.center()

    def center(self):
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()
        # 日志行颜色按追加时的主题写入，切主题后需重刷保证可读
        self.homeInterface.refresh_log_colors()
