#!usr/bin/env python3
# baiguiyexing.py
"""
百鬼夜行
"""

import time
import random
import pathlib
import pyautogui

from . import window
from .function import Function
from mysignal import global_ms as ms

'''
标题
title.png
进入
jinru.png
押选
ya.png
开始
kaishi.png
百鬼契约书
baiguiqiyueshu.png
'''


class BaiGuiYeXing(Function):
    """百鬼夜行"""

    def __init__(self):
        super().__init__()
        self.picpath = 'baiguiyexing'  # 路径
        self.screenshotpath = 'cache_baiguiyexing'  # 截图路径
        self.m = 0  # 当前次数
        self.n = None  # 总次数

    def title(self):
        """场景"""
        flag_title = True  # 场景提示
        while 1:
            if self.judge_scene(f'{self.picpath}/title.png', '[SCENE] 百鬼夜行'):
                return True
            elif flag_title:
                flag_title = False
                ms.text_print_update.emit('[WARN] 请检查游戏场景')

    def start(self):
        """开始"""
        self.judge_click(f'{self.picpath}/jinru.png')

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
        while 1:
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
            x, y = self.random_coor(x1, x2, _y1, _y2)
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
            pyautogui.click()
            time.sleep(2)
            x, y = self.get_coor_info_picture(f'{self.picpath}/ya.png')
            if x != 0 and y != 0:
                print('already choose')
                break
        self.judge_click(f'{self.picpath}/kaishi.png', dura=0.5)

    def fighting(self):
        """砸豆子"""
        n = 250  # 豆子数量
        time.sleep(2)
        while n > 0:
            self.random_sleep(0, 1)
            x, y = self.random_coor(60, window.absolute_window_width - 120, 300,
                                    window.absolute_window_height - 100)
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.25)
            pyautogui.click()
            n -= 5

    def finish(self):
        """结束"""
        while 1:
            x, y = self.get_coor_info_picture(f'{self.picpath}/baiguiqiyueshu.png')
            time.sleep(2)
            if x != 0 and y != 0:
                self.screenshot(self.screenshotpath)
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                break

    def run(self, n: int):
        time.sleep(2)
        self.n = n
        if self.title():
            ms.text_num_update.emit(f'0/{self.n}')
            self.random_sleep(1, 3)
            while self.m < self.n:
                self.random_sleep(0, 2)
                self.start()
                self.random_sleep(1, 3)
                self.choose()
                self.random_sleep(2, 4)
                self.fighting()
                self.random_sleep(2, 4)
                self.finish()
                self.m += 1
                ms.text_num_update.emit(f'{self.m}/{self.n}')
                time.sleep(4)
                if self.m == 12 or self.m == 25 or self.m == 39:
                    self.random_sleep(10, 20)
        ms.text_print_update.emit(f'已完成 百鬼夜行{self.m}次')
        # 启用按钮
        ms.is_fighting_update.emit(False)
