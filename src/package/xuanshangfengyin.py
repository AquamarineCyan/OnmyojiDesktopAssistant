#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# xuanshangfengyin.py
"""悬赏封印"""

import time

from ..utils.config import config
from ..utils.decorator import run_in_thread
from ..utils.event import event_thread, event_xuanshang, event_xuanshang_enable
from ..utils.function import click, get_coor_info_center
from ..utils.log import logger
from ..utils.toast import toast
from .utils import Package


class XuanShangFengYin(Package):
    """悬赏封印"""
    scene_name = "悬赏封印"
    resource_path = "xuanshangfengyin" 
    resource_list: list = [
        "title",  # 特征图像
        "xuanshang_accept",  # 接受
        "xuanshang_refuse",  # 拒绝
        "xuanshang_ignore",  # 忽略
    ]

    def __init__(self):
        self._flag_is_first: bool = True
        self._flag: bool = False
        event_xuanshang_enable.set()  # 启用

    def check_click(self, file: str, timeout: int = None) -> None:
        """图像识别，并点击

        参数:
            file (str): 文件路径&图像名称（*.png）
            timeout (int): 超时时间（秒）
        """
        if timeout:
            start_time = time.time()
        while True:
            if event_thread.is_set():
                return
            if timeout:
                current_time = time.time()
                if current_time - start_time > timeout:
                    return

            coor = get_coor_info_center(f"{self.resource_path}/{file}", is_log=False)
            if coor.is_effective:
                click(coor)
                return

    def run(self) -> None:
        logger.info("悬赏封印进行中...")
        # 第一次进入，确保不会阻塞function.get_coor_info()
        if self._flag_is_first:
            event_xuanshang.set()
            self._flag_is_first = False

        while True:
            coor = get_coor_info_center(f"{self.resource_path}/title.png", is_log=False)
            if coor.is_effective:
                logger.scene(self.scene_name)
                event_xuanshang.clear()
                self._flag = True
                logger.ui("已暂停后台线程，等待处理", "warn")
                match config.config_user.xuanshangfengyin:
                    case "接受":
                        logger.ui("接受协作")
                        self.check_click("xuanshang_accept.png", 5)
                    case "拒绝":
                        logger.ui("拒绝协作")
                        self.check_click("xuanshang_refuse.png", 5)
                    case "忽略":
                        logger.ui("忽略协作")
                        self.check_click("xuanshang_ignore.png", 5)
                    case _:
                        logger.ui("用户配置出错，自动接受协作")
                        self.check_click("xuanshang_accept.png", 5)
                event_xuanshang.set()
                toast("悬赏封印", "检测到协作")
            else:
                event_xuanshang.set()
                if self._flag:
                    self._flag = False
                    logger.ui("悬赏封印已消失，恢复线程")
            time.sleep(0.1)

    @run_in_thread
    def task_start(self):
        self.run()

task_xuanshangfengyin = XuanShangFengYin()
