from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QHBoxLayout, QStackedWidget
from qfluentwidgets import FluentIcon, NavigationInterface, NavigationItemPosition
from qframelesswindow import FramelessWindow, StandardTitleBar

from ..utils.application import ICO_RESOURCE_PATH
from .effective_entry_analysis_widget import EffectiveEntryAnalysisWidget
from .home_widget import HomeWidget
from .setting_widget import SettingWidget
from .window_manager_widget import WindowManagerWidget


class Window(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self, showMenuButton=True)
        self.stackWidget = QStackedWidget(self)

        self.homeInterface = HomeWidget(self)
        self.windowManagerInterface = WindowManagerWidget(self)
        self.effectiveEntryAnalysisInterface = EffectiveEntryAnalysisWidget(self)

        self.settingInterface = SettingWidget(self)

        self.initLayout()
        self.initNavigation()
        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FluentIcon.HOME, "首页")
        self.addSubInterface(self.windowManagerInterface, FluentIcon.ZOOM, "窗口管理")
        self.addSubInterface(self.effectiveEntryAnalysisInterface, FluentIcon.ZOOM_IN, "有效词条分析")

        # 底部顶格
        self.addSubInterface(self.settingInterface, FluentIcon.SETTING, "设置", NavigationItemPosition.BOTTOM)

        self.navigationInterface.setCurrentItem("Home")  # HomeWidget.ObjectName
        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(0)

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, parent=None):
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None,
        )

    def initWindow(self):
        self.resize(800, 600)
        self.setWindowIcon(QIcon(ICO_RESOURCE_PATH))
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        self.center()

    def center(self):
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())
