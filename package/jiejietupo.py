#!/usr/bin/env python3
# jiejietupo.py
"""
结界突破场景
主界面功能3、4
"""

from . import window
from . import function

import time
import pyautogui
from colorama import Fore

picpath = 'jiejietupo'
'''图片路径'''

'''
突破界面
title.png
个人突破
geren.png
阴阳寮按钮
yinyangliao.png
攻破图标
victory.png
失败图标
fail.png
防守记录（个人突破）
fangshoujilu.png
突破记录（阴阳寮突破）
yinyangliao.png
'''

def get_coor_info_picture_tupo(x1, y1, pic: str):
    """
    图像识别，返回图像的局部相对坐标

    :param x1: 识别区域左侧横坐标
    :param y1: 识别区域顶部纵坐标
    :param picname: 图像名称
    :return: x, y
    """
    filename: str = fr'.\pic\{picpath}\{pic}'
    if 'xunzhang' in pic:
        # 个人突破
        try:
            button_location = pyautogui.locateOnScreen(filename, region=(x1 + window.window_left - 25, y1 + window.window_top + 40, 185 + 20, 90 - 20), confidence=0.9)
            x, y = function.random_coor(button_location[0], button_location[0] + button_location[2], button_location[1], button_location[1] + button_location[3])
        except:
            x = y = 0
    else:
        # 阴阳寮突破
        try:
            button_location = pyautogui.locateOnScreen(filename, region=(x1 + window.window_left, y1 - 40 + window.window_top, 185 + 40, 90), confidence=0.8)
            x, y = function.random_coor(button_location[0], button_location[0] + button_location[2], button_location[1], button_location[1] + button_location[3])
        except:
            x = y = 0
    return x, y


def fighting_tupo(x0, y0):
    """
    结界突破战斗

    :param x0: 左侧横坐标
    :param y0: 顶部纵坐标
    :return: None
    """
    x, y = function.random_coor(x0, x0 + 185, y0, y0 + 80)
    pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
    pyautogui.click()
    while 1:
        x, y = function.get_coor_info_picture(f'{picpath}/jingong.png')
        if x != 0 and y != 0:
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click()
            break


def list_num_xunzhang():
    """
    创建列表，返回每个结界的勋章数

    :return: 勋章个数列表
    """
    alist = [0]
    for i in range(1, 10):
        x5, y5 = get_coor_info_picture_tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_5.png')
        x4, y4 = get_coor_info_picture_tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_4.png')
        x3, y3 = get_coor_info_picture_tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_3.png')
        x2, y2 = get_coor_info_picture_tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_2.png')
        x1, y1 = get_coor_info_picture_tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_1.png')
        x0, y0 = get_coor_info_picture_tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_0.png')
        if x5 != 0 and y5 != 0:
            alist.append(5)
            continue
        if x4 != 0 and y4 != 0:
            alist.append(4)
            continue
        if x3 != 0 and y3 != 0:
            alist.append(3)
            continue
        if x2 != 0 and y2 != 0:
            alist.append(2)
            continue
        if x1 != 0 and y1 != 0:
            alist.append(1)
            continue
        if x0 != 0 and y0 != 0:
            alist.append(0)
            continue
        if x0 == 0 and x1 == 0 and x2 == 0 and x4 == 0 and x5 == 0:
            print(i, '已攻破')
            alist.append(-1)
    '''
    for i in range (5, -1, -1):
        if i == 0:
            print(i, '勋章', alist.count(i) - 1, '个')
        else:
            print(i, '勋章', alist.count(i), '个')
    '''
    return alist

'''
个人突破相对坐标
宽185
高90
间隔宽115
间隔高30
'''

tupo_geren_x = {
    1: 215,
    2: 515,
    3: 815,
}
tupo_geren_y = {
    1: 175,
    2: 295,
    3: 415
}

def run_tupo_geren(n: int):
    """个人突破主程序"""
    print('loading...')
    time.sleep(2)
    function.judge_scene(f'{picpath}/title.png', '结界突破')
    time.sleep(2)
    while 1:
        if function.judge_scene(f'{picpath}/fangshoujilu.png', '个人突破'):
            break
        else:
            function.judge_click(f'{picpath}/geren.png')
            time.sleep(4)
    time.sleep(2)
    while n != 0:
        print(f'剩余次数：{n}')
        list_xunzhang = list_num_xunzhang()
        # 打法 胜3刷新
        tupo_victory = list_xunzhang.count(-1)
        if tupo_victory == 3:
            print('已攻破3次，等待刷新')
            function.random_sleep(3, 6)
            function.judge_click(f'{picpath}/shuaxin.png')
            function.random_sleep(2, 4)
            function.judge_click(f'{picpath}/queding.png')
            print(Fore.GREEN + 'waiting for refresh')
            function.random_sleep(2, 4)
        elif tupo_victory < 3:
            print('已攻破', tupo_victory, '个')
            for i in range(5, -1, -1):
                if list_xunzhang.count(i):
                    k = 1
                    for j in range(1, list_xunzhang.count(i) + 1):
                        k = list_xunzhang.index(i, k)
                        print(k, 'need fight')
                        x, y = get_coor_info_picture_tupo(tupo_geren_x[(k + 2) % 3 + 1], tupo_geren_y[(k + 2) // 3], 'fail.png')
                        if x != 0 and y != 0:
                            print(k, 'fail')
                            k += 1
                            continue
                        fighting_tupo(tupo_geren_x[(k + 2) % 3 + 1], tupo_geren_y[(k + 2) // 3])
                        if function.result():
                            n -= 1
                            flag_victory = True
                        else:
                            flag_victory = False
                        time.sleep(1)
                        # 结束界面
                        x, y = function.random_finish_left_right()
                        pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
                        pyautogui.click()
                        time.sleep(2)
                        # 3胜奖励
                        if tupo_victory == 2 and flag_victory:
                            time.sleep(2)
                            while 1:
                                function.judge_click('victory.png')
                                function.random_sleep(1, 2)
                                x, y = function.get_coor_info_picture('victory.png')
                                if x == 0 or y == 0:
                                    break
                            print('victory for 3 times')
                        time.sleep(3)
                        break
        elif tupo_victory > 3:
            print(Fore.RED + '暂不支持大于3个，请自行处理')
            break
        time.sleep(3)
    print('over')

'''
阴阳寮突破相对坐标
宽185
高90
间隔宽115
间隔高40
'''

tupo_yinyangliao_x = {
    1: 460,
    2: 760
}
tupo_yinyangliao_y = {
    1: 170,
    2: 300,
    3: 430,
    4: 560
}

class jiejietupo_yinyangliao():
    """阴阳寮突破"""
    def title(self):
        """界面"""
        return function.judge_scene(f'{picpath}/tupojilu.png', '场景：阴阳寮突破')

    def jibaicishu(self):
        """剩余次数判断"""
        # 无法生效，待废除，或使用OpenCv
        if self.title():
            while 1:
                try:
                    button_location = pyautogui.locateOnScreen(f'./pic/{picpath}/jibaicishu.png', region=(window.window_left, window.window_top, window.window_width, window.window_height))
                    print('find')
                    return False
                except:
                    print('not found')
                    print('仍有剩余次数')
                    return True

    def fighting(self):
        i = 1
        while 1:
            x, y = get_coor_info_picture_tupo(tupo_yinyangliao_x[(i + 1) % 2 + 1], tupo_yinyangliao_y[(i + 1) // 2], 'fail.png')
            if x == 0 or y == 0:
                print(i, 'need to fight')
                fighting_tupo(tupo_yinyangliao_x[(i + 1) % 2 + 1], tupo_yinyangliao_y[(i + 1) // 2])
                if function.result():
                    # 胜利
                    flag = 1
                else:
                    # 失败
                    flag = 0
                time.sleep(2)
                # 结束界面
                x, y = function.random_finish_left_right()
                pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
                pyautogui.click()
                return flag
            else:
                print(i, 'fail')
                i += 1
                if i == 8:
                    # 单页上限8个
                    print('all fail')
                    flag = -1
                    return flag


def Run_Tupo_Yinyangliao(n: int):
    """
    阴阳寮突破主程序

    :param n: 次数
    """
    print('loading...')
    time.sleep(2)
    function.judge_scene(f'{picpath}/title.png', '结界突破')
    time.sleep(2)
    while 1:
        if function.judge_scene(f'{picpath}/tupojilu.png'):
            break
        else:
            function.judge_click(f'{picpath}/yinyangliao.png', dura=0.5)
            time.sleep(4)
    time.sleep(2)
    tp = jiejietupo_yinyangliao()
    m = 1 # 计数器
    while m <= n:
        print(f'{m}/{n}')
        flag = tp.fighting()
        if flag:
            m += 1
        elif flag == -1:
            break
        time.sleep(3)
    print('over')
