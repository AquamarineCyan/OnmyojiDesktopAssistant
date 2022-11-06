#!usr/bin/env python3
# xuanshangfengyin.py
"""
悬赏封印
"""

import time
import pyautogui
import random

from . import window
from utils.mysignal import global_ms as ms
from utils.event import event_xuanshang


class XuanShangFengYin:
    """悬赏封印"""

    def __init__(self) -> None:
        self.picpath = 'xuanshangfengyin'  # 图片路径
        self.m = None
        self._flag_is_first :bool = True
        self._flag: bool = False


    def event_is_set(self) -> bool:
        return event_xuanshang.is_set()

    def event_wait(self) -> None:
        event_xuanshang.wait()

    def get_coor_info_picture(self, pic: str):
        """
        图像识别，返回图像的全屏随机坐标

        :param pic: 文件路径&图像名称(*.png)
        :return: 识别成功，返回图像的随机坐标，识别失败，返回(0,0)
        """
        filename: str = fr'./pic/{pic}'
        x = y = 0
        try:
            button_location = pyautogui.locateCenterOnScreen(filename, region=(
                window.window_left, window.window_top, window.absolute_window_width, window.absolute_window_height),
                                                             confidence=0.8)
            x, y = button_location
        except:
            pass
        finally:
            return x, y

    def judge_click(self, pic: str):
        """
        图像识别，并点击

        :param pic: 文件路径&图像名称(*.png)
        :return: None
        """
        while 1:
            x, y = self.get_coor_info_picture(pic)
            if x != 0 and y != 0:
                # 补间移动，默认启用
                list_tween = [pyautogui.easeInQuad, pyautogui.easeOutQuad, pyautogui.easeInOutQuad]
                random.seed(time.time_ns())
                pyautogui.moveTo(x, y, duration=0.25, tween=list_tween[random.randint(0, 2)])
                pyautogui.click()
                ms.text_print_update.emit('定位成功')
                return


    def judge(self) -> None:
        while 1:
            if self._flag_is_first:
                event_xuanshang.set()
                self._flag_is_first = False
            x, y = self.get_coor_info_picture(f'{self.picpath}/title.png')
            if x != 0 and y != 0:
                if not self._flag:
                    ms.text_print_update.emit('[SCENE] 悬赏封印')
                    event_xuanshang.clear()
                    self._flag = True
                    ms.text_print_update.emit("[WARN] 已暂停后台线程，等待处理")
                    print(event_xuanshang.is_set())
                    ms.text_print_update.emit("当前版本下，自动接受任何协作")
                    self.judge_click(f'{self.picpath}/xuanshang_accept.png')
            else:
                event_xuanshang.set()
                if self._flag:
                    self._flag = False
                    ms.text_print_update.emit("悬赏封印已消失，恢复线程")
                    print(event_xuanshang.is_set())
