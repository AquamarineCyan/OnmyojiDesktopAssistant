#!/usr/bin/env python3
# yuhun.py

'''
御魂界面
仅支持进行中的组队副本
'''
import string

'''
窗体x坐标:-7
窗体y坐标:0
窗体宽度:1154
窗体高度:687

(20,190)**********(260,190)##################(950,190)**********(1100,190)

(20,570)**********(260,570)##################(950,570)**********(1100,570)
'''

import window
import os
import time
import pyautogui
import random

'''
可点击区域
(20,190)**(260,190)#####(950,190)**(1100,190)
                   #####
                   #####
(20,570)**(260,570)#####(950,570)**(1100,570)
'''

# 绝对坐标
# 挑战开始按钮
yuhun_driver_x1 = 1045
yuhun_driver_x2 = 1120
yuhun_driver_y1 = 570
yuhun_driver_y2 = 640
# 左侧可点击区域
yuhun_left_x1 = 20
yuhun_left_x2 = 260
# 右侧可点击区域
yuhun_right_x1 = 950
yuhun_right_x2 = 1100
# y轴
yuhun_y1 = 190
yuhun_y2 = 570
# 相对坐标
relative_yuhun_left_x1 : int
relative_yuhun_left_x2 : int
relative_yuhun_right_x1 : int
relative_yuhun_right_x2 : int
relative_yuhun_y1 : int
relative_yuhun_y2 : int
relative_yuhun_driver_x1 : int
relative_yuhun_driver_x2 : int
relative_yuhun_driver_y1 : int
relative_yuhun_driver_y2 : int

stra : str
strb : str


# 御魂副本次数
yuhun_n = 0
# 御魂副本时长
yuhun_time : int
# 是否为司机（默认否）
flag_driver = 0
# 获取当前目录的父目录
fpath = os.getcwd()
# 保护措施，避免失控
pyautogui.FAILSAFE = True
# 为所有的PyAutoGUI函数增加延迟。默认延迟时间是0.1秒。
pyautogui.PAUSE = 0.5


# 伪随机坐标
def Yuhun_Random(x1 : int, x2 : int, y1 : int, y2 : int):
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # x1-x2随机
    x = int(random.random() * (x2 - x1) + x1)
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # y1-y2随机
    y = int(random.random() * (y2 - y1) + y1)
    return x, y

# 伪随机区域
def Yuhun_Random_Left_Right_Driver(a : string):
    x : int
    y : int
    if a == 'left':
        x, y = Yuhun_Random(relative_yuhun_left_x1, relative_yuhun_left_x2, relative_yuhun_y1, relative_yuhun_y2)
        return x, y
    elif a == 'right':
        x, y = Yuhun_Random(relative_yuhun_right_x1, relative_yuhun_right_x2, relative_yuhun_y1, relative_yuhun_y2)
        return x, y
    elif a == 'driver':
        x, y = Yuhun_Random(relative_yuhun_driver_x1, relative_yuhun_driver_x2, relative_yuhun_driver_y1, relative_yuhun_driver_y2)
        return x, y


# 获取御魂副本界面的可点击区域的相对位置坐标
def GetRelativeInfo_Yuhun():
    global relative_yuhun_left_x1
    global relative_yuhun_left_x2
    global relative_yuhun_right_x1
    global relative_yuhun_right_x2
    global relative_yuhun_y1
    global relative_yuhun_y2
    global relative_yuhun_driver_x1
    global relative_yuhun_driver_x2
    global relative_yuhun_driver_y1
    global relative_yuhun_driver_y2
    relative_yuhun_left_x1 = int(window.window_width * yuhun_left_x1 / window.absolute_window_width)
    relative_yuhun_left_x2 = int(window.window_width * yuhun_left_x2 / window.absolute_window_width)
    relative_yuhun_right_x1 = int(window.window_width * yuhun_right_x1 / window.absolute_window_width)
    relative_yuhun_right_x2 = int(window.window_width * yuhun_right_x2 / window.absolute_window_width)
    relative_yuhun_y1 = int(window.window_height * yuhun_y1 / window.absolute_window_height)
    relative_yuhun_y2 = int(window.window_height * yuhun_y2 / window.absolute_window_height)
    relative_yuhun_driver_x1 = int(window.window_width * yuhun_driver_x1 / window.absolute_window_width)
    relative_yuhun_driver_x2 = int(window.window_width * yuhun_driver_x2 / window.absolute_window_width)
    relative_yuhun_driver_y1 = int(window.window_height * yuhun_driver_y1 / window.absolute_window_height)
    relative_yuhun_driver_y2 = int(window.window_height * yuhun_driver_y2 / window.absolute_window_height)


# 随机延时区间
def SleepRandom(m, n):
    m : int
    n : int
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # m-n (s)
    time.sleep(random.random() * (n - m) + m)


def Run_Yuhun(yuhun_n : int, yuhun_time : int, flag_driver : int):
    global stra
    global strb
    x : int
    y : int
    GetRelativeInfo_Yuhun()
    while(yuhun_n > 0):
        print('剩余' + str(yuhun_n) + '次')
        if(flag_driver):
            # 等待队友
            SleepRandom(3, 4)
            x, y = Yuhun_Random_Left_Right_Driver('driver')
            pyautogui.click(x + window.window_x, y + window.window_y)
            print(x + window.window_x, y + window.window_y)
        # 转场
        SleepRandom(2, 3)
        time.sleep(yuhun_time)
        time.sleep(2)
        # 转场
        SleepRandom(2, 3)
        # 结束界面点击
        if(yuhun_n % 2 == 0):
            stra = 'left'
            strb = 'right'
        else:
            stra = 'right'
            strb = 'left'
        x, y = Yuhun_Random_Left_Right_Driver(stra)
        pyautogui.doubleClick(x + window.window_x, y + window.window_y)
        print(x + window.window_x, y + window.window_y)
        SleepRandom(4, 6)
        x, y = Yuhun_Random_Left_Right_Driver(strb)
        pyautogui.click(x + window.window_x, y + window.window_y)
        print(x + window.window_x, y + window.window_y)
        # 转场
        SleepRandom(3, 4)
        yuhun_n -= 1


'''
if __name__ == '__main__':
    window.GetInfo_window()
    Run_Yuhun(4, 17, 0)
'''