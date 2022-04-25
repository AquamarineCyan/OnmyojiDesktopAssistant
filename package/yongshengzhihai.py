#!/usr/bin/env python3
# yongshengzhihai.py
"""
组队永生之海副本
仅支持进行中的永生之海副本
主界面功能8
"""

import time
import pyautogui

from . import function
from . import window
from mysignal import global_ms as ms

'''
组队界面
title.png
挑战按钮
tiaozhan.png
队员
passenger.png
对局进行中
fighting.png
永生之海副本结算按钮
victory.png
'''


class YongShengZhiHai:
    """组队永生之海副本"""

    def __init__(self):
        self.picpath = 'yongshengzhihai'  # 图片路径
        self.m = 0  # 当前次数
        self.n = None  # 总次数
        self.flag_driver = False  # 是否为司机（默认否）
        self.flag_passenger = False  # 队员2就位
        self.flag_driver_start = False  # 司机待机
        self.flag_fighting = False  # 是否进行中对局（默认否）

    def title(self):
        """场景"""
        flag_title = True  # 场景提示
        while 1:
            if function.judge_scene(f'{self.picpath}/title.png', '[SCENE] 组队永生之海准备中'):
                self.flag_driver_start = True
                return True
            elif function.judge_scene(f'{self.picpath}/fighting.png', '[SCENE] 组队永生之海进行中'):
                self.flag_fighting = True
                return True
            elif flag_title:
                flag_title = False
                ms.text_print_update.emit('[WARN] 请检查游戏场景')

    def finish(self):
        """结算"""
        while 1:
            x, y = function.get_coor_info_picture(f'{self.picpath}/victory.png')
            if x != 0 and y != 0:
                ms.text_print_update.emit('结算中')
                break
        function.random_sleep(2, 4)
        x, y = function.random_finish_left_right(False)
        while 1:
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.25)
            pyautogui.doubleClick()
            if function.result():
                while 1:
                    function.random_sleep(1, 2)
                    pyautogui.click()
                    function.random_sleep(1, 2)
                    x, y = function.get_coor_info_picture('victory.png')
                    if x == 0 or y == 0:
                        break
                break
            function.random_sleep(0, 1)

    def run(self, n: int, flag_driver: bool = False):
        """
        :param n: 次数
        :param flag_driver: 是否司机（默认否）
        """
        x: int
        y: int
        self.flag_driver = flag_driver
        time.sleep(2)
        self.n = n
        if self.title():
            ms.text_num_update.emit(f'0/{self.n}')
            while self.m < self.n:
                self.flag_passenger = False
                # 司机
                if self.flag_driver and self.flag_driver_start:
                    ms.text_print_update.emit('等待队员')
                    # 队员就位
                    while 1:
                        x, y = function.get_coor_info_picture(f'{self.picpath}/passenger.png')
                        if x == 0 and y == 0:
                            self.flag_passenger = True
                            ms.text_print_update.emit('队员就位')
                            break
                    # 开始挑战
                    function.judge_click(f'{self.picpath}/tiaozhan.png')
                    ms.text_print_update.emit('开始')
                if not self.flag_fighting:
                    function.judge_click(f'{self.picpath}/fighting.png', False)
                    self.flag_fighting = False
                    ms.text_print_update.emit('对局进行中')
                self.finish()
                self.m += 1
                ms.text_num_update.emit(f'{self.m}/{self.n}')
                time.sleep(2)
        ms.text_print_update.emit(f'已完成 组队永生之海副本{self.m}次')
        # 启用按钮
        ms.is_fighting_update.emit(False)
