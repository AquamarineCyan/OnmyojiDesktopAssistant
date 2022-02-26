#!usr/bin/env python3
# function.py

"""
通用函数库
"""

import window

import pyautogui
import random
import time


# 伪随机坐标，返回给定坐标区间的随机值
def Coor_Random(x1: int, x2: int, y1: int, y2: int):
    """伪随机坐标，返回给定坐标区间的随机值"""
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # x1-x2随机
    x = int(random.random() * (x2 - x1) + x1)
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # y1-y2随机
    y = int(random.random() * (y2 - y1) + y1)
    # 返回随机值
    return x, y


# 图像识别，返回图像的全屏随机坐标
def GetCoorInfo_Picture(picpath: str = '', picname: str = ''):
    """
    图像识别，返回图像的全屏随机坐标
    识别成功，返回图像的随机坐标
    识别失败，返回(0,0)
    """
    if '.png' in picpath:
        picname = picpath
        picpath = ''
    filename: str = './/pic//' + picpath + '//' + picname
    try:
        button_location = pyautogui.locateOnScreen(filename, region=(
        window.window_left, window.window_top, window.window_width, window.window_height), confidence=0.8)
        # print(button_location)
        x, y = Coor_Random(button_location[0], button_location[0] + button_location[2], button_location[1], button_location[1] + button_location[3])
    except:
        x = y = 0
        # print(picname)
    return x, y


# 随机延时区间
def SleepRandom(m, n):
    """随机延时区间"""
    m: int
    n: int
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # m-n (s)
    time.sleep(random.random() * (n - m) + m)


# 结果判断，返回胜利或者失败结果
def Result():
    """
    结果判断，返回胜利或者失败结果
    胜利，返回1
    失败，返回-1
    """
    while 1:
        x, y = GetCoorInfo_Picture('', 'victory.png')
        if x != 0 and y != 0:
            print('victory')
            result = 1
            break
        x, y = GetCoorInfo_Picture('', 'fail.png')
        if x != 0 and y != 0:
            print('fail')
            result = -1
            break
    return result


# 左侧可点击区域
finish_left_x1 = 20
'''左侧可点击区域x1'''
finish_left_x2 = 260
'''左侧可点击区域x2'''
# 右侧可点击区域
finish_right_x1 = 950
'''右侧可点击区域x1'''
finish_right_x2 = 1100
'''右侧可点击区域x2'''
# y轴
finish_y1 = 190
'''可点击区域y1'''
finish_y2 = 570
'''可点击区域y2'''


# 结算界面伪随机点击区域，返回局部随机坐标
def Finish_Random_Left_Right():
    """结算界面伪随机点击区域，返回局部随机坐标"""
    x: int
    y: int
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    if random.random() * 10 > 5:
        x, y = Coor_Random(finish_left_x1, finish_left_x2, finish_y1, finish_y2)
        return x, y
    else:
        x, y = Coor_Random(finish_right_x1, finish_right_x2, finish_y1, finish_y2)
        return x, y
