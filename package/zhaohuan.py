#!/usr/bin/env python3
# zhaohuan.py
"""
普通召唤
"""

import time

from utils.function import function
from utils.log import log


class ZhaoHuan:
    """召唤"""

    def __init__(self) -> None:
        self.scene_name: str = "召唤"
        self.resource_path: str = "zhaohuan"  # 路径
        self.resource_list: list = [  # TODO resource check
            "title.png",  # 标题
            "putongzhaohuan.png",  # 普通召唤
            "zaicizhaohuan.png",  # 再次召唤
            "queding.png"  # 确定
        ]
        self.m: int = 0  # 当前次数
        self.n: int = None  # 总次数

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if function.judge_scene(f"{self.resource_path}/title.png", self.scene_name):
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def first(self) -> None:
        """第一次召唤"""
        function.judge_click(f"{self.resource_path}/putongzhaohuan.png")
        function.random_sleep(6, 8)

    def again(self) -> None:
        """非第一次召唤"""
        function.judge_click(f"{self.resource_path}/zaicizhaohuan.png")
        function.random_sleep(6, 8)

    def run(self, n: int) -> None:
        time.sleep(2)
        self.n = n
        flag = True  # 是否第一次
        time_progarm = function.TimeProgram()  # 程序计时
        time_progarm.start()
        if self.title():
            log.num(f"0/{self.n}")
            function.random_sleep(1, 3)
            while self.m < self.n:
                if flag:
                    self.first()
                    flag = False
                    self.m += 1
                else:
                    self.again()
                    self.m += 1
                log.num(f"{self.m}/{self.n}")
            # 结束
            if self.m == self.n:
                function.judge_click(f"{self.resource_path}/queding.png")
        text = f"已完成 普通召唤十连 {self.m}次"
        time_progarm.end()
        text = text + " " + time_progarm.print()
        log.info(text, True)
        # 启用按钮
        log.is_fighting(False)
