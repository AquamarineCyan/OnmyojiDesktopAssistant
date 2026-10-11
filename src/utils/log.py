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

MIN_KEEP_BYTES: int = _MB
"""旧日志被截断时至少保留的尾部字节数（不会超过预算的 1/10）

避免出现「为了满足上限，把某个旧日志砍到只剩几 KB」的情况 ——
那样既丢了排障价值，又不如直接删掉。保底值也用于决定何时停止截断。
"""


def _log_error(message: str) -> None:
    """清理阶段的告警

    此时 `logger` 尚未构造（cleanup_logs 会在文件处理程序创建之前被调用），
    只能退回 print。抽成小函数是为了不在多处写同样这句注释。
    """
    print(f"[log] {message}")


def _active_log_path() -> Path:
    return Path(LOG_DIR_PATH / f"{APP_NAME}.log")


def _rotated_logs(active: Path) -> list[Path]:
    """当前日志之外的轮转/遗留日志，按修改时间从旧到新"""
    try:
        files = [f for f in LOG_DIR_PATH.glob(f"{APP_NAME}.log*") if f.is_file() and f != active]
    except OSError:
        return []
    return sorted(files, key=lambda f: f.stat().st_mtime)


_TRIM_MARKER: bytes = b"...(earlier content trimmed by retention policy)...\n"
"""截断标记，写在被丢弃的头部位置，说明日志不完整"""


def _truncate_keeping_tail(path: Path, target_bytes: int) -> bool:
    """把文件截断到「最终大小」恰好为 target_bytes，只保留尾部

    Args:
        target_bytes: 截断后**最终**文件大小。标记本身占用的字节会从
            保留的尾部里扣掉，否则每次截断都会让总量多出标记长度，
            清理后仍然略微超出预算。

    Returns:
        bool: 是否真的发生了截断
    """
    marker_len = len(_TRIM_MARKER)
    try:
        if path.stat().st_size <= target_bytes:
            return False
        keep = target_bytes - marker_len
        if keep <= 0:
            return False
        with open(path, "rb") as f:
            f.seek(-keep, os.SEEK_END)
            tail = f.read()
        with open(path, "wb") as f:
            f.write(_TRIM_MARKER)
            f.write(tail)
        return True
    except OSError as e:
        print(f"[log] truncate failed: {e}")
        return False


def cleanup_logs(retention_days: int = DEFAULT_RETENTION_DAYS, max_size_mb: int = DEFAULT_MAX_SIZE_MB) -> None:
    """清理日志目录

    两条规则，先按时间再按总量：
    1. 超过 `retention_days` 天的轮转日志直接删除（<= 0 表示跳过）
    2. 总量超过 `max_size_mb` 时，从**最旧**的轮转日志开始截断，只保留尾部

    当前正在写入的当日日志既不会被删除、也不会被截断 —— 它是排障时
    唯一对应当前问题的那份记录。所以总量超限时优先牺牲旧日志：
    把最旧的轮转日志砍掉头部、保留尾部，直到回到预算内。
    只有当轮转日志全部被时间规则清空、且当日日志本身就超过上限时，
    才会出现无法收敛的情况 —— 此时只告警，不动当日日志。

    Args:
        retention_days: 保留天数，<= 0 表示不按时间清理
        max_size_mb: 目录总大小上限（MB），<= 0 表示不限制
    """
    active = _active_log_path()
    rotated = _rotated_logs(active)

    # 1) 按保留天数：超出保留窗口的轮转日志已经没有保留价值，直接删除
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

    # 2) 按总量上限：从最旧的轮转日志开始截断（保留尾部），不动当日日志
    if max_size_mb > 0:
        budget = max_size_mb * _MB
        sizes = {}
        total = 0
        for f in [active, *rotated]:
            try:
                sizes[f] = f.stat().st_size
                total += sizes[f]
            except OSError:
                sizes[f] = 0

        if total > budget:
            # 保底值不能超过预算的 1/10，否则在小预算下会把「该截断的旧日志」
            # 全部判成不可截断，导致清理完全失效
            keep_floor = min(MIN_KEEP_BYTES, budget // 10)
            excess = total - budget
            for f in rotated:  # 已按 mtime 从旧到新
                if excess <= 0:
                    break
                size = sizes.get(f, 0)
                # keep 是截断后的**最终**大小，截断标记的字节已由
                # _truncate_keeping_tail 内部从保留尾部里扣除
                keep = max(keep_floor, size - excess)
                if keep >= size:
                    continue  # 这个文件在保底值内也砍不动了，跳过
                if _truncate_keeping_tail(f, keep):
                    actual = f.stat().st_size
                    freed = size - actual
                    excess -= freed
                    total -= freed
                    print(f"[log] truncated {f.name}: {size} -> {actual} bytes")

        if total > budget:
            # 轮转日志全部耗尽仍超限：说明是当日日志本身就大于上限。
            # 按设计不截断当日日志（它是排障时唯一有用的记录），只告警。
            _log_error(
                f"日志目录仍超出上限 {total // _MB}MB > {max_size_mb}MB，"
                f"且已无可清理的旧日志（当日日志不会被截断）。请调高上限或调小保留天数。"
            )


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
