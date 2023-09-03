#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# xuanshangfengyin.py
"""悬赏封印"""

import time

from ..utils.config import config
from ..utils.decorator import log_function_call, run_in_thread
from ..utils.event import event_thread, event_xuanshang, event_xuanshang_enable
from ..utils.function import click, get_coor_info_center
from ..utils.log import logger
from ..utils.toast import toast


class XuanShangFengYin:
    """悬赏封印"""

    def __init__(self):
        self.scene_name: str = "悬赏封印"
        self.resource_path: str = "xuanshangfengyin"  # 图片路径
        self._flag_is_first: bool = True
        self._flag: bool = False
        event_xuanshang_enable.set()  # 启用
        self.resource_list: list = [
            "title",  # 特征图像
            "xuanshang_accept",  # 接受
            "xuanshang_refuse",  # 拒绝
            "xuanshang_ignore"  # 忽略
        ]

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

    @log_function_call
    @run_in_thread
    def run(self) -> None:
        logger.info("悬赏封印进行中...")
        # 第一次进入，确保不会阻塞function.get_coor_info()
        if self._flag_is_first:
            event_xuanshang.set()
            self._flag_is_first = False

        while True:
            coor = get_coor_info_center(f"{self.resource_path}/title.png", is_log=False)
            if coor.is_effective:
                logger.scene("悬赏封印")
                event_xuanshang.clear()
                self._flag = True
                logger.ui("已暂停后台线程，等待处理", "warn")
                match config.config_user.get("悬赏封印"):
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
            time.sleep(1)


xuanshangfengyin = XuanShangFengYin()
