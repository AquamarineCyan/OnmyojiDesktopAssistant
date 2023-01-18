#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# log.py
"""
日志

from utils.log import log
"""

import time
from pathlib import Path
from utils.config import config
from utils.mysignal import global_ms as ms


class Log:
    def __init__(self) -> None:
        self.fpath = config.application_path

    def init(self) -> bool:
        """初始化

        Returns:
            bool: 是否存在日志文件夹
        """
        if self.fpath.joinpath("log") not in self.fpath.iterdir():
            print("no log dir")
            try:
                Path(fr"{self.fpath}\log").mkdir()
                print("log succend")
                return True
            except:
                print("log failed")
                return False
        else:
            print("log already has")
            return True

    def _write_to_file(self, text: str | int) -> None:
        """write text to log.txt

        Args:
            text (str | int): 文本内容
        """
        try:
            with open(fr"{self.fpath}\log\log-{time.strftime('%Y%m%d')}.txt", mode="a", encoding="utf-8") as f:
                f.write(text)
                f.write("\n")
        except:
            print(
                f"FileNotFoundError {self.fpath}\log\log-{time.strftime('%Y%m%d')}.txt")
            print("fail to create log")

    def _text(self, text: str, level: str = "INFO", print_to_gui: bool = False) -> str:
        """封装文本格式

        Args:
            text (str): 文本内容
            level (str, optional): 日志等级. Defaults to "INFO".
            print_to_gui (bool, optional): 是否在UI界面输出. Defaults to False.

        Returns:
            str: 日志内容
        """
        time_now = time.strftime("%H:%M:%S")
        match level:
            case "INFO":
                text = f"{time_now} [INFO] {text}"
            case "SCENE":  # TODO "[SCENE]" for GUI print text
                text = f"{time_now} [SCENE] {text}"
            case "NUM":
                text = f"{time_now} [NUM] {text}"
            case "WARN":
                text = f"{time_now} [WARN] {text}"
            case "ERROR":
                text = f"{time_now} [ERROR] {text}"
            case _:
                text = f"{time_now} [INFO] {text}"
        print(text)  # 输出至控制台调试
        if print_to_gui:
            if "[NUM]" not in text:
                ms.text_print_update.emit(text)  # 输出至UI界面
        self._write_to_file(text)

    def info(self, text: str, print_to_gui: bool = False):
        """标准日志

        Args:
            text (str): 文本内容
            print_to_gui (bool, optional): 是否在UI界面输出. Defaults to False.
        """
        self._text(text, "INFO", print_to_gui)

    def ui(self, text: str) -> None:
        """基于标准日志的UI输出

        Args:
            text (str): 文本内容
        """
        self.info(text=text, print_to_gui=True)

    def scene(self, text: str):
        """场景日志

        Args:
            text (str): 场景描述
        """
        self._text(text, "SCENE", True)

    def num(self, text: str):
        """次数日志

        Args:
            text (str): 次数
        """
        ms.text_num_update.emit(text)  # 输出至完成情况UI界面
        self._text(text, "NUM", True)

    def warn(self, text: str, print_to_gui: bool = False):
        """警告日志

        Args:
            text (str): 文本内容
            print_to_gui (bool, optional): 是否在UI界面输出. Defaults to False.
        """
        self._text(text, "WARN", print_to_gui)
    
    def error(self, text: str, print_to_gui: bool = False):
        """错误日志

        Args:
            text (str): 文本内容
            print_to_gui (bool, optional): 是否在UI界面输出. Defaults to False.
        """
        self._text(text, "ERROR", print_to_gui)

    def is_fighting(self, flag: bool = True):
        """是否进行中，禁用按钮

        Args:
            flag (bool, optional): 进行中. Defaults to True.
        """
        ms.is_fighting_update.emit(flag)

    def clean(self) -> None:
        """日志清理"""
        # TODO 自动清理
        if Path("log").exists():
            for filename in Path("log").iterdir():
                print(filename)
                try:
                    Path(filename).unlink()
                    print(f"remove {filename} successfully")
                except:
                    print(f"FileNotFoundError {filename}")
            Path("log").rmdir()


log = Log()
