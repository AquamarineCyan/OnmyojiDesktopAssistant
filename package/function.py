#!usr/bin/env python3
# function.py
"""
通用函数库
"""

from . import window

import pyautogui
import random
import time
import pathlib
from colorama import init, Fore, Back, Style


def random_coor(x1: int, x2: int, y1: int, y2: int):
    """
    伪随机坐标，返回给定坐标区间的随机值

    :param x1: 左侧横坐标
    :param x2: 右侧横坐标
    :param y1: 顶部纵坐标
    :param y2: 底部纵坐标
    :return: 区域内随机值
    """
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


def get_coor_info_picture(pic: str):
    """
    图像识别，返回图像的全屏随机坐标

    :param pic: 文件路径&图像名称(*.png)
    :return: 识别成功，返回图像的随机坐标，识别失败，返回(0,0)
    """
    filename: str = fr'.\pic\{pic}'
    try:
        button_location = pyautogui.locateOnScreen(filename, region=(
            window.window_left, window.window_top, window.window_width, window.window_height), confidence=0.8)
        x, y = random_coor(button_location[0], button_location[0] + button_location[2], button_location[1],
                           button_location[1] + button_location[3])
    except:
        x = y = 0
    finally:
        return x, y


def judge_scene(pic: str, scenename: str = None):
    # scenename参数待删除
    """
    场景判断

    :param pic: 文件路径&图像名称(*.png)
    :param scenename: 场景名称（默认绿色）
    :return: True or False
    """
    while 1:
        x, y = get_coor_info_picture(pic)
        if x != 0 and y != 0:
            if scenename is not None:
                print(Fore.GREEN + f'场景：{scenename}')
            return True
        else:
            return False


def judge_click(pic: str, click: bool = True, dura: float = 0.5):
    """
    图像识别，并点击

    :param pic: 文件路径&图像名称(*.png)
    :param click: 是否点击（默认True）
    :param dura: 移动速度（默认0.25）
    :return: None
    """
    while 1:
        x, y = get_coor_info_picture(pic)
        if x != 0 and y != 0:
            if click:
                pyautogui.moveTo(x, y, duration=dura)
                pyautogui.click()
            break


def random_sleep(m: int, n: int):
    """
    随机延时区间m-n(s)

    :param m: 左区间（含）
    :param n: 右区间（不含）
    """
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    # m-n (s)
    time.sleep(random.random() * (n - m) + m)


class fighting:
    """战斗场景"""

    def ready(self):
        """准备"""
        judge_click('zhunbei.png')

    def finish(self):
        result()
        x, y = random_finish_left_right()


def result():
    """
    结果判断

    :return: True or False
    """
    while 1:
        x, y = get_coor_info_picture('victory.png')
        if x != 0 and y != 0:
            print('victory')
            return True
        x, y = get_coor_info_picture('fail.png')
        if x != 0 and y != 0:
            print('fail')
            return False


finish_left_x1 = 20
'''左侧可点击区域x1'''
finish_left_x2 = 240
'''左侧可点击区域x2'''
finish_right_x1 = 950
'''右侧可点击区域x1'''
finish_right_x2 = 1100
'''右侧可点击区域x2'''
finish_y1 = 190
'''可点击区域y1'''
finish_y2 = 570
'''可点击区域y2'''


def random_finish_left_right(click: bool = True):
    """
    结算界面伪随机点击区域，返回局部随机坐标，单击全局坐标

    :return: x: 横坐标
             y: 纵坐标
    """
    x: int
    y: int
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    if random.random() * 10 > 5:
        x, y = random_coor(finish_left_x1, finish_left_x2, finish_y1, finish_y2)
    else:
        x, y = random_coor(finish_right_x1, finish_right_x2, finish_y1, finish_y2)
    if click:
        pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
        pyautogui.click()
    return x, y
