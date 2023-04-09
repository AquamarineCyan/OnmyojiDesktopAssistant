#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rilun.py
"""组队日轮副本"""

import pyautogui

from utils.decorator import *
from utils.function import function
from utils.log import log
from utils.window import window


class RiLun:
    """日轮副本"""

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
        self.flag_passenger_2: bool = False  # 队员2就位
        self.flag_passenger_3: bool = False  # 队员3就位
        self.flag_driver_start: bool = False  # 司机待机
        self.flag_fighting: bool = False  # 是否进行中对局（默认否）

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if function.judge_scene(f"{self.resource_yuhun_path}/xiezhanduiwu.png", "组队御魂准备中"):
                self.flag_driver_start = True
                return True
            elif function.judge_scene(f"{self.resource_yuhun_path}/fighting.png", "组队御魂进行中"):
                self.flag_fighting = True
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def finish(self) -> None:
        """结算"""
        while True:
            x, y = function.get_coor_info_picture("victory_gu.png")
            if x != 0 and y != 0:
                log.ui("结算中")
                break
        function.random_sleep(2, 4)
        x, y = function.random_finish_left_right(False)
        while True:
            pyautogui.moveTo(
                x + window.window_left,
                y + window.window_top,
                duration=0.25
            )
            pyautogui.doubleClick()
            if function.result():
                while True:
                    function.random_sleep(1, 2)
                    pyautogui.click()
                    function.random_sleep(1, 2)
                    x, y = function.get_coor_info_picture("victory.png")
                    if x == 0 or y == 0:
                        break
                break
            function.random_sleep(0, 1)

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        if self.title():
            log.num(f"0/{self.max}")
            while self.n < self.max:
                self.flag_passenger_2 = False
                self.flag_passenger_3 = False
                # 司机
                if self.flag_driver and self.flag_driver_start:
                    log.ui("等待队员")
                    # 队员2就位
                    while True:
                        x, y = function.get_coor_info_picture(
                            f"{self.resource_yuhun_path}/passenger_2.png"
                        )
                        if x == 0 and y == 0:
                            self.flag_passenger_2 = True
                            log.ui("队员2就位")
                            break
                    # 是否3人组队
                    if self.flag_passengers == 3:
                        while True:
                            x, y = function.get_coor_info_picture(
                                f"{self.resource_yuhun_path}/passenger_3.png"
                            )
                            if x == 0 and y == 0:
                                self.flag_passenger_3 = True
                                log.ui("队员3就位")
                                break
                    # 开始挑战
                    function.judge_click(
                        f"{self.resource_yuhun_path}/tiaozhan.png", dura=0.25)
                    log.ui("开始")
                if not self.flag_fighting:
                    function.judge_click(f"{self.resource_path}/fighting.png", False)
                    self.flag_fighting = False
                    log.ui("对局进行中")
                self.finish()
                self.n += 1
                log.num(f"{self.n}/{self.max}")
                function.random_sleep(1, 2)
        log.ui(f"已完成 组队日轮副本 {self.n}次")
