#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# zhaohuan.py
"""普通召唤"""

from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import check_scene, random_sleep
from ..utils.log import logger
from .utils import Package


class ZhaoHuan(Package):
    """普通召唤"""
    scene_name = "普通召唤"
    resource_path = "zhaohuan"
    resource_list = [
        "putongzhaohuan",  # 普通召唤
        "queding",  # 确定
        "title",  # 标题
        "zaicizhaohuan",  # 再次召唤
    ]
    description = "普通召唤，请选择十连次数，仅适配默认召唤屋"

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

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
                logger.ui("请检查游戏场景", "warn")

    def first(self) -> None:
        """第一次召唤"""
        self.check_click("putongzhaohuan")

    def again(self) -> None:
        """非第一次召唤"""
        self.check_click("zaicizhaohuan")

    def run(self) -> None:
        _flag_first = True  # 是否第一次
        logger.num(f"0/{self.max}")
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
        self.check_click("queding")
