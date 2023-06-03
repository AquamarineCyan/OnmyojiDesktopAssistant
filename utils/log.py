#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# log.py
"""日志"""

from datetime import date, datetime
from pathlib import Path

from .mysignal import global_ms as ms
from .application import app


class Log:
    """日志"""

    def init(self) -> bool:
        """初始化

        返回:
            bool: 创建日志文件夹是否成功
        """
        try:
            app.LOG_DIR_PATH.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def _write_to_file(self, text: str | int) -> bool:
        """写入日志文件

        参数:
            text (str | int): 文本内容

        返回:
            bool: 文本写入是否成功
        """
        file: Path = app.LOG_DIR_PATH / f"log-{datetime.now().strftime('%Y%m%d')}.txt"
        if isinstance(text, int):
            text = str(text)
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        text = f"[{now}] {text}"
        try:
            with file.open(mode="a", encoding="utf-8") as f:
                f.write(f"{text}\n")
            return True
        except Exception:
            print(f"FileNotFoundError {file}")
            return False

    def _text_format(self, text: str, level: str = "INFO", print_to_gui: bool = False) -> None:
        """封装文本格式

        参数:
            text (str): 文本内容
            level (str): 日志等级，默认"INFO"
            print_to_gui (bool): 是否在UI界面输出，默认否
        """
        _color: str = "black"
        text = f"[{level}] {text}"
        match level:
            case "SCENE":
                _color = "green"
            case "WARN" | "ERROR":
                _color = "red"
        # 输出至日志，使用毫秒记录
        self._write_to_file(text)
        now = datetime.now().strftime("%H:%M:%S")
        # 输出至控制台调试
        print(f"[{now}] {text}")
        # 输出至UI界面
        text = f"{now} {text}"
        if print_to_gui and "[NUM]" not in text:
            ms.text_print_update.emit(text, _color)

    def info(self, text: str, print_to_gui: bool = False) -> None:
        """标准日志

        参数:
            text (str): 文本内容
            print_to_gui (bool): 是否在UI界面输出，默认否
        """
        self._text_format(text, "INFO", print_to_gui)

    def ui(self, text: str) -> None:
        """基于标准日志的UI输出

        参数:
            text (str): 文本内容
        """
        self.info(text=text, print_to_gui=True)

    def scene(self, text: str) -> None:
        """场景日志

        参数:
            text (str): 场景描述
        """
        self._text_format(text, "SCENE", True)

    def num(self, text: str) -> None:
        """次数日志

        参数:
            text (str): 次数
        """
        ms.text_num_update.emit(text)  # 输出至完成情况UI界面
        self._text_format(text, "NUM", True)

    def warn(self, text: str, print_to_gui: bool = True) -> None:
        """警告日志

        参数:
            text (str): 文本内容
            print_to_gui (bool): 是否在UI界面输出，默认否
        """
        self._text_format(text, "WARN", print_to_gui)

    def error(self, text: str, print_to_gui: bool = False) -> None:
        """错误日志

        参数:
            text (str): 文本内容
            print_to_gui (bool): 是否在UI界面输出，默认否
        """
        self._text_format(text, "ERROR", print_to_gui)

    def is_fighting(self, flag: bool = True) -> None:
        """是否进行中，禁用按钮

        参数:
            flag (bool): 进行中，默认是
        """
        ms.is_fighting_update.emit(flag)

    def clean_up(self) -> bool:
        """日志清理"""
        log.info("log clean up...")
        today = date.today()
        n = 0
        if not app.LOG_DIR_PATH.is_dir():
            log.error("Not found log dir.")
            return False
        for item in app.LOG_DIR_PATH.iterdir():
            log_date = date(int(item.stem[-8:-4]), int(item.stem[-4:-2]), int(item.stem[-2:]))
            # 自动清理
            if (today-log_date).days > 30:
                try:
                    item.unlink()
                    n += 1
                    self.info(f"Remove file: {item.absolute()} successfully.")
                except Exception:
                    self.error(f"Remove file: {item.absolute()} failed.")
        self.info(f"Clean up {n} log files in total.")
        return True


log = Log()
