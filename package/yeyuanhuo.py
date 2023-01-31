#!/usr/bin/env python3
# yeyuanhuo.py
"""
业原火副本
"""

import time

from utils.function import function, time_consumption_statistics
from utils.log import log

"""
业原火场景
title.png
挑战
tiaozhan.png
"""


class YeYuanHuo:
    """业原火副本"""

    def __init__(self) -> None:
        self.scene_name: str = "业原火副本"
        self.resource_path: str = "yeyuanhuo"  # 路径
        self.m: int = 0  # 当前次数
        self.n: int = None  # 总次数

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if function.judge_scene(f"{self.resource_path}/title.png", "业原火副本"):
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def start(self):
        """挑战开始"""
        function.judge_click(f"{self.resource_path}/tiaozhan.png")

    @time_consumption_statistics
    def run(self, n: int):
        time.sleep(2)
        self.n = n
        if self.title():
            log.num(f"0/{self.n}")
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
                log.num(f"{self.m}/{self.n}")
        text = f"已完成 业原火副本 {self.m}次"
        log.info(text, True)
