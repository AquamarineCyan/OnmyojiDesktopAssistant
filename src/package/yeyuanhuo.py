#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# yeyuanhuo.py
"""业原火副本"""

from src.utils.event import event_thread
from ..utils.decorator import log_function_call, run_in_thread, time_count
from ..utils.function import (
    check_click,
    check_finish_once,
    check_scene_multiple_once,
    check_scene_multiple_while,
    click,
    finish_random_left_right,
    random_sleep
)
from ..utils.log import log
from .utils import Package


class YeYuanHuo(Package):
    """业原火副本"""
    scene_name: str = "业原火副本"
    resource_path: str = "yeyuanhuo"
    resource_list: list = [
        "title",  # 标题
        "start"  # 挑战
    ]
    fast_time: int = 13  # 最快通关速度，用于中途等待

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    @log_function_call
    def title(self) -> bool:
        """场景"""
        check_scene_multiple_while(self.resource_list, self.resource_path, text="请检查游戏场景")
        return True

    @log_function_call
    def start(self):
        """挑战开始"""
        check_click(f"{self.resource_path}/start")

    @run_in_thread
    @time_count
    @log_function_call
    def run(self):
        log.num(f"0/{self.max}")
        while self.n < self.max:
            if event_thread.is_set():
                return
            
            scene, coor = check_scene_multiple_once(self.resource_list, self.resource_path)
            # if scene is None:
            #     continue
            if scene:
                self.scene_print(scene)

            if coor.is_effective:
                match scene:
                    case "title":
                        self.start()
                        random_sleep(self.fast_time, self.fast_time+1)
                    case "start":
                        click(coor)
                        random_sleep(self.fast_time, self.fast_time+1)
            if result := check_finish_once():
                self.done()
                random_sleep(1, 2)
                finish_random_left_right()
                random_sleep(2, 4)
                continue
            elif result == False:
                log.error("失败，需要手动处理", True)
        log.ui(f"已完成 {self.scene_name} {self.n}次")
