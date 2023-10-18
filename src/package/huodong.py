#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# huodong.py
"""限时活动"""


from ..utils.decorator import log_function_call, run_in_thread, time_count
from ..utils.event import event_thread
from ..utils.function import (
    RESOURCE_FIGHT_PATH,
    check_click,
    check_scene,
    check_scene_multiple_once,
    click,
    finish,
    finish_random_left_right,
    get_coor_info,
    random_sleep
)
from ..utils.log import logger
from .utils import Package


class HuoDong(Package):
    """限时活动"""
    scene_name = "限时活动"
    resource_path = "huodong"
    resource_list: list = [
        "title",
        "start",
    ]
    description = """适配活动「演武练习」
可替换 resource/huodong 下的素材"""

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
        check_click(f"{self.resource_path}/start")

    def finish(self):
        if finish():
            random_sleep(0.4, 0.8)
            finish_random_left_right(is_multiple_drops_y=True)
            random_sleep(0.4, 0.8)
            while True:
                if event_thread.is_set():
                    return
                coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")
                if coor.is_zero:
                    return
                click()
                random_sleep(0.4, 0.8)

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        _g_resource_list: list = [
            f"{self.resource_path}/title",
            # f"{RESOURCE_FIGHT_PATH}/fighting_back_default",
        ]
        _flag_title_msg: bool = True

        logger.num(f"0/{self.max}")
        while self.n < self.max:
            if event_thread.is_set():
                return
            scene, coor = check_scene_multiple_once(_g_resource_list)
            if scene is None:
                continue
            if "/" in scene:
                scene = scene.split("/")[-1]
            match scene:
                case "title":
                    logger.scene("演武练习")
                    _flag_title_msg = False
                    self.start()
                    random_sleep(1, 2)
                # case "fighting_friend_default" | "fighting_friend_linshuanghanxue" | "fighting_friend_chunlvhanqing":
                # case "fighting_back_default":
                    # logger.ui("对局进行中")
                    self.finish()
                    self.done()
                    random_sleep(1.5, 3)
                case _:
                    if _flag_title_msg:
                        logger.ui("请检查游戏场景", "warn")
                        _flag_title_msg = False

        logger.ui(f"已完成 {self.scene_name} {self.n}次")
