#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# tansuo.py
"""契灵-探查"""

from threading import Timer
import time
import pyautogui

from ..utils.application import RESOURCE_DIR_PATH
from ..utils.coordinate import Coor
from ..utils.decorator import log_function_call, run_in_thread, time_count
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
from ..utils.log import log
from ..utils.window import window
from .utils import Package


class QiLing(Package):
    """契灵"""
    scene_name = "契灵"
    resource_path = "qiling"
    resource_list: list = [
        # "title",
        "start",
    ]

    def __init__(self, n: int = 0) -> None:
        super().__init__(n)
        self._flag_finish: bool = False
        self._timestamp: int = int(time.time())

    @log_function_call
    def fighting(self):
        _flag_first: bool = False
        while True:
            if self._flag_finish:
                log.ui("finish by fighting")
                return
            if check_finish_once():
                _flag_first = True
                random_sleep(0.5, 0.8)
                finish_random_left_right()
            elif _flag_first:
                random_sleep(0.3, 0.5)
                return
            random_sleep(0.3, 0.5)

    @log_function_call
    def timer_start(self):
        coor = get_coor_info(f"{self.resource_path}/start")
        if coor.is_effective:
            self._flag_finish = True

    @run_in_thread
    @time_count
    @log_function_call
    def run(self):
        log.ui("仅限探查，地图最多支持刷出5只契灵，测试功能，未完成")
        _resource_list = ["start"]
        while self.n < self.max:
            scene, coor = check_scene_multiple_once(_resource_list, self.resource_path)
            if scene is None:
                continue
            self.scene_print(scene)
            match scene:
                # case "title":
                # pass
                case "start":
                    Timer(5, self.timer_start).start()
                    # _timestamp = int(time.time())
                    # if _timestamp - self._timestamp < 3:
                    #     _flag_finish = True
                    #     continue
                    # else:
                    #     self._timestamp = _timestamp
                    click(coor)
                    random_sleep(1, 2)
                    self.fighting()
                    self.done()
                    random_sleep(2, 4)
            if self._flag_finish:
                log.ui("场上最多存在5只契灵，请及时清理")
                break
