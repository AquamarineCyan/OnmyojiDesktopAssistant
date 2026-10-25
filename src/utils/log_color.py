import re
from enum import StrEnum


class LogColorLevel(StrEnum):
    """日志颜色等级"""

    INFO = "info"
    HINT = "hint"
    WARN = "warn"
    ERROR = "error"


DEFAULT_LOG_COLORS = {
    LogColorLevel.INFO: "#000000",  # 黑色
    LogColorLevel.HINT: "#006400",  # 绿色
    LogColorLevel.WARN: "#B8860B",  # 暗金色
    LogColorLevel.ERROR: "#DC143C",  # 红色
}

# 深色界面下的默认色变体：上面的默认色按浅色背景设计，深色背景下不可读
DEFAULT_LOG_COLORS_DARK = {
    LogColorLevel.INFO: "#E0E0E0",  # 浅灰白
    LogColorLevel.HINT: "#66BB6A",  # 亮绿
    LogColorLevel.WARN: "#FFD54F",  # 亮金
    LogColorLevel.ERROR: "#FF6B6B",  # 亮红
}


_log_colors = dict(DEFAULT_LOG_COLORS)

# 方向性换算表：按目标主题把日志历史行的默认色换成对应变体。
# 只做单向映射保证幂等——若做成对称互换，跟随系统翻转后再手动切到同一主题会把颜色换回去
_LOG_COLOR_TO_DARK = {
    DEFAULT_LOG_COLORS[_level].lower(): DEFAULT_LOG_COLORS_DARK[_level].lower() for _level in LogColorLevel
}
_LOG_COLOR_TO_LIGHT = {v: k for k, v in _LOG_COLOR_TO_DARK.items()}

_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def log_color(level: LogColorLevel) -> str:
    """获取指定等级的当前日志颜色

    用户未自定义（颜色等于浅色默认值）时跟随主题：深色界面下改用亮色变体保证可读。

    Args:
        level (LogColorLevel): 日志颜色等级

    Returns:
        str: 当前颜色
    """
    color = _log_colors.get(level, DEFAULT_LOG_COLORS.get(level, "black"))
    # 配置加载时颜色已被 normalize 成小写，与默认值比较需忽略大小写
    if color.lower() == DEFAULT_LOG_COLORS.get(level, "").lower() and is_dark_theme():
        return DEFAULT_LOG_COLORS_DARK.get(level, color)
    return color


def is_dark_theme() -> bool:
    """当前界面是否为深色主题（延迟导入，避免配置加载阶段引入 Qt 依赖）"""
    from qfluentwidgets.common.style_sheet import isDarkTheme

    return isDarkTheme()


def swap_default_color(color: str, to_dark: bool) -> str | None:
    """主题切换时换算颜色：默认色换成目标主题的变体，自定义色返回 None 表示不变

    Args:
        color (str): 当前颜色（#RRGGBB，大小写均可）
        to_dark (bool): True 表示切换目标为深色，False 为浅色

    Returns:
        str | None: 换算后的颜色；非默认色返回 None
    """
    table = _LOG_COLOR_TO_DARK if to_dark else _LOG_COLOR_TO_LIGHT
    return table.get(color.lower())

def normalize_color(color: str, default: str) -> str:
    """校验并归一化颜色为 #RRGGBB 格式，非法时回退默认值

    Args:
        color (str): 待校验的颜色值
        default (str): 非法时回退的默认颜色

    Returns:
        str: 合法的 #RRGGBB 格式颜色；非法时返回 default
    """
    color = color.strip().lower() if isinstance(color, str) else ""
    if _HEX_COLOR_RE.fullmatch(color):
        return color
    return default


def update_log_colors(info: str, hint: str, warn: str, error: str):
    """更新日志各等级的当前显示颜色

    非 #RRGGBB 格式的非法颜色将被回退为对应默认值。

    Args:
        info (str): 普通信息颜色
        hint (str): 提示信息颜色
        warn (str): 警告信息颜色
        error (str): 错误信息颜色
    """
    _log_colors[LogColorLevel.INFO] = normalize_color(info, DEFAULT_LOG_COLORS[LogColorLevel.INFO])
    _log_colors[LogColorLevel.HINT] = normalize_color(hint, DEFAULT_LOG_COLORS[LogColorLevel.HINT])
    _log_colors[LogColorLevel.WARN] = normalize_color(warn, DEFAULT_LOG_COLORS[LogColorLevel.WARN])
    _log_colors[LogColorLevel.ERROR] = normalize_color(error, DEFAULT_LOG_COLORS[LogColorLevel.ERROR])
