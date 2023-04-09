#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# yeyuanhuo.py
"""业原火副本"""

from utils.decorator import *
from utils.function import function
from utils.log import log

class YeYuanHuo:
    """业原火副本"""

    def __init__(self,n:int = 0) -> None:
        self.scene_name: str = "业原火副本"
        self.n: int = 0  # 当前次数
        self.max: int = None  # 总次数
        self.resource_path: str = "yeyuanhuo"  # 路径
        self.resource_list: list = [
            "tiaozhan",  # 挑战
            "title"  # 标题
        ]

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

    @run_in_thread
    @time_count
    @log_function_call
    def run(self):
        if self.title():
            log.num(f"0/{self.max}")
            function.random_sleep(1, 3)
            while self.n < self.max:
                function.random_sleep(1, 2)
                # 开始
                self.start()
                # 结束
                function.result()
                function.random_sleep(1, 2)
                # 结算
                function.random_finish_left_right(is_multiple_drops_y=True)
                function.random_sleep(1, 3)
                self.n += 1
                log.num(f"{self.n}/{self.max}")
        log.ui(f"已完成 业原火副本 {self.n}次")
