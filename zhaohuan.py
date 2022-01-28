#!/usr/bin/env python3
# zhaohuan.py

'''
召唤界面
主界面功能2
'''

import function

import os
import time
import pyautogui


'''
普通召唤第1个按钮-普通召唤
putongzhaohuan_1.png
普通召唤第2个按钮-再次召唤
putongzhaohuan_2.png
'''


# 召唤次数（默认十连）
zhaohuan_n : int
# 获取当前目录的父目录
fpath = os.getcwd()
# 保护措施，避免失控
pyautogui.FAILSAFE = True
# 为所有的PyAutoGUI函数增加延迟。默认延迟时间是0.1秒。
pyautogui.PAUSE = 0.5


# 程序运行
def Run_Zhaohuan(zhaohuan_n):
    print('ready to run')
    print('loading...')
    time.sleep(1)
    if (zhaohuan_n == 1):
        x, y = function.GetCoorInfo_Picture('putongzhaohuan_1.png')
        if (x != 0 and y != 0):
            print(x, y)
            pyautogui.moveTo(x, y, duration = 0.25)
            pyautogui.click()
        else:
            print('try again')
        function.SleepRandom(4, 6)
    elif (zhaohuan_n > 1):
        x, y = function.GetCoorInfo_Picture('putongzhaohuan_1.png')
        if (x != 0 and y != 0):
            print(x, y)
            pyautogui.moveTo(x, y, duration = 0.25)
            pyautogui.click()
        else:
            print('try again')
        function.SleepRandom(4, 6)
        for i in range(1, zhaohuan_n):
            x, y = function.GetCoorInfo_Picture('putongzhaohuan_2.png')
            if (x != 0 and y != 0):
                print(x, y)
                pyautogui.moveTo(x, y, duration = 0.25)
                pyautogui.click()
            else:
                print('try again')
            function.SleepRandom(4, 6)
    print('end')


'''
if __name__ == '__main__':
    window.GetInfo_Window()
    Run_Zhaohuan(zhaohuan_n = 10)
'''