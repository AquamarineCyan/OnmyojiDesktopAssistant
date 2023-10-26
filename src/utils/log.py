#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# log.py
"""日志"""

import logging
from datetime import date, datetime
from pathlib import Path

from .application import LOG_DIR_PATH, APP_NAME
from .mysignal import global_ms as ms

LOG_LEVEL_GUI: int = 25
logging.addLevelName(LOG_LEVEL_GUI, "GUI")


def send_gui_msg(msg: str = "", color: str = "black"):
    _now = datetime.now().strftime("%H:%M:%S")
    ms.main.ui_text_info_update.emit(f"{_now} {msg}", color)


class CustomLogger(logging.Logger):
    def ui(self, msg, level="info", *args, **kwargs):
        if msg is None:
            return
        match level:
            case "info":
                send_gui_msg(msg, "black")
                super()._log(LOG_LEVEL_GUI, msg, args, **kwargs)
            case "warn":
                send_gui_msg(msg, "red")
                super()._log(logging.WARNING, msg, args, **kwargs)
            case "error":
                send_gui_msg(msg, "red")
                super()._log(logging.ERROR, msg, args, **kwargs)

    def scene(self, msg, *args, **kwargs):
        send_gui_msg(msg, "green")
        super()._log(logging.INFO, f"current scene: {msg}", args, **kwargs)

    def num(self, msg, *args, **kwargs):  # TODO remove and used in printbox
        ms.main.ui_text_completion_times_update.emit(msg)  # 输出至完成次数UI界面
        super()._log(logging.INFO, f"done number: {msg}", args, **kwargs)


_log_file: Path = LOG_DIR_PATH / f"log-{datetime.now().strftime('%Y%m%d')}.log"

# 创建日志记录器
logger = CustomLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

# 创建文件处理程序
file_handler = logging.FileHandler(_log_file, encoding="utf-8")
file_handler.setLevel(logging.INFO)

# 创建屏幕处理程序
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# 创建日志格式
formatter = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d %(levelname)-7s %(pathname)s[line:%(lineno)d]-%(funcName)s %(message)s",
    datefmt="%H:%M:%S")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# 将处理程序添加到日志记录器
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def log_clean_up() -> bool:
    """日志清理"""
    # TODO https://docs.python.org/zh-cn/3/library/logging.handlers.html#logging.handlers.TimedRotatingFileHandler
    logger.info("log clean up...")
    today = date.today()
    n = 0
    if not LOG_DIR_PATH.is_dir():
        logger.error("Not found log dir.")
        return False
    for item in LOG_DIR_PATH.iterdir():
        log_date = date(int(item.stem[-8:-4]), int(item.stem[-4:-2]), int(item.stem[-2:]))
        # 自动清理
        if (today-log_date).days > 30:
            try:
                item.unlink()
                n += 1
                logger.info(f"Remove file: {item.absolute()} successfully.")
            except Exception:
                logger.error(f"Remove file: {item.absolute()} failed.")
    logger.info(f"Clean up {n} log files in total.")
    return True
