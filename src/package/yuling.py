#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# yuling.py
"""御灵副本"""

from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import (
    check_scene,
    finish,
    finish_random_left_right,
    random_sleep
)
from ..utils.log import logger
from .utils import Package


class YuLing(Package):
    """御灵副本"""
    scene_name = "御灵副本"
    resource_path = "yuling"
    resource_list = [
        "title",  # 限时活动特征图像
        "start",  # 挑战
    ]
    description = """暗神龙-周二六日
         暗白藏主-周三六日
         暗黑豹-周四六
         暗孔雀-周五六日
         绘卷期间请减少使用"""

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

    def start(self) -> None:
        """开始"""
        self.check_click("start")

    def run(self) -> None:
        self.title()
        logger.num(f"0/{self.max}")
        while self.n < self.max:
            if event_thread.is_set():
                return
            random_sleep()
            # 开始
            self.start()
            # 结束
            finish()
            random_sleep()
            # 结算
            finish_random_left_right(is_multiple_drops_y=True)
            random_sleep()
            self.done()
            # TODO 强制等待，后续优化
            if self.n in {12, 25, 39, 59, 73}:
                random_sleep(10, 20)
