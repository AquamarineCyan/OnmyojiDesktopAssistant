#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# yuhun.py
"""组队御魂副本"""

import pyautogui

from utils.decorator import *
from utils.function import function
from utils.log import log
from utils.window import window


class YuHun():
    """组队御魂副本"""

    def __init__(
        self,
        n: int = 0,
        flag_driver: bool = False,
        flag_passengers: int = 2,
        flag_drop_statistics: bool = False
    ) -> None:
        """组队御魂副本

        参数:
            n (int): 次数，默认0次
            flag_driver (bool): 是否司机，默认否
            flag_passengers (int): 组队人数，默认2人
            flag_drop_statistics (bool): 是否开启掉落统计，默认否
        """
        self.scene_name: str = "组队御魂副本"
        self.n: int = 0  # 当前次数
        self.max: int = n  # 总次数
        self.resource_path: str = "yuhun"  # 路径
        self.resource_list: list = [  # 资源列表
            "xiezhanduiwu",  # 组队界面
            "fighting",  # 魂土进行中
            "fighting_linshuanghanxue",  # 凛霜寒雪战斗主题
            "fighting_shenfa",  # 神罚战斗场景
            "passenger_2",  # 队员2
            "passenger_3",  # 队员3
            "tiaozhan",  # 挑战
            "yuhun_victory",  # 胜利
            "yuhun_victory_2000",  # 2000天鎏金圣域背景
            "yuhun_victory_shenfa",  # 神罚胜利
            "finish_shenfa"  # 神罚结算
        ]

        self.flag_driver: bool = flag_driver  # 是否为司机（默认否）
        self.flag_passengers: int = flag_passengers  # 组队人数
        self.flag_passenger_2: bool = False  # 队员2就位
        self.flag_passenger_3: bool = False  # 队员3就位
        self.flag_driver_start: bool = False  # 司机待机
        self.flag_fighting: bool = False  # 是否进行中对局（默认否）
        self.flag_is_first: bool = True  # 是否第一次（用于接受邀请）
        self.flag_drop_statistics: bool = flag_drop_statistics  # 是否开启掉落统计
        log.info(f"次数:{self.max}\n司机:{self.flag_driver}\n组队人数:{self.flag_passengers}\n掉落统计:{self.flag_drop_statistics}")

    def title(self):
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if function.judge_scene(f"{self.resource_path}/xiezhanduiwu.png", "组队御魂准备中"):
                self.flag_driver_start = True
                return True
            elif function.judge_scene(f"{self.resource_path}/fighting.png", "组队御魂进行中") or function.judge_scene(f"{self.resource_path}/fighting_linshuanghanxue.png", "组队御魂进行中"):
                self.flag_fighting = True
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def result(self) -> bool:
        """结果判断

        返回:
            bool: 结算结果
        """
        log.info("result check")
        while True:
            x, y = function.get_coor_info_picture("victory.png")
            if x != 0 and y != 0:
                log.ui("胜利")
                return True
            x, y = function.get_coor_info_picture(f"{self.resource_path}/victory_2000.png")
            if x != 0 and y != 0:
                log.ui("胜利 鎏金圣域")
                return True
            x, y = function.get_coor_info_picture(f"{self.resource_path}/finish_shenfa.png")
            if x != 0 and y != 0:
                log.ui("胜利 神罚副本")
                return True
            x, y = function.get_coor_info_picture("fail.png")
            if x != 0 and y != 0:
                log.ui("失败")
                return False

    def finish(self):
        """结束"""
        # while 1:
        #     x, y = function.get_coor_info_picture(f"{self.resource_path}/yuhun_victory.png")
        #     if x != 0 and y != 0:
        #         log.ui("胜利")
        #         break
        #     x, y = function.get_coor_info_picture(f"{self.resource_path}/yuhun_victory_2000.png")
        #     if x != 0 and y != 0:
        #         log.ui("胜利 鎏金圣域")
        #         break
        #     # finish_shenfa
        #     x, y = function.get_coor_info_picture(f"{self.resource_path}/yuhun_victory_shenfa.png")
        #     if x != 0 and y != 0:
        #         log.ui("胜利 神罚副本")
        #         break
        self.result()

        function.random_sleep(1, 3)
        # 结算
        x, y = function.random_finish_left_right(False, is_multiple_drops_x=True)
        while True:
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.25)
            pyautogui.doubleClick()
            if self.result():
                while True:
                    function.random_sleep(1, 2)
                    if self.flag_drop_statistics:
                        function.screenshot("cache_yuhun")
                    pyautogui.click()
                    function.random_sleep(1, 2)
                    # 未检测到图像，退出循环
                    x, y = function.get_coor_info_picture("victory.png")
                    if x == 0 or y == 0:
                        break
                    x, y = function.get_coor_info_picture(f"{self.resource_path}/victory_2000.png")
                    if x == 0 or y == 0:
                        log.ui("胜利 鎏金圣域")
                        break
                    x, y = function.get_coor_info_picture(f"{self.resource_path}/finish_shenfa.png")
                    if x == 0 or y == 0:
                        log.ui("胜利 神罚副本")
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
                # 接受邀请
                # XXX 能用，但是需要修改触发条件，或者重写为多场景
                # if self.flag_is_first:
                #     function.judge_click("accept_invitation")
                #     log.ui("接受邀请")

                # 司机
                if self.flag_driver and self.flag_driver_start:
                    log.ui("等待队员")
                    # 队员2就位
                    while True:
                        x, y = function.get_coor_info_picture(f"{self.resource_path}/passenger_2.png")
                        if x == 0 and y == 0:
                            self.flag_passenger_2 = True
                            log.ui("队员2就位")
                            break
                    # 是否3人组队
                    if self.flag_passengers == 3:
                        while 1:
                            x, y = function.get_coor_info_picture(f"{self.resource_path}/passenger_3.png")
                            if x == 0 and y == 0:
                                self.flag_passenger_3 = True
                                log.ui("队员3就位")
                                break
                    # 开始挑战
                    function.judge_click(f"{self.resource_path}/tiaozhan.png", dura=0.25)
                    log.ui("开始")
                if not self.flag_fighting:
                    # function.judge_click(f"{self.resource_path}/fighting.png", False)
                    while True:
                        scene, (x, y) = function.check_scene_multiple_once(
                            ["fighting", "fighting_linshuanghanxue", "fighting_shenfa"],
                            self.resource_path
                        )
                        if x != 0 and y != 0:
                            break
                    # log.ui(scene)
                    self.flag_fighting = False
                    log.ui("对局进行中")
                self.finish()
                self.n += 1
                log.num(f"{self.n}/{self.max}")
                function.random_sleep(1, 2)
        log.ui(f"已完成 组队御魂副本{self.n}次")


class Coordinate:
    """坐标"""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x: int = x
        self.y: int = y
        self.coor: tuple[int, int] = self._coor_tuple_func()
        self.is_zero = self._is_zero_func()

    def _coor_tuple_func(self) -> tuple[int, int]:
        return (self.x, self.y)

    def _is_zero_func(self) -> bool:
        if self.x == 0 or self.y == 0:
            return True
        else:
            return False


class YuHunTest:
    """组队御魂副本"""

    def __init__(
        self,
        n: int = 0,
        flag_driver: bool = False,
        flag_passengers: int = 2
    ) -> None:

        self.resource_path = "yuhun"  # 图片路径
        self.n = 0  # 当前次数
        self.max = n  # 总次数
        self.resource_list: list = [
            'xiezhanduiwu',  # 组队界面
            'fighting',
            'fighting_linshuanghanxue',
            'yuhun_victory',
            'yuhun_victory_2000',
            'passenger_2',
            'passenger_3',
            'tiaozhan'
        ]

        self.flag_driver = flag_driver  # 是否为司机（默认否）
        self.flag_passengers = flag_passengers  # 组队人数
        self.flag_passenger_2 = False  # 队员2就位
        self.flag_passenger_3 = False  # 队员3就位
        self.flag_driver_start = False  # 司机待机
        self.flag_title_msg = False  # 场景提示
        self.flag_fighting = False  # 是否进行中对局（默认否）
        self.flag_is_first: bool = True  # 是否第一次（用于接受邀请）

    @run_in_thread
    @time_count
    @log_function_call
    def run(self):
        while self.n < self.max:
            scene = function.check_scene_multiple_while(self.resource_list, self.resource_path)
            match scene:
                case 'xiezhanduiwu':
                    log.ui('组队界面准备中')
                    self.flag_driver_start = True
                    if self.flag_driver:
                        scene = function.check_scene_multiple_once(self.resource_list, self.resource_path)
                        match scene:
                            case '1':
                                pass
                case _:
                    if not self.flag_title_msg:
                        log.warn("请检查游戏场景", True)
                        self.flag_title_msg = True
                    else:
                        pass
