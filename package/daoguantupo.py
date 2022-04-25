#!usr/bin/env python3
# daoguantupo.py
"""
道馆突破
主界面功能6
"""

import time
import pyautogui

from . import function
from mysignal import global_ms as ms

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


class DaoGuanTuPo:
    """道馆突破"""

    def __init__(self):
        self.picpath = 'daoguantupo'  # 图片路径
        self.m = 0  # 当前次数
        self.flag_fighting = False  # 是否进行中

    def title(self):
        """场景"""
        flag_title = True  # 场景提示
        self.flag_fighting = False  # 进行中
        flag_daojishi = True  # 倒计时
        while 1:
            if function.judge_scene(f'{self.picpath}/title.png', '[SCENE] 道馆突破'):
                while 1:
                    # 等待倒计时自动进入
                    if self.judge_scene() == '倒计时':
                        if flag_daojishi:
                            ms.text_print_update.emit('等待倒计时自动进入')
                            flag_daojishi = False
                        self.flag_fighting = True
                        break
                    elif self.judge_scene() == '可进攻':
                        self.flag_fighting = False
                        break
                    # 馆主战
                    elif self.judge_scene() == '馆主战':
                        ms.text_print_update.emit('[WARN] 待开发')
                        break
                return True
            # 已进入道馆进攻状态
            elif self.judge_scene() == '进行中':
                ms.text_print_update.emit('道馆突破进行中')
                self.flag_fighting = True
                return True
            elif flag_title:
                flag_title = False
                ms.text_print_update.emit('[WARN] 请检查游戏场景')

    def judge_scene(self):
        """场景判断"""
        scene = {
            'daojishi.png': '倒计时',
            'shengyutuposhijian.png': '可进攻',
            'guanzhuzhan.png': '馆主战',
            'button_zhuwei.png': '进行中'
        }  # '可进攻'未实现
        for item in scene.keys():
            x, y = function.get_coor_info_picture(f'{self.picpath}/{item}')
            if x != 0 and y != 0:
                return scene[item]

    def guanzhan(self):
        """观战"""

    def guanzhuzhan(self):
        """馆主战"""

    def run(self):
        time.sleep(2)
        flag_result = False  # 结束
        if self.title():
            ms.text_num_update.emit(0)
            function.random_sleep(2, 4)
            if not self.flag_fighting:
                function.judge_click(f'{self.picpath}/tiaozhan.png')
            function.random_sleep(2, 4)
            # 调整预设队伍
            # 开始
            while 1:
                scene = {
                    f'{self.picpath}/zhunbei.png': '准备',
                    'victory.png': '胜利',
                    'fail.png': '失败'
                }
                for item in scene.keys():
                    x, y = function.get_coor_info_picture(item)
                    if x != 0 and y != 0:
                        if item == f'{self.picpath}/zhunbei.png':
                            self.m += 1
                            ms.text_num_update.emit(str(self.m))
                        if item == 'victory.png' or item == 'fail.png':
                            time.sleep(2)
                            flag_result = True
                        ms.text_print_update.emit(scene[item])
                        pyautogui.moveTo(x, y, duration=0.5)
                        pyautogui.click()
                        break
                function.random_sleep(4, 6)
                if flag_result:
                    break
        ms.text_print_update.emit(f'已完成 道馆突破 胜利{self.m}次')
        # 启用按钮
        ms.is_fighting_update.emit(False)
