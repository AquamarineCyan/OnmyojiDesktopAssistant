from contextlib import suppress

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget
from qfluentwidgets import (
    FluentIcon,
    FluentWindow,
    InfoBar,
    InfoBarIcon,
    InfoBarPosition,
    NavigationItemPosition,
)

from ..utils.application import ICO_RESOURCE_PATH
from .home_widget import HomeWidget
from .info_bar import BelowTitleBarInfoBarManager  # noqa: F401
from .ocr_detection_widget import OcrDetectionWidget
from .setting_widget import SettingWidget
from .window_manager_widget import WindowManagerWidget


class CustomWindow(FluentWindow):
    """主窗口基类

    基于 qfluentwidgets 的 FluentWindow：标题栏（FluentTitleBar）、导航栏、
    内容面板的深浅主题样式由 qfluentwidgets 官方 QSS 自动管理，无需自写样式。
    仅承载界面通用能力，业务逻辑由子类实现。
    """

    def __init__(self):
        super().__init__()
        # 关闭 Win11 Mica 材质，使用随主题切换的纯色背景
        self.setMicaEffectEnabled(False)

        self.sub_windows: list[QWidget] = []  # 子窗口列表

        self.homeInterface = HomeWidget(self)
        self.windowManagerInterface = WindowManagerWidget(self)
        self.ocrDetectionInterface = OcrDetectionWidget(self)

        self.settingInterface = SettingWidget(self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FluentIcon.HOME, "首页")
        self.addSubInterface(self.windowManagerInterface, FluentIcon.ZOOM, "窗口管理")
        self.addSubInterface(self.ocrDetectionInterface, FluentIcon.SEARCH, "文字识别")

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

    def open_sub_window(self, window: QWidget) -> QWidget:
        """注册并打开独立子弹窗，统一管理以便关闭软件时一起关闭

        Args:
            window (QWidget): 要打开的弹窗

        Returns:
            QWidget: 传入的弹窗实例
        """
        self.sub_windows.append(window)
        window_id = id(window)
        window.destroyed.connect(lambda *_, wid=window_id: self._forget_sub_window(wid))
        window.show()
        return window

    def _forget_sub_window(self, window_id: int) -> None:
        """子窗口销毁后移除引用"""
        self.sub_windows[:] = [w for w in self.sub_windows if id(w) != window_id]

    def show_info_bar(
        self,
        icon: InfoBarIcon,
        title: str,
        content: str,
        duration: int = 5,
        is_closable: bool = True,
        auto_show: bool = True,
    ) -> InfoBar:
        """在主窗口右上角显示 InfoBar 通知

        Args:
            icon (InfoBarIcon): 图标
            title (str): 标题
            content (str): 内容
            duration (int): 显示时长（秒），`-1` 为不自动关闭
            is_closable (bool): 是否显示关闭按钮
            auto_show (bool): 是否立即显示，为 `False` 时由调用方配置完内容后自行显示

        Returns:
            InfoBar: 提示条实例
        """
        bar = InfoBar(
            icon,
            title,
            content,
            orient=Qt.Horizontal,
            isClosable=is_closable,
            duration=-1 if duration < 0 else duration * 1000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self,
        )
        if auto_show:
            bar.show()
        return bar

    def info_bar_requested_handle(self, title: str, content: str, level: str, duration: int = 5):
        """主界面 InfoBar 通知

        Args:
            title (str): 标题
            content (str): 内容
            level (str): 级别，`success` / `warning` / `info`
            duration (int): 显示时长（秒），`-1` 为不自动关闭
        """
        icon = {
            "success": InfoBarIcon.SUCCESS,
            "warning": InfoBarIcon.WARNING,
        }.get(level, InfoBarIcon.INFORMATION)
        self.show_info_bar(icon, title, content, duration=duration)

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()
        # 日志行颜色按追加时的主题写入，切主题后需重刷保证可读
        self.homeInterface.refresh_log_colors()

    def closeEvent(self, event):
        """关闭窗口时一并关闭子窗口"""
        for child in list(self.sub_windows):
            with suppress(RuntimeError):
                if child is not None and child.isVisible():
                    child.close()
        self.sub_windows.clear()

        super().closeEvent(event)

    def _exit_handle(self):
        self.close()
