#!/usr/bin/env python3
# yuling.py
"""
御灵副本
主界面功能7
"""

import time

from . import function
from mysignal import global_ms as ms

'''
御灵场景
title.png
挑战
tiaozhan.png
'''


class YuLing:
    """御灵副本"""

    def __init__(self):
        self.picpath = 'yuling'  # 路径
        self.m = 0  # 当前次数
        self.n = None  # 总次数

    def title(self):
        """场景"""
        flag_title = True  # 场景提示
        while 1:
            if function.judge_scene(f'{self.picpath}/title.png', '[SCENE] 御灵'):
                return True
            elif flag_title:
                flag_title = False
                ms.text_print_update.emit('[WARN] 请检查游戏场景')

    def start(self):
        """挑战开始"""
        function.judge_click(f'{self.picpath}/tiaozhan.png')

    def run(self, n: int):
        time.sleep(2)
        self.n = n
        if self.title():
            ms.text_num_update.emit(f'0/{self.n}')
            function.random_sleep(1, 3)
            while self.m < self.n:
                function.random_sleep(1, 2)
                # 开始
                self.start()
                # 结束
                function.result()
                function.random_sleep(1, 2)
                # 结算
                function.random_finish_left_right(is_yuling=True)
                function.random_sleep(1, 3)
                self.m += 1
                ms.text_num_update.emit(f'{self.m}/{self.n}')
        ms.text_print_update.emit(f'已完成 御灵副本{self.m}次')
        # 启用按钮
        ms.is_fighting_update.emit(False)
