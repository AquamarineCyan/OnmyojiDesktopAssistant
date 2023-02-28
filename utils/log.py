#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# log.py
"""
日志
"""

import time
from datetime import date
from pathlib import Path
from utils.config import config
from utils.mysignal import global_ms as ms


class Log:
    def __init__(self) -> None:
        self.application_path = config.application_path
        self.log_dir_path = self.application_path / "log"

    def init(self) -> bool:
        """初始化

        Returns:
            bool: 创建日志文件夹是否成功
        """
        try:
            self.log_dir_path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            return False

    def _write_to_file(self, text: str | int) -> bool:
        """写入日志文件

        Args:
            text (str | int): 文本内容

        Returns:
            bool: 文本写入是否成功
        """
        file: Path = self.log_dir_path / f"log-{time.strftime('%Y%m%d')}.txt"
        if isinstance(text, int):
            text = str(text)
        try:
            with file.open(mode="a", encoding="utf-8") as f:
                f.write(f"{text}\n")
                return True
        except:
            print(f"FileNotFoundError {file}")
            return False

    def _text_format(self, text: str, level: str = "INFO", print_to_gui: bool = False) -> str:
        """封装文本格式

        Args:
            text (str): 文本内容
            level (str): 日志等级，默认"INFO"
            print_to_gui (bool): 是否在UI界面输出，默认否

        Returns:
            str: 日志内容
        """
        time_now = time.strftime("%H:%M:%S")
        match level:
            case "INFO":
                text = f"{time_now} [INFO] {text}"
            case "SCENE":
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

    def info(self, text: str, print_to_gui: bool = False) -> None:
        """标准日志

        Args:
            text (str): 文本内容
            print_to_gui (bool): 是否在UI界面输出，默认否
        """
        self._text_format(text, "INFO", print_to_gui)

    def ui(self, text: str) -> None:
        """基于标准日志的UI输出

        Args:
            text (str): 文本内容
        """
        self.info(text=text, print_to_gui=True)

    def scene(self, text: str) -> None:
        """场景日志

        Args:
            text (str): 场景描述
        """
        self._text_format(text, "SCENE", True)

    def num(self, text: str) -> None:
        """次数日志

        Args:
            text (str): 次数
        """
        ms.text_num_update.emit(text)  # 输出至完成情况UI界面
        self._text_format(text, "NUM", True)

    def warn(self, text: str, print_to_gui: bool = False) -> None:
        """警告日志

        Args:
            text (str): 文本内容
            print_to_gui (bool): 是否在UI界面输出，默认否
        """
        self._text_format(text, "WARN", print_to_gui)

    def error(self, text: str, print_to_gui: bool = False) -> None:
        """错误日志

        Args:
            text (str): 文本内容
            print_to_gui (bool): 是否在UI界面输出，默认否
        """
        self._text_format(text, "ERROR", print_to_gui)

    def is_fighting(self, flag: bool = True) -> None:
        """是否进行中，禁用按钮

        Args:
            flag (bool): 进行中，默认是
        """
        ms.is_fighting_update.emit(flag)

    def clean_up(self) -> bool:
        """日志清理"""
        log.info("log clean up...")
        today = date.today()
        n = 0
        if not self.log_dir_path.is_dir():
            log.error("Not found log dir.")
            return False
        for item in self.log_dir_path.iterdir():
            log_date = date(int(item.stem[-8:-4]), int(item.stem[-4:-2]), int(item.stem[-2:]))
            # 自动清理
            if (today-log_date).days > 30:
                try:
                    item.unlink()
                    n += 1
                    self.info(f"Delect file: {item.absolute()} successfully.")
                except:
                    self.error(f"Delect file: {item.absolute()} failed.")
        self.info(f"Clean up {n} log files in total.")
        return True


log = Log()
