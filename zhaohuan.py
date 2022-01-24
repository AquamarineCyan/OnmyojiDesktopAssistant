#!/usr/bin/env python3
# zhaohuan.py

'''
召唤界面
主界面功能2
'''

import window

import os
import time
import pyautogui
import random


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


# 图像识别
def GetCoorInfo_Picture(picname : str):
    timestart = time.time_ns()
    filename : str = './/pic//' + picname
    try:
        button_location = pyautogui.locateOnScreen(filename, region =(window.window_left, window.window_top, window.window_width, window.window_height))
    except:
        print('检测不到游戏窗口')
        x = y = 0
    else:
        # print(button_location)
        x, y = Coor_Random(button_location[0], button_location[0] + button_location[2], button_location[1],
                           button_location[1] + button_location[3])
    timeend = time.time_ns()
    print('time')
    print(timeend - timestart)
    return x, y


# 伪随机坐标
def Coor_Random(x1 : int, x2 : int, y1 : int, y2 : int):
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # x1-x2随机
    x = int(random.random() * (x2 - x1) + x1)
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # y1-y2随机
    y = int(random.random() * (y2 - y1) + y1)
    return x, y


# 随机延时区间
def SleepRandom(m, n):
    m : int
    n : int
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # m-n (s)
    time.sleep(random.random() * (n - m) + m)


# 程序运行
def Run_Zhaohuan(zhaohuan_n):
    print('ready to run')
    print('loading...')
    time.sleep(1)
    if (zhaohuan_n == 1):
        x, y = GetCoorInfo_Picture('putongzhaohuan_1.png')
        if (x != 0 and y != 0):
            print(x, y)
            pyautogui.moveTo(x, y, duration = 0.25)
            pyautogui.click()
        else:
            print('try again')
        SleepRandom(4, 6)
    elif (zhaohuan_n > 1):
        x, y = GetCoorInfo_Picture('putongzhaohuan_1.png')
        if (x != 0 and y != 0):
            print(x, y)
            pyautogui.moveTo(x, y, duration = 0.25)
            pyautogui.click()
        else:
            print('try again')
        SleepRandom(4, 6)
        for i in range(1, zhaohuan_n):
            x, y = GetCoorInfo_Picture('putongzhaohuan_2.png')
            if (x != 0 and y != 0):
                print(x, y)
                pyautogui.moveTo(x, y, duration = 0.25)
                pyautogui.click()
            else:
                print('try again')
            SleepRandom(4, 6)
    print('end')

'''
if __name__ == '__main__':
    window.GetInfo_Window()
    Run_Zhaohuan(zhaohuan_n = 10)
'''