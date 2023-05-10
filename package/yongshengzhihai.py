#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# yongshengzhihai.py
"""组队永生之海副本"""

import pyautogui

from utils.decorator import *
from utils.function import (
    RESOURCE_FIGHT_PATH,
    check_click,
    check_scene,
    finish,
    finish_random_left_right,
    get_coor_info,
    random_sleep
)
from utils.log import log
from utils.window import window


class YongShengZhiHai:
    """组队永生之海副本"""

    @log_function_call
    def __init__(self, n: int = 0, flag_driver: bool = False) -> None:
        """组队永生之海副本

        参数:
            n (int): 次数,默认0次
            flag_driver (bool): 是否司机,默认否
        """
        self.scene_name: str = "组队永生之海副本"
        self.n: int = 0  # 当前次数
        self.max: int = n  # 总次数
        self.resource_path: str = "yongshengzhihai"  # 路径
        self.resource_list: list = [  # 资源列表
            "fighting",  # 战斗中
            "passenger",  # 队员
            "start",  # 挑战
            "title",  # 标题-四层
            "victory"  # 成功
        ]

        self.flag_driver: bool = flag_driver  # 是否为司机（默认否）
        self.flag_passenger: bool = False  # 队员2就位
        self.flag_driver_start: bool = False  # 司机待机
        self.flag_fighting: bool = False  # 是否进行中对局（默认否）

    def get_coor_info(self, file: str):
        return get_coor_info(f"{self.resource_path}/{file}")

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if check_scene(f"{self.resource_path}/title", "组队永生之海准备中"):
                self.flag_driver_start = True
                return True
            elif check_scene(f"{self.resource_path}/fighting", "组队永生之海进行中"):
                self.flag_fighting = True
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景")

    def finish(self) -> None:
        """结束"""
        while True:
            coor = get_coor_info(f"{self.resource_path}/victory")
            if coor.is_effective:
                log.ui("结算中")
                break
        random_sleep(2, 4)
        coor = finish_random_left_right(is_click=False)
        while True:
            pyautogui.moveTo(
                coor.x + window.window_left,
                coor.y + window.window_top,
                duration=0.25
            )
            pyautogui.doubleClick()
            if finish():
                while True:
                    random_sleep(1, 2)
                    pyautogui.click()
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
                self.flag_passenger = False
                # 司机
                if self.flag_driver and self.flag_driver_start:
                    log.ui("等待队员")
                    # 队员就位
                    while True:
                        coor = get_coor_info(f"{self.resource_path}/passenger")
                        if coor.is_zero:
                            self.flag_passenger = True
                            log.ui("队员就位")
                            break
                    # 开始挑战
                    check_click(f"{self.resource_path}/start")
                    log.ui("开始")
                if not self.flag_fighting:
                    check_click(f"{self.resource_path}/fighting", is_click=False)
                    self.flag_fighting = False
                    log.ui("对局进行中")
                self.finish()
                self.n += 1
                log.num(f"{self.n}/{self.max}")
                random_sleep(1, 2)
        log.ui(f"已完成 {self.scene_name} {self.n}次")
