#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# zhaohuan.py
"""普通召唤"""

from src.utils.event import event_thread

from ..utils.decorator import log_function_call, run_in_thread, time_count
from ..utils.function import check_click, check_scene, random_sleep
from ..utils.log import log
from .utils import Package


class ZhaoHuan(Package):
    """普通召唤"""

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)
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
            if event_thread.is_set():
                return
            if check_scene(f"{self.resource_path}/title", self.scene_name):
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景")

    def first(self) -> None:
        """第一次召唤"""
        check_click(f"{self.resource_path}/putongzhaohuan")

    def again(self) -> None:
        """非第一次召唤"""
        check_click(f"{self.resource_path}/zaicizhaohuan")

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        _flag_first = True  # 是否第一次
        log.num(f"0/{self.max}")
        random_sleep(0.4, 0.8)
        self.title()

        while self.n < self.max:
            if event_thread.is_set():
                return
            if _flag_first:
                self.first()
                _flag_first = False
            else:
                self.again()
            random_sleep(4, 6)
            self.done()

        check_click(f"{self.resource_path}/queding")
        log.ui(f"已完成 普通召唤十连 {self.n}次")
