#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# yongshengzhihai.py
"""永生之海副本"""

import pyautogui

from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import (
    RESOURCE_FIGHT_PATH,
    check_click,
    check_scene_multiple_once,
    click,
    finish_random_left_right,
    random_sleep,
    result
)
from ..utils.log import logger
from ..utils.window import window
from .utils import Package


class YongShengZhiHai(Package):
    """永生之海副本"""
    scene_name = "永生之海副本"
    resource_path = "yongshengzhihai"
    resource_list = [
        "title_team",  # 组队界面
        "passenger",  # 队员
        "start_team",  # 组队挑战
        # "start_single",  # 单人挑战
        "fighting",  # 进行中
        # "accept_invitation",  # 接受邀请
    ]
    description = "默认打手30次"
    fast_time = 13 - 2

    @log_function_call
    def start(self) -> None:
        """挑战"""
        if isinstance(self, YongShengZhiHaiTeam):
            check_click(f"{self.resource_path}/start_team")
        else:
            check_click(f"{RESOURCE_FIGHT_PATH}/start_single")


class YongShengZhiHaiTeam(YongShengZhiHai):
    """组队永生之海副本"""
    scene_name = "组队永生之海副本"
    resource_list = [
        "title_team",  # 组队界面
        "passenger_2",  # 队员2
        "start_team",  # 组队挑战
        "fighting",  # 进行中
        "accept_invitation",  # 接受邀请
    ]

    @log_function_call
    def __init__(
        self,
        n: int = 0,
        flag_driver: bool = False,
        flag_drop_statistics: bool = False  # TODO
    ) -> None:
        """
        组队永生之海副本

        参数:
            n (int): 次数，默认0次

            flag_driver (bool): 是否司机，默认否

            flag_drop_statistics (bool): 是否开启掉落统计，默认否
        """
        super().__init__(n)
        self.flag_driver: bool = flag_driver  # 是否为司机（默认否）
        self.flag_drop_statistics: bool = flag_drop_statistics  # 是否开启掉落统计

    @log_function_call
    def is_passengers_on_position(self):
        """队员就位"""
        logger.ui("等待队员")
        while True:
            if event_thread.is_set():
                return
            coor = self.get_coor_info("passenger")
            if coor.is_zero:
                logger.ui("队员就位")
                return

    @log_function_call
    def finish(self):
        """
        结束

        掉落物大体分为2种情况：

        1.正常情况，达摩蛋能被识别

        2.掉落过多情况（指神罚一排紫蛇皮），达摩蛋被遮挡，此时贪吃鬼必定（可能）出现
        """
        _flag_screenshot = True
        _flag_first = True
        result()
        random_sleep(0.4, 0.8)
        # 结算
        coor = finish_random_left_right(False, is_multiple_drops_x=True)

        pyautogui.moveTo(coor.x + window.window_left, coor.y + window.window_top, duration=0.25)
        pyautogui.doubleClick()
        while True:
            if event_thread.is_set():
                return
            # 检测到任一图像
            scene, coor = check_scene_multiple_once([
                f"{RESOURCE_FIGHT_PATH}/finish",
                f"{RESOURCE_FIGHT_PATH}/tanchigui"
            ])
            if coor.is_effective:
                if _flag_screenshot and self.flag_drop_statistics:
                    self.screenshot()
                    _flag_screenshot = False
                click()
                _flag_first = False
                random_sleep(0.6, 1)
            # 所有图像都未检测到，退出循环
            elif _flag_first:
                continue
            elif coor.is_zero:
                logger.ui("结束")
                return

    def run(self):
        # 保留必需图像，提高识别效率
        _g_resource_list: list = [
            f"{self.resource_path}/title_team",  # 组队界面
            # f"{RESOURCE_FIGHT_PATH}/start_team",  # 组队挑战
            f"{self.resource_path}/fighting",  # 战斗中-小白
            f"{RESOURCE_FIGHT_PATH}/accept_invitation",  # 接受邀请
        ]
        if self.flag_driver:
            _g_resource_list.append(f"{RESOURCE_FIGHT_PATH}/start_team")
        _flag_title_msg: bool = True

        logger.num(f"0/{self.max}")
        while self.n < self.max:
            if event_thread.is_set():
                return
            self.current_resource_list = _g_resource_list
            scene, coor = self.check_scene_multiple_once()
            if scene is None:
                continue
            self.scene_handle(scene)

            match self.current_scene:
                case "title_team":
                    logger.ui("组队界面准备中")
                    if self.flag_driver:
                        self.is_passengers_on_position()
                        self.start()
                        # self.start()
                    random_sleep()
                    _flag_title_msg = False
                case "fighting":
                    logger.ui("对局进行中")
                    self.finish()
                    self.done()
                    random_sleep()
                    _flag_title_msg = False
                case "accept_invitation":
                    # TODO 新设备第一次接受邀请会有弹窗，需手动勾选“不再提醒”
                    logger.ui("接受邀请")
                    click(coor)
                case _:
                    if _flag_title_msg:
                        logger.ui("请检查游戏场景", "warn")
                        _flag_title_msg = False
