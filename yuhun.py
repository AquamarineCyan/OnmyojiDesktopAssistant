#!/usr/bin/env python3
# yuhun.py

'''
御魂界面
仅支持进行中的组队副本
主界面功能1
'''

import function
import window

import os
from time import sleep
import pyautogui
import string


'''
组队界面
yuhun_zudui.png
司机挑战按钮
yuhun_tiaozhan.png
队员2
yuhun_passenger_2.png
队员3
yuhun_passenger_3.png
对局进行中
yuhun_fighting.png
御魂副本结算按钮
yuhun_victory.png
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
# 组队人数
flag_passengers : int
# 队员2就位
flag_passenger_2 : int
# 队员3就位
flag_passenger_3 : int
# 是否进行中对局（默认否）
flag_fighting = 0
# 获取当前目录的父目录
fpath = os.getcwd()
# 保护措施，避免失控
pyautogui.FAILSAFE = True
# 为所有的PyAutoGUI函数增加延迟。默认延迟时间是0.1秒。
pyautogui.PAUSE = 0.5


# 伪随机区域
def Yuhun_Random_Left_Right_Driver(a : string):
    x : int
    y : int
    if a == 'left':
        x, y = function.Coor_Random(relative_yuhun_left_x1, relative_yuhun_left_x2, relative_yuhun_y1, relative_yuhun_y2)
        return x, y
    elif a == 'right':
        x, y = function.Coor_Random(relative_yuhun_right_x1, relative_yuhun_right_x2, relative_yuhun_y1, relative_yuhun_y2)
        return x, y
    elif a == 'driver':
        x, y = function.Coor_Random(relative_yuhun_driver_x1, relative_yuhun_driver_x2, relative_yuhun_driver_y1, relative_yuhun_driver_y2)
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



def Run_Yuhun(yuhun_n : int, flag_driver : int = 0, flag_passengers : int = 2):
    global stra, strb
    global flag_fighting
    global flag_driver_start
    global flag_passenger_2, flag_passenger_3
    x : int
    y : int
    GetRelativeInfo_Yuhun()
    while(yuhun_n > 0):
        flag_fighting = 0
        flag_driver_start = 0
        while(1):
            x, y = function.GetCoorInfo_Picture('yuhun_zudui.png')
            if(x != 0 and y != 0):
                flag_driver_start = 1
                print('当前为组队界面')
                break
            x, y = function.GetCoorInfo_Picture('yuhun_fighting.png')
            if (x != 0 and y != 0):
                flag_fighting = 1
                print('对局进行中...')
                break
        if(x != 0 and y != 0):
            print('剩余' + str(yuhun_n) + '次')
            # 司机
            if(flag_driver_start and flag_driver):
                print('waitng for passengers...')
                # 队员2就位
                while(1):
                    x, y = function.GetCoorInfo_Picture('yuhun_passenger_2.png')
                    if (x == 0 and y == 0):
                        flag_passenger_2 = 1
                        print('passenger 2 is already')
                        break
                # 是否3人组队
                if(flag_passengers == 3):
                    while(1):
                        x, y = function.GetCoorInfo_Picture('yuhun_passenger_3.png')
                        if (x == 0 and y == 0):
                            flag_passenger_3 = 1
                            print('passenger 3 is already')
                            break
                # 挑战开始
                while(1):
                    x, y = function.GetCoorInfo_Picture('yuhun_tiaozhan.png')
                    if (x != 0 and y != 0):
                        pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.25)
                        pyautogui.click()
                        print(x + window.window_left, y + window.window_top)
                        print('start')
            if(flag_fighting == 0):
                while (1):
                    x, y = function.GetCoorInfo_Picture('yuhun_fighting.png')
                    if (x != 0 and y != 0):
                        flag_fighting = 0
                        print('对局进行中...')
                        break
            # 转场
            print('sleep for 8s')
            sleep(8)
            while (1):
                x, y = function.GetCoorInfo_Picture('yuhun_victory.png')
                if (x != 0 and y != 0):
                    print('victory!')
                    break
            # 结束界面
            if(yuhun_n % 2 == 0):
                stra = 'left'
                strb = 'right'
            else:
                stra = 'right'
                strb = 'left'
            x, y = Yuhun_Random_Left_Right_Driver(stra)
            pyautogui.moveTo(x + window.window_left, y + window.window_top)
            pyautogui.doubleClick()
            print(x + window.window_left, y + window.window_top)
            '''
            while (1):
                x, y = GetCoorInfo_Picture('yuhun_finish.png')
                if (x != 0 and y != 0):
                    print('finish')
                    break
                else:
                    print('yuhun_finish.png')
            '''
            sleep(1)
            x, y = Yuhun_Random_Left_Right_Driver(strb)
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration = 0.25)
            pyautogui.click()
            print(x + window.window_left, y + window.window_top)
            while (1):
                x, y = function.GetCoorInfo_Picture('yuhun_zudui.png')
                if (x == 0 and y == 0):
                    x, y = Yuhun_Random_Left_Right_Driver(strb)
                    pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.25)
                    pyautogui.click()
                    print(x + window.window_left, y + window.window_top)
                    sleep(0.5)
                else:
                    break
            # 转场
            sleep(1)
            yuhun_n -= 1


'''
if __name__ == '__main__':
    window.GetInfo_Window()
    Run_Yuhun(50)
'''