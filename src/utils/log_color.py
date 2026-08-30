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


_log_colors = dict(DEFAULT_LOG_COLORS)

_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def log_color(level: LogColorLevel) -> str:
    """获取指定等级的当前日志颜色

    Args:
        level (LogColorLevel): 日志颜色等级

    Returns:
        str: 当前颜色
    """
    return _log_colors.get(level, DEFAULT_LOG_COLORS.get(level, "black"))


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
