#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# baiguiyexing.py
"""百鬼夜行"""

import random
import time

import pyautogui

from utils.decorator import *
from utils.function import (
    check_click,
    check_scene,
    get_coor_info,
    random_coor,
    random_sleep,
    screenshot
)
from utils.log import log
from utils.window import window


class BaiGuiYeXing:
    """百鬼夜行"""

    @log_function_call
    def __init__(self, n: int = 0):
        self.scene_name: str = "百鬼夜行"
        self.n: int = 0  # 当前次数
        self.max: int = n  # 总次数
        self.resource_path = "baiguiyexing"  # 资源路径
        self.resource_list: list = [  # 资源列表
            "title",  # 标题
            "jinru",  # 进入
            "ya",  # 押选
            "kaishi",  # 开始
            "baiguiqiyueshu"  # 百鬼契约书
        ]
        self.screenshotpath = "cache_baiguiyexing"  # 截图路径

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if check_scene(f"{self.resource_path}/title", self.scene_name):
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def start(self):
        """开始"""
        check_click(f"{self.resource_path}/jinru")

    def choose(self):
        """鬼王选择"""
        _x1_left = 230
        _x1_right = 260
        _x2_left = 560
        _x2_right = 590
        _x3_left = 880
        _x3_right = 910
        _y1 = 300
        _y2 = 550
        while True:
            # 获取系统当前时间戳
            random.seed(time.time_ns())
            m = random.random() * 3 + 1
            if m < 2:
                x1 = _x1_left
                x2 = _x1_right
            elif m < 3:
                x1 = _x2_left
                x2 = _x2_right
            else:
                x1 = _x3_left
                x2 = _x3_right
            x, y = random_coor(x1, x2, _y1, _y2).coor
            pyautogui.moveTo(
                x + window.window_left,
                y + window.window_top,
                duration=0.5
            )
            pyautogui.click()
            time.sleep(2)
            x, y = get_coor_info(f"{self.resource_path}/ya").coor
            if x != 0 and y != 0:
                log.ui("已选择鬼王")
                break
        check_click(f"{self.resource_path}/kaishi", dura=0.5)

    def fighting(self):
        """砸豆子"""
        n = 250  # 豆子数量
        time.sleep(2)
        while n > 0:
            random_sleep(0.2, 1)
            x, y = random_coor(
                60,
                window.absolute_window_width - 120,
                300,
                window.absolute_window_height - 100
            ).coor
            pyautogui.moveTo(
                x + window.window_left,
                y + window.window_top,
                duration=0.25
            )
            pyautogui.click()
            n -= 5

    def finish(self):
        """结束"""
        while True:
            coor = get_coor_info(f'{self.resource_path}/baiguiqiyueshu')
            time.sleep(2)
            if coor.is_effective:
                screenshot(self.screenshotpath)
                pyautogui.moveTo(coor.x, coor.y, duration=0.5)
                pyautogui.click()
                break

    @run_in_thread
    @time_count
    @log_function_call
    def run(self):
        if self.title():
            log.num(f"0/{self.max}")
            random_sleep(1, 3)
            while self.n < self.max:
                random_sleep(0, 2)
                self.start()
                random_sleep(1, 3)
                self.choose()
                random_sleep(2, 4)
                self.fighting()
                random_sleep(2, 4)
                self.finish()
                self.n += 1
                log.num(f"{self.n}/{self.max}")
                time.sleep(4)
                # TODO 更新随机判断
                if self.n == 12 or self.n == 25 or self.n == 39:
                    random_sleep(10, 20)
        log.ui(f"已完成 {self.scene_name} {self.n}次")
