#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# log.py
"""日志"""

import logging
from datetime import date, datetime
from pathlib import Path

from .application import LOG_DIR_PATH
from .mysignal import global_ms as ms


class Log:
    """日志"""

    def __init__(self) -> None:
        _log_file: Path = LOG_DIR_PATH / f"log-{datetime.now().strftime('%Y%m%d')}.log"

        # 创建日志记录器
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # 创建文件处理程序
        file_handler = logging.FileHandler(_log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # 创建屏幕处理程序
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        # 创建日志格式
        formatter = logging.Formatter(
            # fmt="%(asctime)s.%(msecs)03d %(levelname)-7s %(pathname)s[line:%(lineno)d]-%(module)s-%(funcName)s %(message)s",
            fmt="%(asctime)s.%(msecs)03d %(levelname)-7s %(pathname)s[line:%(lineno)d] %(message)s",
            datefmt="%H:%M:%S")
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # 将处理程序添加到日志记录器
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        self.logger = logger
        self.info = self.logger.info
        """use `logger.info` replace `log.info` """

    # def _write_to_file(self, text: str | int) -> bool:
    #     """写入日志文件

    #     参数:
    #         text (str | int): 文本内容

    #     返回:
    #         bool: 文本写入是否成功
    #     """
    #     file: Path = LOG_DIR_PATH / f"log-{datetime.now().strftime('%Y%m%d')}.log"
    #     if isinstance(text, int):
    #         text = str(text)
    #     try:
    #         with file.open(mode="a", encoding="utf-8") as f:
    #             f.write(f"{text}\n")
    #         return True
    #     except Exception:
    #         print(f"FileNotFoundError {file}")
    #         return False

    def _send_gui_msg(self, msg: str = "", color: str = "black"):
        _now = datetime.now().strftime("%H:%M:%S")
        ms.text_print_update.emit(f"{_now} {msg}", color)

    # def _text_format(self, text: str, level: str = "INFO", print_to_gui: bool = False) -> None:
    #     """封装文本格式

    #     参数:
    #         text (str): 文本内容
    #         level (str): 日志等级，默认"INFO"
    #         print_to_gui (bool): 是否在UI界面输出，默认否
    #     """
    #     _color: str = "black"
    #     text = f"[{level}] {text}"
    #     match level:
    #         case "SCENE":
    #             _color = "green"
    #         case "WARN" | "ERROR":
    #             _color = "red"

    #     now = datetime.now()

    #     # 输出至UI界面
    #     if print_to_gui and "[NUM]" not in text:
    #         _now = now.strftime("%H:%M:%S")
    #         ms.text_print_update.emit(f"{_now} {text}", _color)

    #     _now = now.strftime("%H:%M:%S.%f")[:-3]
    #     text = f"[{_now}] {text}"
    #     # 输出至控制台调试
    #     print(text)
    #     # 输出至日志，使用毫秒记录
    #     self._write_to_file(text)

    # def info(self, msg: str) -> None:
    #     """标准日志

    #     参数:
    #         msg (str): 文本内容
    #     """
    #     self.logger.info(msg)

    def ui(self, msg: str) -> None:
        """基于标准日志的UI输出

        参数:
            msg (str): 文本内容
        """
        self.logger.info(msg)
        self._send_gui_msg(msg)

    def scene(self, msg: str) -> None:
        """场景日志

        参数:
            msg (str): 场景描述
        """
        self.logger.info(f"current scene: {msg}")
        self._send_gui_msg(msg, "green")

    def num(self, msg: str) -> None:  # TODO remove and used in printbox
        """次数日志

        参数:
            msg (str): 次数
        """
        ms.text_num_update.emit(msg)  # 输出至完成情况UI界面
        self.logger.info(f"done number: {msg}")

    def warn(self, msg: str, print_to_gui: bool = True) -> None:
        """警告日志

        参数:
            msg (str): 文本内容
            print_to_gui (bool): 是否在UI界面输出，默认否
        """
        self.logger.warning(msg)
        if print_to_gui:
            self._send_gui_msg(msg, "red")

    def error(self, msg: str, print_to_gui: bool = False) -> None:
        """错误日志

        参数:
            msg (str): 文本内容
            print_to_gui (bool): 是否在UI界面输出，默认否
        """
        self.logger.error(msg)
        if print_to_gui:
            self._send_gui_msg(msg, "red")


log = Log()
logger = log.logger


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
