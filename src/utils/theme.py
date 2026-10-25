from enum import StrEnum

import darkdetect
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from qfluentwidgets import Theme, setTheme


class AppTheme(StrEnum):
    """界面主题"""

    LIGHT = "浅色"
    DARK = "深色"
    AUTO = "跟随系统"


_app_theme = AppTheme.AUTO
_scheme_signal_connected = False


def apply_theme(mode: str | None = None) -> None:
    """将主题应用到整个应用，需在 QApplication 创建之后调用

    Args:
        mode (str): 主题模式（AppTheme 的值）；None 表示按当前模式重新应用
    """
    global _app_theme
    if mode is not None:
        _app_theme = AppTheme(mode)

    app = QApplication.instance()
    if app is None:
        return

    # 调色板：浅色/深色强制覆盖，跟随系统时交还 Qt 自动翻转（原生对话框等随之变色）
    app.styleHints().setColorScheme({
        AppTheme.LIGHT: Qt.ColorScheme.Light,
        AppTheme.DARK: Qt.ColorScheme.Dark,
        AppTheme.AUTO: Qt.ColorScheme.Unknown,
    }[_app_theme])

    # 不能直接 setTheme(Theme.AUTO)：themeMode 已是 AUTO 时 qconfig.set 会去重跳过，
    # 已解析的 qconfig.theme 不随系统主题刷新，控件样式会停在旧主题；先显式解析
    theme = {
        AppTheme.LIGHT: Theme.LIGHT,
        AppTheme.DARK: Theme.DARK,
        AppTheme.AUTO: Theme.DARK if (darkdetect.theme() or "").lower() == "dark" else Theme.LIGHT,
    }[_app_theme]
    setTheme(theme)

    # qfluentwidgets 感知不到系统主题变化（其监听线程会挂住进程退出，不使用），由 Qt 信号驱动重应用
    global _scheme_signal_connected
    if not _scheme_signal_connected:
        app.styleHints().colorSchemeChanged.connect(
            lambda scheme: apply_theme() if _app_theme == AppTheme.AUTO else None
        )
        _scheme_signal_connected = True
