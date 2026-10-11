import logging
import os
import sys
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from .application import APP_NAME, LOG_DIR_PATH
from .log_color import LogColorLevel, log_color
from .signals import signal_manager

LOG_LEVEL_GUI: int = 25
logging.addLevelName(LOG_LEVEL_GUI, "GUI")

DEFAULT_RETENTION_DAYS: int = 7
"""默认日志保留天数"""

DEFAULT_MAX_SIZE_MB: int = 100
"""默认日志目录总大小上限（MB）"""

_MB: int = 1024 * 1024


def _active_log_path() -> Path:
    return Path(LOG_DIR_PATH / f"{APP_NAME}.log")


def _rotated_logs(active: Path) -> list[Path]:
    """当前日志之外的轮转/遗留日志，按修改时间从旧到新"""
    try:
        files = [f for f in LOG_DIR_PATH.glob(f"{APP_NAME}.log*") if f.is_file() and f != active]
    except OSError:
        return []
    return sorted(files, key=lambda f: f.stat().st_mtime)


def _truncate_keeping_tail(path: Path, keep_bytes: int) -> bool:
    """把文件截断到只保留尾部 keep_bytes

    用于「单个当日日志就撑爆上限」的情况 —— 此时没有可删的轮转文件。
    只在文件未被打开时调用（见 import 期的那次清理）。
    """
    try:
        if path.stat().st_size <= keep_bytes:
            return False
        with open(path, "rb") as f:
            f.seek(-keep_bytes, os.SEEK_END)
            tail = f.read()
        with open(path, "wb") as f:
            f.write(b"...(earlier content trimmed by retention policy)...\n")
            f.write(tail)
        return True
    except OSError as e:
        print(f"[log] truncate failed: {e}")
        return False


def cleanup_logs(retention_days: int = DEFAULT_RETENTION_DAYS, max_size_mb: int = DEFAULT_MAX_SIZE_MB) -> None:
    """清理日志目录

    两条规则，先按时间再按总量：
    1. 超过 `retention_days` 天的轮转日志直接删除（<= 0 表示跳过）
    2. 仍超过 `max_size_mb` 时，从最旧的轮转日志开始依次删除
    3. 轮转日志删完还超（说明是当日日志本身就过大），把当前日志截断只保留尾部

    当前正在写入的日志永远不会被规则 1/2 删除 —— 它是排障时唯一有用的那份。

    Args:
        retention_days: 保留天数，<= 0 表示不按时间清理
        max_size_mb: 目录总大小上限（MB），<= 0 表示不限制
    """
    active = _active_log_path()
    rotated = _rotated_logs(active)

    # 1) 按保留天数
    if retention_days > 0:
        cutoff = time.time() - retention_days * 86400
        keep = []
        for f in rotated:
            try:
                if f.stat().st_mtime < cutoff:
                    f.unlink(missing_ok=True)
                    print(f"[log] removed expired log: {f.name}")
                else:
                    keep.append(f)
            except OSError:
                keep.append(f)
        rotated = keep

    # 2) 按总量上限
    if max_size_mb > 0:
        budget = max_size_mb * _MB
        total = 0
        sizes = {}
        for f in [active, *rotated]:
            try:
                sizes[f] = f.stat().st_size
                total += sizes[f]
            except OSError:
                sizes[f] = 0

        for f in rotated:  # 已按 mtime 从旧到新
            if total <= budget:
                break
            try:
                f.unlink(missing_ok=True)
                total -= sizes.get(f, 0)
                print(f"[log] removed oversized log: {f.name}")
            except OSError:
                pass

        # 3) 只剩当日日志还超限 → 截断保留尾部
        if total > budget and active.exists():
            if _truncate_keeping_tail(active, budget // 2):
                print(f"[log] truncated active log to {budget // 2 // _MB} MB")


# 导入期先按默认值清一次：此时 file_handler 还没建，截断当前日志是安全的。
# 用户配置加载后 Config._init 会再调一次，用实际设置覆盖。
cleanup_logs()


def send_gui_msg(msg: str = "", level: LogColorLevel = LogColorLevel.INFO):
    """发送消息到GUI日志文本框

    Args:
        msg (str): 消息内容
        level (LogColorLevel): 日志颜色等级
    """
    _now = datetime.now().astimezone().strftime("%H:%M:%S")
    signal_manager.main.ui_text_info_appended.emit(f"{_now} {msg}", log_color(level))


class CustomLogger(logging.Logger):
    def ui(self, msg, *args, **kwargs):
        send_gui_msg(msg, LogColorLevel.INFO)
        super()._log(LOG_LEVEL_GUI, msg, args, **kwargs, stacklevel=2)

    def ui_hint(self, msg, *args, **kwargs):
        send_gui_msg(msg, LogColorLevel.HINT)
        super()._log(logging.INFO, msg, args, **kwargs, stacklevel=2)

    def ui_warn(self, msg, *args, **kwargs):
        send_gui_msg(msg, LogColorLevel.WARN)
        super()._log(logging.WARNING, msg, args, **kwargs, stacklevel=2)

    def ui_error(self, msg, *args, **kwargs):
        send_gui_msg(msg, LogColorLevel.ERROR)
        super()._log(logging.ERROR, msg, args, **kwargs, stacklevel=2)

    def progress(self, msg, *args, **kwargs):
        signal_manager.main.ui_text_progress_changed.emit(str(msg))  # 输出至完成情况UI界面
        super()._log(logging.INFO, f"done number: {msg}", args, **kwargs, stacklevel=2)


# 创建日志记录器
logger = CustomLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

# 创建文件处理程序
# backupCount 只按份数留档，真正的「保留天数 / 目录总大小上限」由上面的
# cleanup_logs 负责（按份数无法限制单份体积，也无法限制天数）
file_handler = TimedRotatingFileHandler(
    _active_log_path(),
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8",
)

file_handler.setLevel(logging.INFO)

# 创建屏幕处理程序
# 无控制台打包时 sys.stderr 为 None，兜底到空设备，避免每次输出触发异常
_stream = sys.stderr if sys.stderr is not None else open(os.devnull, "w", encoding="utf-8")
stream_handler = logging.StreamHandler(_stream)
stream_handler.setLevel(logging.DEBUG)

# 创建日志格式
formatter = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d %(levelname)-7s %(filename)s[line:%(lineno)d]-%(funcName)s %(message)s",
    datefmt="%H:%M:%S",
)
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# 将处理程序添加到日志记录器
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


class _LogRedirectStream:
    """将第三方库通过 print / sys.stdout.write 输出的文本转发到日志文件"""

    def __init__(self, name: str, level: int = logging.INFO):
        self._name = name
        self._level = level
        self._buffer = ""

    def write(self, text: str):
        if not text:
            return
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                logger.log(self._level, f"[{self._name}] {line}")

    def flush(self):
        if self._buffer.strip():
            logger.log(self._level, f"[{self._name}] {self._buffer}")
            self._buffer = ""

    def isatty(self) -> bool:
        return False


def redirect_third_party_output():
    """在 sys.stdout / sys.stderr 为空（无控制台打包）时，将其重定向到日志文件"""
    if sys.stdout is None:
        sys.stdout = _LogRedirectStream("stdout")
    if sys.stderr is None:
        sys.stderr = _LogRedirectStream("stderr")
