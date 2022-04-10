#!usr/bin/env python3
# daoguantupo.py
"""
道馆突破
主界面功能6
"""

from . import function

import time
import pyautogui
from colorama import init, Fore, Back, Style

picpath = 'daoguantupo'
'''图片路径'''

'''
标题
title.png
挑战
tiaozhan.png
倒计时
daojishi.png
预设1
yushe1.png
出战
chuzhan.png
准备
zhunbei.png
助威开关
button_zhuwei.png
剩余突破时间
shengyutuposhijian.png
观战
guanzhan.png
前往
qianwang.png
助威
zhuwei.png
馆主战
guanzhuzhan.png
胜利
victory.png
'''


class daoguantupo:
    """道馆突破"""

    def title(self):
        """场景"""
        x, y = function.get_coor_info_picture(f'{picpath}/title.png')
        if x != 0 and y != 0:
            print(Fore.GREEN + '场景：道馆突破')
            return True
        else:
            return False

    def judge_scene(self):
        scene = {
            'daojishi.png': '倒计时',
            'shengyutuposhijian.png': '可进攻',
            'guanzhuzhan.png': '馆主战',
            'button_zhuwei.png': '进行中'
        }
        for item in scene.keys():
            x, y = function.get_coor_info_picture(f'{picpath}/{item}')
            if x != 0 and y != 0:
                # print(scene[item])
                return scene[item]
    def guanzhan(self):
        """观战"""

    def guanzhuzhan(self):
        """馆主战"""


def run_daoguantupo():
    """道馆突破主程序"""
    print('loading...')
    time.sleep(2)
    flag_title = True  # 场景提示
    flag_fighting = False  # 进行中
    flag_daojishi = True  # 倒计时
    flag_result = False  # 结束
    dgtp = daoguantupo()
    # judge
    while 1:
        if dgtp.title():
            while 1:
                if dgtp.judge_scene() == '倒计时':
                    if flag_daojishi:
                        print(Fore.GREEN + '等待系统自行进入')
                        flag_daojishi = False
                    flag_fighting = True
                    time.sleep(10)
                else:
                    break
            break
        elif dgtp.judge_scene() == '进行中':
            print(Fore.GREEN + '道馆突破进行中')
            flag_fighting = True
            break
        elif flag_title:
            flag_title = False
            print(Fore.RED + '请检查游戏场景')
    time.sleep(2)
    if not flag_fighting:
        function.judge_click(f'{picpath}/tiaozhan.png')
    time.sleep(4)
    # 调整预设队伍
    # start
    while 1:
        scene = {
            f'{picpath}/zhunbei.png': '准备',
            'victory.png': '胜利',
            'fail.png': '失败'
        }
        for item in scene.keys():
            x, y = function.get_coor_info_picture(item)
            if x != 0 and y != 0:
                if item == 'victory.png' or item == 'fail.png':
                    time.sleep(2)
                    flag_result = True
                print(scene[item])
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                break
        time.sleep(4)
        if flag_result:
            break
    print(Fore.RED + 'over')
