#!/usr/bin/env python3
# zhaohuan.py
"""
普通召唤
主界面功能2
"""

from . import function

import time

picpath = 'zhaohuan'
'''图片路径'''

'''
标题
title.png
普通召唤
putongzhaohuan.png
再次召唤
zaicizhaohuan.png
'''


class zhaohuan:
    """召唤"""

    def title(self):
        """场景"""
        return function.judge_scene(f'{picpath}/title.png', '召唤')

    def first(self):
        """第一次召唤"""
        function.judge_click(f'{picpath}/putongzhaohuan.png')
        function.random_sleep(6, 8)

    def again(self):
        """非第一次召唤"""
        function.judge_click(f'{picpath}/zaicizhaohuan.png')
        function.random_sleep(6, 8)


def run_zhaohuan(n: int):
    """
    召唤主程序

    :param n: 次数
    """
    time.sleep(2)
    flag = False
    if n == 1:
        flag = True
    zh = zhaohuan()
    if zh.title():
        while n > 0:
            print(f'剩余{n}次')
            if flag:
                zh.first()
                flag = False
                n -= 1
            else:
                zh.again()
                n -= 1
    print('over')
