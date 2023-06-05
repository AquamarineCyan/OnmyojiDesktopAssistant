#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# zhaohuan.py
"""普通召唤"""

from ..utils.decorator import log_function_call, run_in_thread, time_count
from ..utils.function import check_click, check_scene, random_sleep
from ..utils.log import log


class ZhaoHuan:
    """普通召唤"""

    @log_function_call
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
            if check_scene(f"{self.resource_path}/title", self.scene_name):
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景")

    def first(self) -> None:
        """第一次召唤"""
        check_click(f"{self.resource_path}/putongzhaohuan")
        random_sleep(6, 8)

    def again(self) -> None:
        """非第一次召唤"""
        check_click(f"{self.resource_path}/zaicizhaohuan")
        random_sleep(6, 8)

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        flag = True  # 是否第一次
        if self.title():
            log.num(f"0/{self.max}")
            while self.n < self.max:
                if flag:
                    self.first()
                    flag = False
                else:
                    self.again()
                self.n += 1
                log.num(f"{self.n}/{self.max}")
            # 结束
            if self.n == self.max:
                check_click(f"{self.resource_path}/queding")
        log.ui(f"已完成 普通召唤十连 {self.n}次")
