#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rilun.py
"""组队日轮副本"""

import pyautogui

from src.utils.event import event_thread
from ..utils.decorator import log_function_call, run_in_thread, time_count
from ..utils.function import (
    check_click,
    check_scene,
    click,
    finish,
    finish_random_left_right,
    get_coor_info,
    is_passengers_on_position,
    random_sleep,
    result,
    RESOURCE_FIGHT_PATH
)
from ..utils.log import log
from ..utils.window import window


class RiLun:
    """日轮副本"""

    @log_function_call
    def __init__(self, n: int = 0, flag_driver: bool = False, flag_passengers: int = 2) -> None:
        self.scene_name: str = "日轮副本"
        self.n: int = 0  # 当前次数
        self.max: int = n  # 总次数
        self.resource_path: str = "rilun"  # 路径
        self.resource_yuhun_path: str = "yuhun"  # 御魂路径，复用资源
        self.resource_list: list = [  # 资源列表
            "fighting"  # 对局进行中
        ]

        self.flag_driver: bool = flag_driver  # 是否为司机（默认否）
        self.flag_passengers: bool = flag_passengers  # 组队人数
        self.flag_driver_start: bool = False  # 司机待机
        self.flag_fighting: bool = False  # 是否进行中对局（默认否）

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if event_thread.is_set():
                return
            if check_scene(f"{self.resource_yuhun_path}/xiezhanduiwu", "组队御魂准备中"):
                self.flag_driver_start = True
                return True
            elif check_scene(f"{self.resource_yuhun_path}/fighting", "组队御魂进行中"):
                self.flag_fighting = True
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def finish(self) -> None:
        """结束"""
        result()
        random_sleep(1.5, 3)
        coor = finish_random_left_right(is_click=False)
        while True:
            if event_thread.is_set():
                return
            pyautogui.moveTo(
                coor.x + window.window_left,
                coor.y + window.window_top,
                duration=0.25
            )
            pyautogui.doubleClick()
            if finish():
                while True:
                    if event_thread.is_set():
                        return
                    random_sleep(1, 2)
                    click()
                    random_sleep(1, 2)
                    coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")
                    if coor.is_zero:
                        break
                break
            random_sleep(0, 1)

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        if self.title():
            log.num(f"0/{self.max}")
            while self.n < self.max:
                if event_thread.is_set():
                    return
                # 司机
                if self.flag_driver and self.flag_driver_start:
                    is_passengers_on_position(self.flag_passengers)
                    # 开始挑战
                    check_click(f"{RESOURCE_FIGHT_PATH}/start_team", dura=0.25)
                    log.ui("开始")
                if not self.flag_fighting:
                    check_click(f"{self.resource_path}/fighting", False)
                    self.flag_fighting = False
                    log.ui("对局进行中")
                self.finish()
                self.n += 1
                log.num(f"{self.n}/{self.max}")
                random_sleep(1, 2)
        log.ui(f"已完成 组队日轮副本 {self.n}次")
