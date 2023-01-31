#!/usr/bin/env python3
# yuling.py
"""
御灵副本
"""

import time

from utils.function import function, time_consumption_statistics
from utils.log import log

"""
御灵场景
title.png
挑战
tiaozhan.png
"""


class YuLing:
    """御灵副本"""

    def __init__(self) -> None:
        self.scene_name: str = "御灵副本"
        self.resource_path: str = "yuling"  # 路径
        self.m: int = 0  # 当前次数
        self.n: int = None  # 总次数

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if function.judge_scene(f"{self.resource_path}/title.png", self.scene_name):
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def start(self) -> None:
        """挑战开始"""
        function.judge_click(f"{self.resource_path}/tiaozhan.png")

    @time_consumption_statistics
    def run(self, n: int) -> None:
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
                # TODO 强制等待，后续优化
                if self.m == 12 or self.m == 25 or self.m == 39 or self.m == 59 or self.m == 73:
                    function.random_sleep(10, 20)
        text = f"已完成 {self.scene_name} {self.m}次"
        log.info(text, True)
