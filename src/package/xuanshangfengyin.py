#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# xuanshangfengyin.py
"""悬赏封印"""

import time

from ..utils.config import config
from ..utils.decorator import log_function_call, run_in_thread
from ..utils.event import event_xuanshang, event_xuanshang_enable
from ..utils.function import click, get_coor_info_center
from ..utils.log import log, logger
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

    def check_click(self, file: str) -> None:
        """图像识别，并点击

        参数:
            file (str): 文件路径&图像名称(*.png)
        """
        while True:
            coor = get_coor_info_center(f"{self.resource_path}/{file}", is_log=False)
            if coor.is_effective:
                click(coor)

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
                if not self._flag:
                    log.scene("悬赏封印")
                    event_xuanshang.clear()
                    self._flag = True
                    log.warn("已暂停后台线程，等待处理", True)
                    logger.info(f"event_xuanshang by coor_effective: {event_xuanshang.is_set()}")
                    match config.config_user.get("悬赏封印"):
                        case "接受":
                            log.ui("接受协作")
                            self.check_click("xuanshang_accept.png")
                        case "拒绝":
                            log.ui("拒绝协作")
                            self.check_click("xuanshang_refuse.png")
                        case "忽略":
                            log.ui("忽略协作")
                            self.check_click("xuanshang_ignore.png")
                        case _:
                            log.ui("用户配置出错，自动接受协作")
                            self.check_click("xuanshang_accept.png")
                    event_xuanshang.set()
                    toast("悬赏封印", "检测到协作")
            else:
                event_xuanshang.set()
                if self._flag:
                    self._flag = False
                    log.ui("悬赏封印已消失，恢复线程")
                    logger.info(f"event_xuanshang by coor_zero: {event_xuanshang.is_set()}")
            time.sleep(1)


xuanshangfengyin = XuanShangFengYin()
