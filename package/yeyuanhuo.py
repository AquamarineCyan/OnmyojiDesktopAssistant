#!/usr/bin/env python3
# yeyuanhuo.py
"""
业原火副本
"""

import time

from .function import Function
from mysignal import global_ms as ms

'''
业原火场景
title.png
挑战
tiaozhan.png
'''


class YeYuanHuo(Function):
    """业原火副本"""

    def __init__(self):
        self.picpath = 'yuling'  # 路径
        self.m = 0  # 当前次数
        self.n = None  # 总次数

    def title(self):
        """场景"""
        flag_title = True  # 场景提示
        while 1:
            if self.judge_scene(f'{self.picpath}/title.png', '[SCENE] 业原火'):
                return True
            elif flag_title:
                flag_title = False
                ms.text_print_update.emit('[WARN] 请检查游戏场景')

    def start(self):
        """挑战开始"""
        self.judge_click(f'{self.picpath}/tiaozhan.png')

    def run(self, n: int):
        time.sleep(2)
        self.n = n
        time_progarm = self.TimeProgram()  # 程序计时
        time_progarm.start()
        if self.title():
            ms.text_num_update.emit(f'0/{self.n}')
            self.random_sleep(1, 3)
            while self.m < self.n:
                self.random_sleep(1, 2)
                # 开始
                self.start()
                # 结束
                self.result()
                self.random_sleep(1, 2)
                # 结算
                self.random_finish_left_right(is_yuling=True)
                self.random_sleep(1, 3)
                self.m += 1
                ms.text_num_update.emit(f'{self.m}/{self.n}')
        text = f"已完成 业原火副本{self.m}次"
        time_progarm.end()
        text = text + " " + time_progarm.print()
        ms.text_print_update.emit(text)
        # 启用按钮
        ms.is_fighting_update.emit(False)
