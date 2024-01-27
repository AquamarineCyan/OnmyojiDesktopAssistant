#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tansuo.py
"""探索副本-单人"""

import pyautogui

from ..utils.application import RESOURCE_DIR_PATH
from ..utils.coordinate import Coor
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import (
    check_click,
    check_finish_once,
    check_scene_multiple_once,
    click,
    drag_in_window,
    finish_random_left_right,
    get_coor_info,
    image_file_format,
    random_sleep
)
from ..utils.log import logger
from ..utils.window import window
from .utils import Package


class TanSuo(Package):
    """探索"""
    scene_name = "探索"
    resource_path = "tansuo"
    resource_list = [
        # "boss_finish",
        "chuzhanxiaohao",
        "fighting",
        "fighting_boss",
        "kunnan_big",
        # "kunnan_small",
        # "putong_big",
        # "putong_small",
        "quit",
        "quit_true",
        # "quit_true_false",
        "tansuo",
        "tansuo_28",
        "tansuo_28_0",
        "tansuo_28_title",
        "treasure_box",
        # "zidonglunhuan",
    ]
    description = "提前准备好自动轮换和加成，仅单人探索"

    def __init__(self, n: int = 0) -> None:
        super().__init__(n)
        self.flag_boss_done: bool = False  # boss战结束

    def get_all_coor_info_tansuo_center(self, file: str):
        """图像识别，返回匹配到的第一个图像的中心坐标

        参数:
            file (Path | str): 图像名称

        用法：
            `file` without `self.resource_path`

        返回:
            Coor: 识别成功，返回匹配到的第一个图像的全局中心坐标，识别失败，返回(0,0)
        """
        _file_name = image_file_format(RESOURCE_DIR_PATH / self.resource_path / file)
        logger.info(_file_name)
        try:
            for button_location in pyautogui.locateAllOnScreen(
                _file_name,
                region=(
                    window.window_left,
                    window.window_top,
                    window.window_standard_width,
                    window.window_standard_height
                ),
                confidence=0.8
            ):
                logger.info(f"button_location: {button_location}")
                button_location_center = pyautogui.center(button_location)
                logger.info(f"button_location_center: {button_location_center}")
                return Coor(button_location_center.x, button_location_center.y)
            # 未匹配到一个
            return Coor(0, 0)
        except Exception:
            return Coor(0, 0)

    @log_function_call
    def title(self) -> bool:
        flag_title = True  # 场景提示
        flag_fighting = False  # 进行中
        while True:
            if event_thread.is_set():
                return
            scene_list: list = [
                "chuzhanxiaohao",
                "tansuo_28",
                "tansuo_28_0",
                "tansuo_28_title"
            ]
            scene, coor = check_scene_multiple_once(scene_list, self.resource_path)
            if scene is None:
                continue
            scene = self.scene_handle(scene)

            match scene:
                case "chuzhanxiaohao" | "tansuo_28" | "tansuo_28_0" | "tansuo_28_title":
                    return True
                case _:
                    if flag_title:
                        flag_title = False
                        logger.ui("请检查游戏场景", "warn")

    @log_function_call
    def fighting(self, flag_boss=False):
        _flag_first: bool = False
        while True:
            if event_thread.is_set():
                return
            if check_finish_once():
                _flag_first = True
                random_sleep(0.5, 0.8)
                finish_random_left_right()
            elif _flag_first:
                if flag_boss:
                    self.flag_boss_done = True
                return
            random_sleep(1, 1.5)

    @log_function_call
    def finish(self):
        """boss战后的结束阶段

        1.有掉落物，不需要点击，直接左上角退出即可
        2.无掉落物，系统自动跳转出去
        3.1、2出来之后，存在宝箱/妖气封印的可能，当前章节的小界面被关闭，需要右侧列表重新点开
        """
        while True:
            if event_thread.is_set():
                return
            # 等待加载完毕
            random_sleep(1.5, 2)
            coor = get_coor_info(f"{self.resource_path}/chuzhanxiaohao")
            if coor.is_effective:
                check_click(f"{self.resource_path}/quit")
                random_sleep(0.4, 0.8)
                check_click(f"{self.resource_path}/quit_true")
            else:
                coor = get_coor_info(f"{self.resource_path}/tansuo")
                if coor.is_effective:
                    return
                if coor.is_zero:
                    # 宝箱
                    coor_treasure_box = get_coor_info(f"{self.resource_path}/treasure_box")
                    if coor_treasure_box.is_effective:
                        click(coor_treasure_box)
                        random_sleep(1.5, 2)
                        click()
                    # 妖气封印
                    return

    def run(self):
        _scene_list = [
            "tansuo_28_0",
            "tansuo_28_title",
            "kunnan_big",
            "tansuo",
            "chuzhanxiaohao",
        ]

        while self.n < self.max and self.title():
            if event_thread.is_set():
                return

            scene, coor = check_scene_multiple_once(_scene_list, self.resource_path)
            if scene is None:
                continue
            self.scene_print(scene)

            match scene:
                case "tansuo_28_0":  # 右侧列表按钮
                    # function.judge_click(f"{self.resource_path}/tansuo")
                    click(coor)
                    random_sleep()
                    # self.n += 1
                case "tansuo_28_title":
                    self.check_click("tansuo")
                    # self.n += 1
                    random_sleep(2)
                case "chuzhanxiaohao":
                    random_sleep(0.5, 1)
                    # 先判断boss面灵气
                    coor = self.get_coor_info("fighting_boss")
                    if coor.is_effective:
                        logger.scene("BOSS")
                        click(coor)
                        self.fighting(flag_boss=True)
                    else:  # FIXME 打完一次普通的就会退出整场探索
                        coor = self.get_all_coor_info_tansuo_center("fighting")
                        if coor.is_effective:
                            click(coor)
                            self.fighting()
                        else:
                            drag_in_window(-400, 0)
                    random_sleep()
                    if self.flag_boss_done:
                        self.flag_boss_done = False
                        self.finish()
                        self.done()
