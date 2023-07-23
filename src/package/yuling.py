#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# yuling.py
"""御灵副本"""

from src.utils.event import event_thread

from ..utils.decorator import log_function_call, run_in_thread, time_count
from ..utils.function import (
    check_click,
    check_scene,
    finish,
    finish_random_left_right,
    random_sleep
)
from ..utils.log import log


class YuLing:
    """御灵副本"""

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        self.scene_name: str = "御灵副本"
        self.n: int = 0  # 当前次数
        self.max: int = n  # 总次数
        self.resource_path: str = "yuling"  # 路径
        self.resource_list: list = [  # 资源列表
            "title",  # 限时活动特征图像
            "start"  # 挑战
        ]

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if event_thread.is_set():
                return
            if check_scene(f"{self.resource_path}/title", self.scene_name):
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景")

    def start(self) -> None:
        """开始"""
        check_click(f"{self.resource_path}/start")

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        if self.title():
            log.num(f"0/{self.max}")
            while self.n < self.max:
                if event_thread.is_set():
                    return
            
                random_sleep(1, 2)
                # 开始
                self.start()
                # 结束
                finish()
                random_sleep(1, 2)
                # 结算
                finish_random_left_right(is_multiple_drops_y=True)
                random_sleep(1, 3)
                self.n += 1
                log.num(f"{self.n}/{self.max}")
                # TODO 强制等待，后续优化
                if self.n in {12, 25, 39, 59, 73}:
                    random_sleep(10, 20)
        log.ui(f"已完成 {self.scene_name} {self.n}次")
