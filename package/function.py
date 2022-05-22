#!usr/bin/env python3
# function.py
"""
通用函数库
"""

import pyautogui
import random
import time
import pathlib

from . import window
from mysignal import global_ms as ms


class Function:
    """通用函数"""

    def random_num(self, minimum, maximun):
        """
        返回给定范围的随机值

        :param minimum: 下限
        :param maximun: 上限
        :return: 给定范围的随机值
        """
        # 获取系统当前时间戳
        random.seed(time.time_ns())
        return random.random() * (maximun - minimum) + minimum

    def random_coor(self, x1: int, x2: int, y1: int, y2: int):
        """
        伪随机坐标，返回给定坐标区间的随机值

        :param x1: 左侧横坐标
        :param x2: 右侧横坐标
        :param y1: 顶部纵坐标
        :param y2: 底部纵坐标
        :return: 区域内随机值
        """
        x = self.random_num(x1, x2)
        y = self.random_num(y1, y2)
        return x, y

    def get_coor_info_picture(self, pic: str):
        """
        图像识别，返回图像的全屏随机坐标

        :param pic: 文件路径&图像名称(*.png)
        :return: 识别成功，返回图像的随机坐标，识别失败，返回(0,0)
        """
        filename: str = fr'.\pic\{pic}'
        try:
            button_location = pyautogui.locateOnScreen(filename, region=(
                window.window_left, window.window_top, window.window_width, window.window_height), confidence=0.8)
            x, y = self.random_coor(button_location[0], button_location[0] + button_location[2], button_location[1],
                                    button_location[1] + button_location[3])
        except:
            x = y = 0
        finally:
            return x, y

    def judge_scene(self, pic: str, text: str = None):
        """
        场景判断

        :param pic: 文件路径&图像名称(*.png)
        :param text: 提示语
        :return: True or False
        """
        while 1:
            x, y = self.get_coor_info_picture(pic)
            if x != 0 and y != 0:
                if text is not None:
                    ms.text_print_update.emit(text)
                return True
            else:
                return False

    def judge_click(self, pic: str, click: bool = True, dura: float = 0.5, sleeptime: float = 0.0):
        """
        图像识别，并点击

        :param pic: 文件路径&图像名称(*.png)
        :param click: 是否点击（默认True）
        :param dura: 移动速度（默认0.25）
        :param sleeptime:延迟时间(float)
        :return: None
        """
        while 1:
            x, y = self.get_coor_info_picture(pic)
            if x != 0 and y != 0:
                if click:
                    # 延迟
                    if sleeptime is not None:
                        time.sleep(sleeptime)
                    # 补间移动，默认启用
                    list_tween = [pyautogui.easeInQuad, pyautogui.easeOutQuad, pyautogui.easeInOutQuad]
                    random.seed(time.time_ns())
                    pyautogui.moveTo(x, y, duration=dura, tween=list_tween[random.randint(0, 2)])
                    pyautogui.click()
                break

    def random_sleep(self, m: int, n: int):
        """
        随机延时区间m-n(s)

        :param m: 左区间（含）
        :param n: 右区间（不含）
        """
        time.sleep(self.random_num(m, n))

    def result(self):
        """
        结果判断

        :return: True or False
        """
        while 1:
            x, y = self.get_coor_info_picture('victory.png')
            if x != 0 and y != 0:
                ms.text_print_update.emit('胜利')
                return True
            x, y = self.get_coor_info_picture('fail.png')
            if x != 0 and y != 0:
                ms.text_print_update.emit('失败')
                return False

    def random_finish_left_right(self, click: bool = True, is_yuling: bool = False):
        """
        结算界面伪随机点击区域，返回局部随机坐标，单击全局坐标

        :return: x: 横坐标
                 y: 纵坐标
        """
        # 绝对坐标
        finish_left_x1 = 20
        '''左侧可点击区域x1'''
        finish_left_x2 = 240
        '''左侧可点击区域x2'''
        finish_right_x1 = 950
        '''右侧可点击区域x1'''
        finish_right_x2 = 1100
        '''右侧可点击区域x2'''
        finish_y1 = 190
        '''可点击区域y1'''
        finish_y2 = 570
        '''可点击区域y2'''
        x: int
        y: int
        # 获取系统当前时间戳
        random.seed(time.time_ns())
        if random.random() * 10 > 5:
            if is_yuling:
                x, y = self.random_coor(finish_left_x1, finish_left_x2, finish_y1, finish_y2 - 200)
            else:
                x, y = self.random_coor(finish_left_x1, finish_left_x2, finish_y1, finish_y2)
        else:
            if is_yuling:
                x, y = self.random_coor(finish_right_x1, finish_right_x2, finish_y1, finish_y2 - 200)
            else:
                x, y = self.random_coor(finish_right_x1, finish_right_x2, finish_y1, finish_y2)
        if click:
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
            pyautogui.click()
        return x, y

    # 未启用
    def fighting(self):
        """战斗场景"""

        def ready(self):
            """准备"""
            self.judge_click('zhunbei.png')

        def finish(self):
            self.result()
            x, y = self.random_finish_left_right()
