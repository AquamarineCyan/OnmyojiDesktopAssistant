#!/usr/bin/env python3
# yuling.py
"""
御灵场景
主界面功能7
"""

from . import window
from . import function

import time
import pyautogui
from colorama import Fore

picpath = 'yuling'
'''图片路径'''

'''
御灵场景
title.png
挑战
tiaozhan.png
'''

class yuling():
    """御灵"""

    def title(self):
        """场景"""
        return function.judge_scene(f'{picpath}/title.png', '御灵')

    def start(self):
        """挑战开始"""
        function.judge_click(f'{picpath}/tiaozhan.png')


def run_yuling(n: int):
    """
    御灵主程序

    :param n: 次数
    """
    print('loading...')
    time.sleep(2)
    flag_title = True  # 场景提示
    yl = yuling()
    while 1:
        if yl.title():
            while n > 0:
                print(f'剩余{n}次')
                time.sleep(1)
                function.random_sleep(0, 1)
                yl.start()
                time.sleep(8)
                function.result()
                time.sleep(1)
                x, y = function.random_finish_left_right()
                pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
                pyautogui.click()
                function.random_sleep(1,3)
                n -= 1
            break
        elif flag_title:
            flag_title = False
            print(Fore.RED + '请检查游戏场景')
    print(Fore.RED + 'over')