#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# huodong.py
"""
限时活动
"""

import time

from utils.function import function, time_consumption_statistics
from utils.log import log


class HuoDong:
    """限时活动"""

    def __init__(self, n: int = 0) -> None:
        self.scene_name = "限时活动"
        self.resource_path = "huodong"  # 路径
        self.n = 0  # 当前次数
        self.max = n  # 总次数
        self.scene_list: list = [
            "title",  # 限时活动特征图像
            "tiaozhan"  # 挑战
        ]

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if function.judge_scene(f"{self.resource_path}/title.png", self.scene_name):
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def start(self):
        """挑战开始"""
        function.judge_click(f"{self.resource_path}/tiaozhan.png")

    @time_consumption_statistics
    def run(self) -> None:
        time.sleep(2)
        if self.title():
            log.num(f"0/{self.max}")
            function.random_sleep(1, 3)
            while self.n < self.max:
                function.random_sleep(1, 2)
                # 开始
                function.judge_click(f"{self.resource_path}/tiaozhan.png")
                # 结束
                function.result()
                function.random_sleep(1, 2)
                # 结算
                function.random_finish_left_right(is_yuling=True)
                function.random_sleep(1, 3)
                self.n += 1
                log.num(f"{self.n}/{self.max}")
        text = f"已完成 {self.scene_name} {self.n}次"
        log.ui(text)
