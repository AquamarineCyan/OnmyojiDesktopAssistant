#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# qiling.py
"""契灵-探查"""

from threading import Timer

from ..utils.decorator import log_function_call, run_in_thread, time_count
from ..utils.function import (
    RESOURCE_FIGHT_PATH,
    check_finish_once,
    check_scene_multiple_once,
    click,
    finish_random_left_right,
    get_coor_info,
    random_sleep
)
from ..utils.log import log
from .utils import Package


class QiLing(Package):
    """契灵"""
    scene_name = "契灵"
    resource_path = "qiling"
    resource_list: list = [
        # "title",
        "start_tancha",
        "start_jieqi",
        "zhenmushou",
        "xiaohei",
        "huoling",
        "ciqiu",
    ]

    def __init__(self, n: int = 0, _flag_tancha: bool = True, _flag_jieqi: bool = False) -> None:
        super().__init__(n)
        self._flag_tancha = _flag_tancha
        self._flag_jieqi = _flag_jieqi
        self._flag_finish: bool = False
        self._flag_timer_jieqi_finish: bool = True
        # self._timestamp: int = int(time.time())

    @log_function_call
    def fighting(self):
        _flag_first: bool = False
        while True:
            if self._flag_finish:
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
        coor = get_coor_info(f"{self.resource_path}/start_tancha")
        if coor.is_effective:
            self._flag_finish = True

    @log_function_call
    def check_pokemon(self) -> bool:
        _resource_list: list = [
            "zhenmushou",
            "xiaohei",
            "huoling",
            "ciqiu",
        ]
        _, coor = check_scene_multiple_once(_resource_list, self.resource_path)
        if coor.is_zero:
            return False
        click(coor)
        return True

    @log_function_call
    def timer_jieqi_finish(self):
        coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")
        if coor.is_zero:
            self._flag_timer_jieqi_finish = False

    @log_function_call
    def run_tancha(self):
        log.ui("仅限探查，地图最多支持刷出5只契灵，测试功能，未完成")
        _resource_list = ["start_tancha"]
        while self.n < self.max:
            scene, coor = check_scene_multiple_once(_resource_list, self.resource_path)
            if scene is None:
                continue
            self.scene_print(scene)
            match scene:
                # case "title":
                # pass
                case "start_tancha":
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

    @log_function_call
    def run_jieqi(self):
        """结契"""
        log.ui("请先在游戏内设置“结契设置”")
        _n: int = 0
        _resource_list = ["start_tancha", "start_jieqi"]
        _flag_done_once: bool = False

        while _n <= 5:
            scene, coor = check_scene_multiple_once(_resource_list, self.resource_path)
            if scene is None:
                continue
            self.scene_print(scene)

            match scene:
                case "start_tancha":
                    if _flag_done_once:
                        _flag_done_once = False
                        _n += 1
                        log.ui(f"结契第{_n}只成功")
                    if not self.check_pokemon():
                        break
                    random_sleep(1, 2)
                    continue
                case "start_jieqi":
                    click(coor)
                    random_sleep(10, 11)
                    _flag_first: bool = False
                    _timer = Timer(2 * 60, self.timer_jieqi_finish)
                    _timer.start()

                    while True:
                        if not self._flag_timer_jieqi_finish:
                            # TODO 需要识别其他罗盘点击
                            log.warn("没有足够的指定的罗盘")

                        if check_finish_once():
                            _flag_first = True
                            _timer.cancel()
                            random_sleep(0.5, 0.8)
                            finish_random_left_right()
                        elif _flag_first:
                            _flag_done_once = True
                            random_sleep(2, 3)
                            break

    @run_in_thread
    @time_count
    @log_function_call
    def run(self):
        if self._flag_tancha:
            self.run_tancha()
        if self._flag_jieqi:
            self.run_jieqi()
