#!usr/bin/env python3
# function.py

'''
通用函数
'''

import window

import pyautogui
import random
import time
import string



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


# 图像识别
def GetCoorInfo_Picture(picname : str):
    filename : str = './/pic//' + picname
    try:
        button_location = pyautogui.locateOnScreen(filename, region = (window.window_left, window.window_top, window.window_width, window.window_height),  confidence = 0.8)
        # print(button_location)
        x, y = Coor_Random(button_location[0], button_location[0] + button_location[2], button_location[1], button_location[1] + button_location[3])
    except:
        x = y = 0
        # print(picname)
    return x, y


# 随机延时区间
def SleepRandom(m, n):
    m : int
    n : int
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # m-n (s)
    time.sleep(random.random() * (n - m) + m)


# 结果判断
def Result():
    while(1):
        x, y = GetCoorInfo_Picture('victory.png')
        if (x != 0 and y != 0):
            print('victory')
            result = 1
            break
        x, y = GetCoorInfo_Picture('fail.png')
        if (x != 0 and y != 0):
            print('fail')
            result = -1
            break
    return result


# 左侧可点击区域
finish_left_x1 = 20
finish_left_x2 = 260
# 右侧可点击区域
finish_right_x1 = 950
finish_right_x2 = 1100
# y轴
finish_y1 = 190
finish_y2 = 570

# 结束界面伪随机区域
def Finish_Random_Left_Right(a : string):
    x : int
    y : int
    if a == 'left':
        x, y = Coor_Random(finish_left_x1, finish_left_x2, finish_y1, finish_y2)
        return x, y
    elif a == 'right':
        x, y = Coor_Random(finish_right_x1, finish_right_x2, finish_y1, finish_y2)
        return x, y
