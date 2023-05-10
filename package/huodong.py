#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# huodong.py
"""限时活动"""

import random

import pyautogui

from utils.decorator import *
from utils.function import (
    check_click,
    check_scene,
    check_scene_multiple_once,
    click,
    finish,
    finish_random_left_right,
    random_sleep
)
from utils.log import log
from utils.window import window


class HuoDong:
    """限时活动"""

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        self.scene_name: str = "限时活动"
        self.n: int = 0  # 当前次数
        self.max: int = n  # 总次数
        self.resource_path: str = "huodong"  # 路径
        self.resource_list: list = [  # 资源列表
            "title",  # 限时活动特征图像
            "start"  # 挑战
        ]

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if check_scene(f"{self.resource_path}/title", self.scene_name):
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景")

    def start(self):
        """挑战开始"""
        check_click(f"{self.resource_path}/start")

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        if self.title():
            log.num(f"0/{self.max}")
            random_sleep(1, 3)
            while self.n < self.max:
                random_sleep(1, 2)
                # 开始
                check_click(f"{self.resource_path}/tiaozhan")
                # 结束
                finish()
                random_sleep(1, 2)
                # 结算
                finish_random_left_right(is_multiple_drops_y=True)
                random_sleep(1, 3)
                self.n += 1
                log.num(f"{self.n}/{self.max}")
        log.ui(f"已完成 {self.scene_name} {self.n}次")


class BaiMianGuiYi(HuoDong):
    """百面归一"""

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        if self.title():
            log.num(f"0/{self.max}")
            _flag_title_msg: bool = True

            while self.n < self.max:
                _resource_list = ["title", "start", "hechengbiao", "finish", "money"]
                scene, coor = check_scene_multiple_once(_resource_list, self.resource_path)
                if scene:
                    log.ui(f"scene: {scene}")
                match scene:
                    case "title":
                        self.start()
                        _flag_title_msg = False
                    case "start":
                        click(coor)
                        _flag_title_msg = False
                    case "hechengbiao":
                        log.ui("进行中")
                        _x = window.absolute_window_width / 2
                        _y = window.absolute_window_height / 2
                        # 移至正中心
                        pyautogui.moveTo(_x + window.window_left, _y+window.window_top)
                        random.seed(time.time_ns())
                        x, y = random.choice([(0, 50), (0, -50), (50, 0), (-50, 0)])
                        pyautogui.drag(x, y, button="left")
                        _flag_title_msg = False
                    case "finish":
                        log.ui("结算")
                        finish_random_left_right()
                        self.n += 1
                        log.num(f"{self.n}/{self.max}")
                    case "money":
                        log.ui("结束")
                        click()
                    case _:
                        if _flag_title_msg:
                            log.warn("请检查游戏场景")
                            _flag_title_msg = False
        log.ui(f"已完成 {self.scene_name} {self.n}次")
