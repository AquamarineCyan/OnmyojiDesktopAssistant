#!/usr/bin/env python3
# huodong.py
"""
限时活动
"""

import time

from utils.function import function, time_consumption_statistics
from utils.log import log

"""
限时活动特征图像
title.png
挑战
tiaozhan.png
"""


class HuoDong:
    """限时活动"""

    def __init__(self) -> None:
        self.scene_name = "限时活动"
        self.resource_path = "huodong"  # 路径
        self.m = 0  # 当前次数
        self.n = None  # 总次数

    def title(self) -> None:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if function.judge_scene(f"{self.resource_path}/title.png", self.scene_name):
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def start(self):
        """挑战开始"""
        function.judge_click(f"{self.resource_path}/tiaozhan.png")

    @time_consumption_statistics
    def run(self, n: int) -> None:
        time.sleep(2)
        self.n = n
        # time_progarm = function.TimeProgram()  # 程序计时
        # time_progarm.start()
        if self.title():
            log.num(f"0/{self.n}")
            function.random_sleep(1, 3)
            while self.m < self.n:
                function.random_sleep(1, 2)
                # 开始
                self.start()
                # 结束
                function.result()
                function.random_sleep(1, 2)
                # 结算
                function.random_finish_left_right(is_yuling=True)
                function.random_sleep(1, 3)
                self.m += 1
                log.num(f"{self.m}/{self.n}")
        text = f"已完成 {self.scene_name} {self.m}次"
        # time_progarm.end()
        # text = text + " " + time_progarm.print()
        log.info(text, True)
        # 启用按钮
        log.is_fighting(False)
