#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# qiling.py
"""契灵"""

from ..utils.coordinate import RelativeCoor
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import (
    RESOURCE_FIGHT_PATH,
    check_finish_once,
    check_scene_multiple_once,
    click,
    finish_random_left_right,
    get_coor_info,
    random_sleep
)
from ..utils.log import logger
from ..utils.mythread import WorkTimer
from .utils import Package


class QiLing(Package):
    """契灵"""
    scene_name = "契灵"
    resource_path = "qiling"
    resource_list: list = [
        "start_tancha",
        "start_jieqi",
    ]
    description = "次数为探查次数，选中“结契”按钮将在探查结束后自动挑战场上所有，地图最多支持刷出5只契灵，请提前在游戏内配置“结契设置”"

    @log_function_call
    def __init__(self, n: int = 0, _flag_tancha: bool = True, _flag_jieqi: bool = False) -> None:
        super().__init__(n)
        self._flag_tancha = _flag_tancha
        self._flag_jieqi = _flag_jieqi
        self._flag_finish: bool = False
        self._flag_timer_jieqi_finish: bool = True
        self._pokemon_address_count: int = 0
        # self._timestamp: int = int(time.time())

    @log_function_call
    def fighting(self):
        _flag_first: bool = False
        while True:
            if event_thread.is_set():
                return
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
        coor = self.get_coor_info("start_tancha")
        if coor.is_effective:
            self._flag_finish = True

    @log_function_call
    def check_pokemon(self) -> bool:
        """判断5个契灵小图标的固定点位"""
        _pokemon_list = [
            RelativeCoor(220, 528),
            RelativeCoor(378, 485),
            RelativeCoor(635, 505),
            RelativeCoor(815, 484),
            RelativeCoor(935, 490),
        ]
        # 遍历5个固定点位
        for i in range(self._pokemon_address_count, 5):
            logger.info(f"_pokemon_address_count: {self._pokemon_address_count}")
            click(_pokemon_list[i])
            self._pokemon_address_count += 1
            random_sleep(2)
            coor = self.get_coor_info("start_jieqi")
            if coor.is_effective:
                return True
            else:
                continue
        return False

    @log_function_call
    def timer_jieqi_finish(self):
        coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")
        if coor.is_zero:
            self._flag_timer_jieqi_finish = False

    @log_function_call
    def run_tancha(self):
        _resource_list = ["start_tancha"]
        while self.n < self.max:
            if event_thread.is_set():
                return
            scene, coor = check_scene_multiple_once(_resource_list, self.resource_path)
            scene = self.scene_handle(scene)
            
            match scene:
                # case "title":
                # pass
                case "start_tancha":
                    WorkTimer(5, self.timer_start).start()
                    # _timestamp = int(time.time())
                    # if _timestamp - self._timestamp < 3:
                    #     _flag_finish = True
                    #     continue
                    # else:
                    #     self._timestamp = _timestamp
                    click(coor)
                    random_sleep()
                    self.fighting()
                    self.done()
                    random_sleep(2, 4)
            if self._flag_finish:
                logger.ui("场上最多存在5只契灵，请及时清理")
                break

    @log_function_call
    def run_jieqi(self):
        """结契"""
        _n: int = 0
        self.current_resource_list = ["start_tancha", "start_jieqi"]
        _flag_done_once: bool = False

        while _n <= 5:
            if event_thread.is_set():
                return
            scene, coor = self.check_scene_multiple_once()
            if scene is None:
                continue
            scene = self.scene_handle(scene)

            match scene:
                # 确保在探查界面点击契灵小图标
                case "start_tancha":
                    logger.scene("契灵之境")
                    if _flag_done_once:
                        _flag_done_once = False
                        _n += 1
                        logger.ui(f"结契第{_n}只成功")
                    if not self.check_pokemon():
                        break
                    random_sleep()
                    continue
                case "start_jieqi":
                    logger.scene("契灵探查")
                    click(coor)
                    random_sleep(10)
                    _flag_first: bool = False
                    _timer = WorkTimer(2 * 60, self.timer_jieqi_finish)
                    _timer.start()

                    while True:
                        if not self._flag_timer_jieqi_finish:
                            # TODO 需要识别其他罗盘点击
                            logger.ui("没有足够的指定的罗盘", "warn")

                        if check_finish_once():
                            _flag_first = True
                            _timer.cancel()
                            random_sleep(0.5, 0.8)
                            finish_random_left_right()
                        elif _flag_first:
                            _flag_done_once = True
                            random_sleep(2)
                            break

    def run(self):
        if self._flag_tancha:
            self.run_tancha()
        if self._flag_jieqi:
            self.run_jieqi()
