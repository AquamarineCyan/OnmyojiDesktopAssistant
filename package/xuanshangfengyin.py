#!usr/bin/env python3
# xuanshangfengyin.py
"""
悬赏封印
"""

from pathlib import Path
import time
import pyautogui
import random

from utils.config import config
from utils.event import event_xuanshang
from utils.log import log
from utils.window import window
from utils.toaster import toaster


class XuanShangFengYin:
    """悬赏封印"""

    def __init__(self) -> None:
        self.scene_name = "悬赏封印"
        self.resource_path = "xuanshangfengyin"  # 图片路径
        self.m = None
        self._flag_is_first: bool = True
        self._flag: bool = False

    def event_is_set(self) -> bool:
        return event_xuanshang.is_set()

    def event_wait(self) -> None:
        event_xuanshang.wait()

    def get_coor_info_picture(self, file: str):
        """
        图像识别，返回图像的全屏随机坐标

        :param file: 文件路径&图像名称(*.png)
        :return: 识别成功，返回图像的随机坐标，识别失败，返回(0,0)
        """
        # filename: str = fr'./pic/{file}'
        filename = config.resource_path / file
        if isinstance(filename, Path):
            filename = str(filename)
        x = y = 0
        try:
            button_location = pyautogui.locateCenterOnScreen(
                filename,
                region=(
                    window.window_left,
                    window.window_top,
                    window.absolute_window_width,
                    window.absolute_window_height
                ),
                confidence=0.8
            )
            x, y = button_location
        except:
            pass
        finally:
            return x, y

    def judge_click(self, file: str) -> None:
        """
        图像识别，并点击

        :param pic: 文件路径&图像名称(*.png)
        :return: None
        """
        while True:
            x, y = self.get_coor_info_picture(file)
            if x != 0 and y != 0:
                # 补间移动，默认启用
                list_tween = [
                    pyautogui.easeInQuad,
                    pyautogui.easeOutQuad,
                    pyautogui.easeInOutQuad
                ]
                random.seed(time.time_ns())
                pyautogui.moveTo(
                    x,
                    y,
                    duration=0.25,
                    tween=list_tween[random.randint(0, 2)]
                )
                pyautogui.click()
                log.info("定位成功", True)
                return

    def judge(self) -> None:
        log.info("悬赏封印进行中...")
        while True:
            if self._flag_is_first:
                event_xuanshang.set()
                self._flag_is_first = False
            x, y = self.get_coor_info_picture(
                f"{self.resource_path}/title.png")
            if x != 0 and y != 0:
                if not self._flag:
                    log.scene("悬赏封印")
                    event_xuanshang.clear()
                    self._flag = True
                    log.warn("已暂停后台线程，等待处理", True)
                    toaster("悬赏封印", "检测到协作")
                    print(event_xuanshang.is_set())
                    match config.xuanshangfengyin_receive:
                        case "接受":
                            log.ui("自动接受协作")
                            # log.info("当前版本下，自动接受任何协作", True)
                            self.judge_click(
                                f"{self.resource_path}/xuanshang_accept.png")
                        case "拒绝":
                            log.ui("自动拒绝协作")
                            self.judge_click(
                                f"{self.resource_path}/xuanshang_refuse.png")
                        case "忽略":
                            log.ui("自动忽略协作")
                            self.judge_click(
                                f"{self.resource_path}/xuanshang_ignore.png")
                        case _:
                            log.ui("用户配置出错，自动接受协作")
                            self.judge_click(
                                f"{self.resource_path}/xuanshang_accept.png")
            else:
                event_xuanshang.set()
                if self._flag:
                    self._flag = False
                    log.info("悬赏封印已消失，恢复线程", True)
                    print(event_xuanshang.is_set())


xuanshangfengyin = XuanShangFengYin()
