#!usr/bin/env python3
# baiguiyexing.py
"""
百鬼夜行
主界面功能5
"""

from . import window
from . import function

import pyautogui
import time
import random
import pathlib
from colorama import init, Fore, Back, Style

picpath = 'baiguiyexing'
'''图片路径'''
screenshotpath = 'cache_baiguiyexing'
'''截图路径'''

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

class baiguiyexing():
    """百鬼夜行"""
    def title(self):
        """场景"""
        x, y = function.get_coor_info_picture(f'{picpath}/title.png')
        if x != 0 and y != 0:
            print(Fore.GREEN + '场景：百鬼夜行')
            return True
        else:
            return False

    def start(self):
        """开始"""
        function.judge_click(f'{picpath}/jinru.png')

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
            x, y = function.random_coor(x1, x2, _y1, _y2)
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
            pyautogui.click()
            time.sleep(2)
            x, y = function.get_coor_info_picture(f'{picpath}/ya.png')
            if x != 0 and y != 0:
                print(Fore.GREEN + 'already choose')
                break
        function.judge_click(f'{picpath}/kaishi.png', dura=0.5)

    def fighting(self):
        """砸豆子"""
        n = 250  # 豆子数量
        time.sleep(2)
        while n > 0:
            function.random_sleep(0, 1)
            x, y = function.random_coor(60, window.absolute_window_width - 120, 300, window.absolute_window_height - 100)
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.25)
            pyautogui.click()
            n -= 5

    def finish(self):
        """结束"""
        while 1:
            x, y = function.get_coor_info_picture(f'{picpath}/baiguiqiyueshu.png')
            time.sleep(2)
            if x != 0 and y != 0:
                self.screenshot()
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                break

    def screenshot(self):
        """截图"""

        fpath = pathlib.Path.cwd()
        filepath = fpath / screenshotpath
        if not filepath.exists():
            filepath.mkdir()
        picname = f'{screenshotpath}./screenshot-{time.strftime("%Y%m%d%H%M%S")}.png'
        pyautogui.screenshot(imageFilename=picname, region=(window.window_left - 1, window.window_top, 1138, 679))


def Run_BaiGuiYeXing(n: int):
    """
    百鬼夜行主程序

    :param n: 次数
    """
    print('loading...')
    time.sleep(2)
    while n > 0:
        print(f'剩余{n}次')
        bgyx = baiguiyexing()
        if bgyx.title():
            time.sleep(1)
            function.random_sleep(0, 2)
            bgyx.start()
            function.random_sleep(1, 3)
            bgyx.choose()
            function.random_sleep(2, 4)
            bgyx.fighting()
            function.random_sleep(2, 4)
            bgyx.finish()
            n -= 1
            time.sleep(4)
    print('over')
