#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# yeyuanhuo.py
"""业原火副本"""

from utils.coordinate import Coor
from utils.decorator import *
from utils.function import function
from utils.log import log


class YeYuanHuo:
    """业原火副本"""

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        self.scene_name: str = "业原火副本"
        self.n: int = 0  # 当前次数
        self.max: int = n  # 总次数
        self.fast_time: int = 13  # 最快通关速度，用于中途等待
        self.resource_path: str = "yeyuanhuo"  # 路径
        self.resource_list: list = [

            "title",  # 标题
            "start"  # 挑战
        ]

    @log_function_call
    def title(self) -> bool:
        """场景"""
        function.check_scene_multiple_while(self.resource_list, self.resource_path, text="请检查游戏场景")
        return True

    @log_function_call
    def start(self):
        """挑战开始"""
        function.judge_click(f"{self.resource_path}/start")

    @run_in_thread
    @time_count
    @log_function_call
    def run(self):
        if self.title():
            log.num(f"0/{self.max}")
            while self.n < self.max:
                scene, (x, y) = function.check_scene_multiple_once(self.resource_list, self.resource_path)
                if Coor(x, y).is_effective:
                    match scene:
                        case "title":
                            self.start()
                            function.random_sleep(self.fast_time, self.fast_time+1)
                        case "start":
                            function.click(x, y)
                            function.random_sleep(self.fast_time, self.fast_time+1)
                result = function.result_once()
                if result:
                    self.n += 1
                    log.num(f"{self.n}/{self.max}")
                    function.random_sleep(1, 2)
                    function.random_finish_left_right()
                    function.random_sleep(2, 4)
                    continue
                elif result == False:
                    log.error("失败，需要手动处理", True)
            log.ui(f"已完成 业原火副本 {self.n}次")
