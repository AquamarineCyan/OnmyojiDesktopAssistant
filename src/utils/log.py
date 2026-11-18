import logging
import os
import re
import sys
import threading
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from .application import APP_NAME, LOG_DIR_PATH
from .log_color import LogColorLevel, log_color
from .signals import signal_manager

LOG_LEVEL_GUI: int = 25
logging.addLevelName(LOG_LEVEL_GUI, "GUI")


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


def today_log_file() -> Path:
    """获取当天的日志文件路径（文件名带日期）"""
    return LOG_DIR_PATH / f"{APP_NAME}_{datetime.now().astimezone().strftime('%Y%m%d')}.log"


def migrate_legacy_log_files():
    """将旧命名格式的日志文件重命名为新格式，由 30 天保留规则统一清理

    - OnmyojiDesktopAssistant.log            → OnmyojiDesktopAssistant_{文件修改日期}.log
    - OnmyojiDesktopAssistant.log.2026-11-18 → OnmyojiDesktopAssistant_20261118.log
    目标文件已存在时直接删除旧文件。
    TODO: 兼容旧版本日志命名使用，v2.3.0 删除本函数及其调用
    """
    legacy_pattern = re.compile(rf"^{re.escape(APP_NAME)}\.log(?:\.(\d{{4}})-(\d{{2}})-(\d{{2}}))?$")
    try:
        entries = sorted(LOG_DIR_PATH.iterdir())
    except OSError:
        return
    for path in entries:
        if not path.is_file():
            continue
        match = legacy_pattern.match(path.name)
        if not match:
            continue
        try:
            if match.group(1):
                date = f"{match.group(1)}{match.group(2)}{match.group(3)}"
            else:
                date = datetime.fromtimestamp(path.stat().st_mtime).astimezone().strftime("%Y%m%d")
            target = LOG_DIR_PATH / f"{APP_NAME}_{date}.log"
            if target.exists():
                # 目标文件已存在时直接删除旧文件
                path.unlink()
            else:
                path.rename(target)
        except OSError:
            pass


class DailyFileHandler(TimedRotatingFileHandler):
    """按天分文件的日志处理器

    启动时直接写入带当天日期的文件，跨天后的第一条日志自动切换到新日期的文件。
    切换时先打开新文件，成功后再关闭旧文件，不重命名文件，避免文件被其它进程占用时切分失败。
    """

    def __init__(self, log_dir: Path, app_name: str, backup_count: int = 30):
        self._log_dir = Path(log_dir)
        self._app_name = app_name
        self._current_date = self._today()
        super().__init__(
            self._log_file(self._current_date),
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8",
        )
        self._file_pattern = re.compile(rf"^{re.escape(self._app_name)}_\d{{8}}\.log$")
        self._cleanup_backups()

    @staticmethod
    def _today() -> str:
        return datetime.now().astimezone().strftime("%Y%m%d")

    def _log_file(self, date: str) -> Path:
        return self._log_dir / f"{self._app_name}_{date}.log"

    def shouldRollover(self, record) -> bool:
        return self._today() != self._current_date

    def doRollover(self):
        new_date = self._today()
        old_stream, old_base = self.stream, self.baseFilename
        self.baseFilename = os.path.abspath(self._log_file(new_date))
        try:
            new_stream = self._open()
        except OSError:
            # 新文件打开失败时继续写旧文件，避免 stream 为空导致后续日志写入全部异常
            self.baseFilename = old_base
            return
        self.stream = new_stream
        self._current_date = new_date
        if old_stream:
            old_stream.close()

    def _cleanup_backups(self):
        """只保留最近 backupCount 天的日志文件"""
        if self.backupCount <= 0:
            return
        files = sorted(p for p in self._log_dir.glob(f"{self._app_name}_*.log") if self._file_pattern.match(p.name))
        for path in files[: -self.backupCount]:
            try:
                path.unlink()
            except OSError:
                pass


# 创建日志记录器
logger = CustomLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

# 旧命名日志迁移为新格式（须在打开当天日志文件前执行）
migrate_legacy_log_files()

# 创建文件处理程序
file_handler = DailyFileHandler(log_dir=LOG_DIR_PATH, app_name=APP_NAME, backup_count=30)

file_handler.setLevel(logging.INFO)

# 创建屏幕处理程序
# 无控制台打包时 sys.stderr 为 None，兜底到空设备，避免每次输出触发异常
_stream = sys.stderr if sys.stderr is not None else open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115
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


_redirect_local = threading.local()
"""记录当前线程是否正在把输出写入日志，用于重入保护"""


class _LogRedirectStream:
    """将第三方库通过 print / sys.stdout.write 输出的文本转发到日志文件"""

    def __init__(self, name: str, level: int = logging.INFO):
        self._name = name
        self._level = level
        self._buffer = ""

    def write(self, text: str):
        if not text:
            return
        # 重入保护：日志写入过程中若再次触发（如 handler 报错时写 stderr），直接丢弃，避免递归
        if getattr(_redirect_local, "writing", False):
            return
        _redirect_local.writing = True
        try:
            self._buffer += text
            while "\n" in self._buffer:
                line, self._buffer = self._buffer.split("\n", 1)
                if line.strip():
                    logger.log(self._level, f"[{self._name}] {line}")
        finally:
            _redirect_local.writing = False

    def flush(self):
        if not self._buffer.strip() or getattr(_redirect_local, "writing", False):
            return
        _redirect_local.writing = True
        try:
            logger.log(self._level, f"[{self._name}] {self._buffer}")
            self._buffer = ""
        finally:
            _redirect_local.writing = False

    def isatty(self) -> bool:
        return False


def redirect_third_party_output():
    """在 sys.stdout / sys.stderr 为空（无控制台打包）时，将其重定向到日志文件"""
    if sys.stdout is None:
        sys.stdout = _LogRedirectStream("stdout")
    if sys.stderr is None:
        sys.stderr = _LogRedirectStream("stderr")
