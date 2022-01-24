#!/usr/bin/env python3
# yuhun.py

'''
御魂界面
仅支持进行中的组队副本
主界面功能1
'''

import window

import os
import time
import pyautogui
import random
import string


'''
御魂副本第1个按钮-结束界面的’鼓‘
yuhun_victory.png
御魂副本第2个按钮-结束界面的’达摩‘
yuhun_egg.png
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
# 是否进行中对局（默认否）
flag_fighting = 0
# 获取当前目录的父目录
fpath = os.getcwd()
# 保护措施，避免失控
pyautogui.FAILSAFE = True
# 为所有的PyAutoGUI函数增加延迟。默认延迟时间是0.1秒。
pyautogui.PAUSE = 0.5


# 图像识别
def GetCoorInfo_Picture(picname : str):
    filename : str = './/pic//' + picname
    try:
        button_location = pyautogui.locateOnScreen(filename, region =(window.window_left, window.window_top, window.window_width, window.window_height))
        # print(button_location)
        x, y = Coor_Random(button_location[0], button_location[0] + button_location[2], button_location[1],
                           button_location[1] + button_location[3])
        # print('true')
    except:
        x = y = 0
        # print(picname)
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


# 伪随机区域
def Yuhun_Random_Left_Right_Driver(a : string):
    x : int
    y : int
    if a == 'left':
        x, y = Coor_Random(relative_yuhun_left_x1, relative_yuhun_left_x2, relative_yuhun_y1, relative_yuhun_y2)
        return x, y
    elif a == 'right':
        x, y = Coor_Random(relative_yuhun_right_x1, relative_yuhun_right_x2, relative_yuhun_y1, relative_yuhun_y2)
        return x, y
    elif a == 'driver':
        x, y = Coor_Random(relative_yuhun_driver_x1, relative_yuhun_driver_x2, relative_yuhun_driver_y1, relative_yuhun_driver_y2)
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


def Run_Yuhun(yuhun_n : int, flag_driver : int = 0):
    global stra
    global strb
    global flag_fighting
    x : int
    y : int
    GetRelativeInfo_Yuhun()
    while(yuhun_n > 0):
        flag_fighting = 0
        while(1):
            x, y = GetCoorInfo_Picture('yuhun_zudui.png')
            if(x != 0 and y != 0):
                print('当前为组队界面')
                break
            x, y = GetCoorInfo_Picture('yuhun_fighting.png')
            if (x != 0 and y != 0):
                flag_fighting = 1
                print('对局进行中...')
                break
        if(x != 0 and y != 0):
            print('剩余' + str(yuhun_n) + '次')
            # 司机
            if(flag_driver):
                '''print('waitng for passengers...')
                SleepRandom(3, 4)
                x, y = Yuhun_Random_Left_Right_Driver('driver')
                pyautogui.click(x + window.window_left, y + window.window_top)
                print(x + window.window_left, y + window.window_top)'''
            if(flag_fighting == 0):
                while (1):
                    x, y = GetCoorInfo_Picture('yuhun_fighting.png')
                    if (x != 0 and y != 0):
                        flag_fighting = 0
                        print('对局进行中...')
                        break
            # 转场
            print('sleep for 10s')
            time.sleep(10)
            while (1):
                x, y = GetCoorInfo_Picture('yuhun_victory.png')
                if (x != 0 and y != 0):
                    print('victory!')
                    break
            # time.sleep(yuhun_time)
            # time.sleep(2)
            # 转场
            # SleepRandom(2, 3)
            # 结束界面点击
            if(yuhun_n % 2 == 0):
                stra = 'left'
                strb = 'right'
            else:
                stra = 'right'
                strb = 'left'
            x, y = Yuhun_Random_Left_Right_Driver(stra)
            pyautogui.doubleClick(x + window.window_left, y + window.window_top)
            print(x + window.window_left, y + window.window_top)
            while (1):
                x, y = GetCoorInfo_Picture('yuhun_finish.png')
                if (x != 0 and y != 0):
                    print('finish')
                    break
            time.sleep(1)
            x, y = Yuhun_Random_Left_Right_Driver(strb)
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration = 0.25)
            pyautogui.click()
            print(x + window.window_left, y + window.window_top)
            while (1):
                x, y = GetCoorInfo_Picture('yuhun_zudui.png')
                if (x == 0 and y == 0):
                    x, y = Yuhun_Random_Left_Right_Driver(strb)
                    pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.25)
                    pyautogui.click()
                    print(x + window.window_left, y + window.window_top)
                else:
                    break
            # 转场
            time.sleep(1)
            yuhun_n -= 1


'''
if __name__ == '__main__':
    window.GetInfo_Window()
    Run_Yuhun(4)
'''