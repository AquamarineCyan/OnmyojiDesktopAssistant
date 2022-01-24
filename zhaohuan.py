#!/usr/bin/env python3
# zhaohuan.py

'''
召唤界面
'''


import window
import mouse

import os
import time
import pyautogui
import random


# 相对坐标
# 第一个按钮-普通召唤
relative_zhaohuan_1_x = 0.2339688041594454
relative_zhaohuan_1_y = 0.8864628820960698
# 第二个按钮-再次召唤
relative_zhaohuan_2_x = 0.5979202772963604
relative_zhaohuan_2_y = 0.8893740902474527
# 第一个按钮-普通召唤
relative_zhaohuan_1_x1 = 0.0
relative_zhaohuan_1_x2 = 0.0
relative_zhaohuan_1_y1 = 0.0
relative_zhaohuan_1_y2 = 0.0
# 第二个按钮-再次召唤
relative_zhaohuan_2_x1 = 0.0
relative_zhaohuan_2_x2 = 0.0
relative_zhaohuan_2_y1 = 0.0
relative_zhaohuan_2_y2 = 0.0


# 召唤次数（默认十连）
zhaohuan_n = 0
# 获取当前目录的父目录
fpath = os.getcwd()
# 保护措施，避免失控
pyautogui.FAILSAFE = True
# 为所有的PyAutoGUI函数增加延迟。默认延迟时间是0.1秒。
pyautogui.PAUSE = 0.5


# 获取召唤界面的按钮相对位置坐标
def GetRelativeInfo_Zhaohuan():
    mouse_x, mouse_y = mouse.GetInfo_Mouse()
    global relative_zhaohuan_1_x
    global relative_zhaohuan_1_y
    global relative_zhaohuan_2_x
    global relative_zhaohuan_2_y
    # relative_zhaohuan_1_x = (mouse_x - window_x) / window_Width
    # relative_zhaohuan_1_y = (mouse_y - window_y) / window_Height
    # print(relative_zhaohuan_1_x, relative_zhaohuan_1_y)
    relative_zhaohuan_2_x = (mouse_x - window.window_x) / window.window_width
    relative_zhaohuan_2_y = (mouse_y - window.window_y) / window.window_height
    print(relative_zhaohuan_2_x, relative_zhaohuan_2_y)



# 随机延时区间
def SleepRandom(m, n):
    m : int
    n : int
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # m-n (s)
    time.sleep(random.random() * (n - m) + m)


# 修改配置文件
def WriteConfig():
    f = open(fpath + '\config.txt', 'a')
    f.write(str(relative_zhaohuan_1_x) + '\n')
    f.write(str(relative_zhaohuan_1_y) + '\n')
    f.close()


# 程序运行
def Run_Zhaohuan(zhaohuan_n):
    if (zhaohuan_n == 1):
        x = int((relative_zhaohuan_1_x * window.window_width) + window.window_x)
        y = int((relative_zhaohuan_1_y * window.window_height) + window.window_y)
        pyautogui.click(x, y)
        print(x, y)
        SleepRandom(4, 6)
    elif (zhaohuan_n > 1):
        x = int((relative_zhaohuan_1_x * window.window_width) + window.window_x)
        y = int((relative_zhaohuan_1_y * window.window_height) + window.window_y)
        pyautogui.click(x, y)
        print(x, y)
        SleepRandom(4, 6)
        x = int((relative_zhaohuan_2_x * window.window_width) + window.window_x)
        y = int((relative_zhaohuan_2_y * window.window_height) + window.window_y)
        for i in range(1, zhaohuan_n):
            pyautogui.click(x, y)
            print(x, y)
            SleepRandom(4, 6)
    print('end')

