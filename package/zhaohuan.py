#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# zhaohuan.py
"""普通召唤"""

from utils.decorator import *
from utils.function import function
from utils.log import log


class ZhaoHuan:
    """普通召唤"""

    def __init__(self, n: int = 0) -> None:
        self.scene_name: str = "普通召唤"
        self.n: int = 0  # 当前次数
        self.max: int = n  # 总次数
        self.resource_path: str = "zhaohuan"  # 路径
        self.resource_list: list = [  # 资源列表
            "putongzhaohuan",  # 普通召唤
            "queding",  # 确定
            "title",  # 标题
            "zaicizhaohuan"  # 再次召唤
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

    def first(self) -> None:
        """第一次召唤"""
        function.judge_click(f"{self.resource_path}/putongzhaohuan.png")
        function.random_sleep(6, 8)

    def again(self) -> None:
        """非第一次召唤"""
        function.judge_click(f"{self.resource_path}/zaicizhaohuan.png")
        function.random_sleep(6, 8)

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        flag = True  # 是否第一次
        if self.title():
            log.num(f"0/{self.max}")
            function.random_sleep(1, 3)
            while self.n < self.max:
                if flag:
                    self.first()
                    flag = False
                    self.n += 1
                else:
                    self.again()
                    self.n += 1
                log.num(f"{self.n}/{self.max}")
            # 结束
            if self.n == self.max:
                function.judge_click(f"{self.resource_path}/queding.png")
        log.ui(f"已完成 普通召唤十连 {self.n}次")
