#!/usr/bin/env python3
# yuhun.py
"""
组队御魂副本
仅支持进行中的组队副本
主界面功能1
"""
from . import function
from . import window

import time
import pyautogui

picpath = 'yuhun'
'''图片路径'''

'''
组队界面-协战队伍
xiezhanduiwu.png
挑战按钮
tiaozhan.png
队员2
passenger_2.png
队员3
passenger_3.png
对局进行中
fighting.png
御魂副本结算按钮
yuhun_victory.png
'''

# 绝对坐标
'''# 挑战开始按钮
yuhun_driver_x1 = 1045
yuhun_driver_x2 = 1120
yuhun_driver_y1 = 570
yuhun_driver_y2 = 640'''
# 左侧可点击区域
yuhun_left_x1 = 20
'''左侧可点击区域x1'''
yuhun_left_x2 = 260
'''左侧可点击区域x2'''
# 右侧可点击区域
yuhun_right_x1 = 950
'''右侧可点击区域x1'''
yuhun_right_x2 = 1100
'''右侧可点击区域x2'''
# y轴
yuhun_y1 = 190
'''可点击区域y1'''
yuhun_y2 = 570
'''可点击区域y2'''
# 相对坐标
relative_yuhun_left_x1: int
relative_yuhun_left_x2: int
relative_yuhun_right_x1: int
relative_yuhun_right_x2: int
relative_yuhun_y1: int
relative_yuhun_y2: int

flag_driver = False
'''是否为司机（默认否）'''
flag_passengers: int
'''组队人数'''
flag_passenger_2: bool
'''队员2就位'''
flag_passenger_3: bool
'''队员3就位'''
flag_driver_start: bool
'''司机待机'''
flag_fighting = False
'''是否进行中对局（默认否）'''


class yuhun:
    """组队御魂副本"""

    def scene(self):
        """
        场景

        :return: True->御魂组队 False->进行中对局
        """
        while 1:
            x, y = function.get_coor_info_picture(f'{picpath}/xiezhanduiwu.png')
            if x != 0 and y != 0:
                flag_driver_start = 1
                print('场景：御魂组队')
                return True
            x, y = function.get_coor_info_picture(f'{picpath}/fighting.png')
            if x != 0 and y != 0:
                flag_fighting = True
                print('场景：进行中对局')
                return False

    def finish(self):
        """结算"""
        while 1:
            x, y = function.get_coor_info_picture(f'{picpath}/yuhun_victory.png')
            if x != 0 and y != 0:
                print('finish')
                break
        function.random_sleep(3, 5)
        x, y = function.random_finish_left_right(False)
        while 1:
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.25)
            pyautogui.doubleClick()
            if function.result():
                while 1:
                    function.random_sleep(1, 2)
                    pyautogui.click()
                    function.random_sleep(1, 2)
                    x, y = function.get_coor_info_picture('victory.png')
                    if x == 0 or y == 0:
                        break
                break
            function.random_sleep(0, 1)


def run_yuhun(n: int, flag_driver: bool = False, flag_passengers: int = 2):
    """
    御魂副本主程序

    :param n: 次数
    :param flag_driver: 是否司机（默认否）
    :param flag_passengers: 人数（默认2人）
    :return:None
    """
    global flag_fighting
    global flag_driver_start
    global flag_passenger_2, flag_passenger_3
    x: int
    y: int
    time.sleep(2)
    yh = yuhun()
    while n > 0:
        flag_fighting = False
        flag_driver_start = False
        if yh.scene():
            flag_driver_start = True
            print('场景：御魂组队')
        else:
            flag_fighting = True
            print('场景：进行中对局')
        print(f'剩余{n}次')
        # 司机
        if flag_driver_start and flag_driver:
            print('waitng for passengers')
            # 队员2就位
            while 1:
                x, y = function.get_coor_info_picture(f'{picpath}/passenger_2.png')
                if x == 0 and y == 0:
                    flag_passenger_2 = True
                    print('passenger 2 is already')
                    break
            # 是否3人组队
            if flag_passengers == 3:
                while 1:
                    x, y = function.get_coor_info_picture(f'{picpath}/passenger_3.png')
                    if x == 0 and y == 0:
                        flag_passenger_3 = True
                        print('passenger 3 is already')
                        break
            # start
            while 1:
                x, y = function.get_coor_info_picture(f'{picpath}/tiaozhan.png')
                if x != 0 and y != 0:
                    pyautogui.moveTo(x, y, duration=0.25)
                    pyautogui.click()
                    print('start')
        if not flag_fighting:
            while 1:
                x, y = function.get_coor_info_picture(f'{picpath}/fighting.png')
                if x != 0 and y != 0:
                    flag_fighting = False
                    print('对局进行中...')
                    break
        yh.finish()
        n -= 1
        time.sleep(2)
    print('over')
