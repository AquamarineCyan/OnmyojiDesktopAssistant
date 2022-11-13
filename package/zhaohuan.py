#!/usr/bin/env python3
# zhaohuan.py
"""
普通召唤
"""

from pathlib import Path
import time

from utils.function import Function
from utils.log import log

"""
标题
title.png
普通召唤
putongzhaohuan.png
再次召唤
zaicizhaohuan.png
确定
queding.png
"""
piclist = [
    "title.png",  # 标题
    "putongzhaohuan.png",  # 普通召唤
    "zaicizhaohuan.png",  # 再次召唤
    "queding.png"  # 确定
]


class ZhaoHuan(Function):
    """召唤"""

    def __init__(self):
        self.scene_name = "召唤"
        self.picpath = "zhaohuan"  # 路径
        self.piclist = [
            "title.png",  # 标题
            "putongzhaohuan.png",  # 普通召唤
            "zaicizhaohuan.png",  # 再次召唤
            "queding.png"  # 确定
        ]
        self.m = 0  # 当前次数
        self.n = None  # 总次数

    def title(self):
        """场景"""
        flag_title = True  # 场景提示
        log.info(Path.cwd())
        log.info(f"looking for {self.picpath}/title.png")
        log.info(Path(f"{self.picpath}/title.png"))
        while 1:
            if self.judge_scene(f"{self.picpath}/title.png", self.scene_name):
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def first(self):
        """第一次召唤"""
        self.judge_click(f"{self.picpath}/putongzhaohuan.png")
        self.random_sleep(6, 8)

    def again(self):
        """非第一次召唤"""
        self.judge_click(f"{self.picpath}/zaicizhaohuan.png")
        self.random_sleep(6, 8)

    def run(self, n: int):
        time.sleep(2)
        self.n = n
        flag = True  # 是否第一次
        time_progarm = self.TimeProgram()  # 程序计时
        time_progarm.start()
        if self.title():
            log.num(f"0/{self.n}")
            self.random_sleep(1, 3)
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
                self.judge_click(f"{self.picpath}/queding.png")
        text = f"已完成 普通召唤十连{self.m}次"
        time_progarm.end()
        text = text + " " + time_progarm.print()
        log.info(text, True)
        # 启用按钮
        log.is_fighting(False)
