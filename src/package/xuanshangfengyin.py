#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# xuanshangfengyin.py
"""悬赏封印"""

import random
import time
from pathlib import Path

import pyautogui

from ..utils.application import RESOURCE_DIR_PATH
from ..utils.config import config
from ..utils.decorator import log_function_call, run_in_thread
from ..utils.event import event_xuanshang
from ..utils.log import log
from ..utils.toast import toast
from ..utils.window import window


class XuanShangFengYin:
    """悬赏封印"""

    def __init__(self):
        self.scene_name: str = "悬赏封印"
        self.resource_path: str = "xuanshangfengyin"  # 图片路径
        self._flag_is_first: bool = True
        self._flag: bool = False
        self.flag_work: bool = True  # 是否启用
        self.resource_list: list = [
            "title",  # 特征图像
            "xuanshang_accept",  # 接受
            "xuanshang_refuse",  # 拒绝
            "xuanshang_ignore"  # 忽略
        ]

    def is_working(self) -> bool:
        return bool(self.flag_work)

    def event_is_set(self) -> bool:
        return event_xuanshang.is_set()

    def event_wait(self) -> None:
        event_xuanshang.wait()

    def get_coor_info_picture(self, file: str) -> tuple[int, int]:
        """图像识别，返回图像的全屏随机坐标

        参数:
            file (str): 文件路径&图像名称(*.png)

        返回:
            tuple[int, int]: 识别成功，返回图像的随机坐标，识别失败，返回(0,0)
        """
        filename = RESOURCE_DIR_PATH / file
        if isinstance(filename, Path):
            filename = str(filename)

        try:
            button_location = pyautogui.locateCenterOnScreen(
                filename,
                region=(
                    window.window_left,
                    window.window_top,
                    window.absolute_window_width,
                    window.absolute_window_height
                ),
                confidence=0.8
            )
            x, y = button_location
        except Exception:
            x = y = 0
        finally:
            return x, y

    def check_click(self, file: str) -> None:
        """图像识别，并点击

        参数:
            file (str): 文件路径&图像名称(*.png)
        """
        while True:
            x, y = self.get_coor_info_picture(f"{self.resource_path}/{file}")
            if x != 0 and y != 0:
                # 补间移动，默认启用
                list_tween = [
                    pyautogui.easeInQuad,
                    pyautogui.easeOutQuad,
                    pyautogui.easeInOutQuad
                ]
                random.seed(time.time_ns())
                pyautogui.moveTo(x, y, duration=0.25, tween=random.choice(list_tween))
                pyautogui.click()
                log.ui("定位成功")
                return

    @log_function_call
    @run_in_thread
    def judge(self) -> None:
        log.info("悬赏封印进行中...")
        while True:
            if self._flag_is_first:
                event_xuanshang.set()
                self._flag_is_first = False
            x, y = self.get_coor_info_picture(f"{self.resource_path}/title.png")
            if x != 0 and y != 0:
                if not self._flag:
                    log.scene("悬赏封印")
                    event_xuanshang.clear()
                    self._flag = True
                    log.warn("已暂停后台线程，等待处理", True)
                    print(event_xuanshang.is_set())
                    match config.config_user.get("悬赏封印"):
                        case "接受":
                            log.ui("接受协作")
                            self.check_click("xuanshang_accept.png")
                        case "拒绝":
                            log.ui("拒绝协作")
                            self.check_click("xuanshang_refuse.png")
                        case "忽略":
                            log.ui("忽略协作")
                            self.check_click("xuanshang_ignore.png")
                        case _:
                            log.ui("用户配置出错，自动接受协作")
                            self.check_click("xuanshang_accept.png")
                    toast("悬赏封印", "检测到协作")
            else:
                event_xuanshang.set()
                if self._flag:
                    self._flag = False
                    log.ui("悬赏封印已消失，恢复线程")
                    print(event_xuanshang.is_set())


xuanshangfengyin = XuanShangFengYin()
