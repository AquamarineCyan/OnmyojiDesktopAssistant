import logging
import os
import sys
from datetime import date, datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from .application import APP_NAME, LOG_DIR_PATH
from .log_color import LogColorLevel, log_color
from .mysignal import global_ms as ms

LOG_LEVEL_GUI: int = 25
logging.addLevelName(LOG_LEVEL_GUI, "GUI")


def send_gui_msg(msg: str = "", level: LogColorLevel = LogColorLevel.INFO):
    """发送消息到GUI日志文本框

    Args:
        msg (str): 消息内容
        level (LogColorLevel): 日志颜色等级
    """
    _now = datetime.now().strftime("%H:%M:%S")
    ms.main.ui_text_info_update.emit(f"{_now} {msg}", log_color(level))


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
        ms.main.ui_text_progress_update.emit(str(msg))  # 输出至完成情况UI界面
        super()._log(logging.INFO, f"done number: {msg}", args, **kwargs, stacklevel=2)


# 创建日志记录器
logger = CustomLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

# 创建文件处理程序
file_handler = TimedRotatingFileHandler(
    Path(LOG_DIR_PATH / f"{APP_NAME}.log"),
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


def log_clean_up() -> bool:
    """日志清理"""
    # TODO v2.1.0后移除
    logger.info("log clean up...")
    today = date.today()
    n = 0
    if not LOG_DIR_PATH.is_dir():
        logger.error("Not found log dir.")
        return False
    for item in LOG_DIR_PATH.iterdir():
        try:
            log_date = date(int(item.stem[-8:-4]), int(item.stem[-4:-2]), int(item.stem[-2:]))
            # 自动清理
            if (today - log_date).days > 30:
                try:
                    item.unlink()
                    n += 1
                    logger.info(f"Remove file: {item.absolute()} successfully.")
                except Exception:
                    logger.error(f"Remove file: {item.absolute()} failed.")
        except Exception:
            continue
    logger.info(f"Clean up {n} log files in total.")
    return True
