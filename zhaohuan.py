#!/usr/bin/env python3
# zhaohuan.py

"""
普通召唤
主界面功能2
"""

import function

import time
import pyautogui

picpath = 'zhaohuan'
'''图片路径'''

'''
普通召唤-破碎的符咒
putongzhaohuan.png
普通召唤-再次召唤
zaicizhaohuan.png
'''

# 召唤主程序
def Run_Zhaohuan(n: int):
    """召唤主程序"""
    print('loading...')
    time.sleep(1)
    if n == 1:
        while 1:
            x, y = function.GetCoorInfo_Picture(picpath, 'putongzhaohuan.png')
            if x != 0 and y != 0:
                pyautogui.moveTo(x, y, duration=0.25)
                pyautogui.click()
                break
        function.SleepRandom(4, 6)
    elif n > 1:
        while 1:
            x, y = function.GetCoorInfo_Picture(picpath, 'putongzhaohuan.png')
            if x != 0 and y != 0:
                pyautogui.moveTo(x, y, duration=0.25)
                pyautogui.click()
                break
        function.SleepRandom(4, 6)
        for i in range(1, n):
            while 1:
                x, y = function.GetCoorInfo_Picture(picpath, 'zaicizhaohuan.png')
                if x != 0 and y != 0:
                    pyautogui.moveTo(x, y, duration=0.25)
                    pyautogui.click()
                    break
            function.SleepRandom(4, 6)
    print('over')
