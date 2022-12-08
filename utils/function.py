#!usr/bin/env python3
# function.py
"""
通用函数库
"""

import random
import time
from pathlib import Path

import pyautogui

from package.xuanshangfengyin import XuanShangFengYin

from . import window
from .log import log


class Function:
    """通用函数"""

    """ 
    def __init__(self):
        self.window_width_screenshot = 1138  # 截图宽度
        self.window_height_screenshot = 679  # 截图高度
    """

    def random_num(self, minimum: int, maximun: int) -> int:
        """返回给定范围的随机值

        Args:
            minimum (int): 下限（包含）
            maximun (int): 上限（不含）

        Returns:
            int: 随机值
        """
        # 获取系统当前时间戳
        random.seed(time.time_ns())
        return random.random() * (maximun - minimum) + minimum

    def random_coor(self, x1: int, x2: int, y1: int, y2: int) -> tuple[int, int]:
        """伪随机坐标，返回给定坐标区间的随机值

        Args:
            x1 (int): 左侧横坐标
            x2 (int): 右侧横坐标
            y1 (int): 顶部纵坐标
            y2 (int): 底部纵坐标

        Returns:
            tuple[int, int]: 矩形区域内随机值
        """
        # TODO 返回坐标偏中心
        x = self.random_num(x1, x2)
        y = self.random_num(y1, y2)
        return x, y

    def get_coor_info_picture(self, pic: str) -> tuple[int, int]:
        """图像识别，返回图像的全屏随机坐标

        Args:
            pic (str): 文件路径&图像名称(*.png)

        Returns:
            tuple[int, int]: 识别成功，返回图像的随机坐标；识别失败，返回(0,0)
        """
        filename: str = fr'./pic/{pic}'
        # print("test", XuanShangFengYin().event_is_set())
        # 等待悬赏封印判定
        XuanShangFengYin().event_wait()
        try:
            button_location = pyautogui.locateOnScreen(filename, region=(
                window.window_left, window.window_top, window.absolute_window_width, window.absolute_window_height),
                confidence=0.8)
            log.info(f"button_location:{button_location}")
            x, y = self.random_coor(button_location[0], button_location[0] + button_location[2], button_location[1],
                                    button_location[1] + button_location[3])
        except:
            x = y = 0
        finally:
            log.info(f"random_coor_x_y:{x},{y}")
            return x, y

    def judge_scene(self, pic: str, scene_name: str = None) -> bool:
        """场景判断

        Args:
            pic (str): 文件路径&图像名称(*.png)
            scene_name (str, optional): 场景描述. Defaults to None.

        Returns:
            bool: 是否为指定场景
        """
        while True:
            x, y = self.get_coor_info_picture(pic)
            if x != 0 and y != 0:
                if scene_name is not None:
                    log.scene(scene_name)
                return True
            else:
                return False

    def judge_click(self, pic: str, click: bool = True, dura: float = 0.5, sleeptime: float = 0.0) -> None:
        """图像识别，并点击

        Args:
            pic (str): 文件路径&图像名称(*.png)
            click (bool, optional): 是否点击. Defaults to True.
            dura (float, optional): 移动速度. Defaults to 0.5.
            sleeptime (float, optional): 延迟时间. Defaults to 0.0.
        """
        flag = False
        while True:
            x, y = self.get_coor_info_picture(pic)
            if x != 0 and y != 0:
                if click:
                    # 延迟
                    if sleeptime is not None:
                        time.sleep(sleeptime)
                    # 补间移动，默认启用
                    list_tween = [pyautogui.easeInQuad,
                                  pyautogui.easeOutQuad, pyautogui.easeInOutQuad]
                    random.seed(time.time_ns())
                    pyautogui.moveTo(x, y, duration=dura,
                                     tween=list_tween[random.randint(0, 2)])
                    log.info(f"x,y:{x},{y}")
                    pyautogui.click()
                log.info("move to right coor successfully")
                time.sleep(1)
                flag = True
                return
            # elif (x == 0 or y == 0) and flag:
            # log.info("等待加载", True)
            # return

    def random_sleep(self, m: int, n: int) -> None:
        """随机延时(s)

        Args:
            m (int): 左区间（含）
            n (int): 右区间（不含）
        """
        time.sleep(self.random_num(m, n))

    def result(self) -> bool:
        """结果判断

        Returns:
            bool: Success or failure
        """
        log.info("result judgment")
        while True:
            x, y = self.get_coor_info_picture("victory.png")
            if x != 0 and y != 0:
                log.info("胜利", True)
                return True
            x, y = self.get_coor_info_picture("yuhun/victory_2000.png")
            if x != 0 and y != 0:
                log.ui("胜利，2000天御魂背景")
                return True
            x, y = self.get_coor_info_picture("fail.png")
            if x != 0 and y != 0:
                log.info("失败", True)
                return False

    def random_finish_left_right(self, click: bool = True, is_yuling: bool = False) -> tuple[int, int]:
        """结算界面伪随机点击区域

        Args:
            click (bool, optional): 鼠标点击. Defaults to True.
            is_yuling (bool, optional): 是否为御灵. Defaults to False.

        Returns:
            tuple[int, int]: 局部随机坐标
        """
        # 绝对坐标
        finish_left_x1 = 20
        """左侧可点击区域x1"""
        finish_left_x2 = 220
        """左侧可点击区域x2"""
        finish_right_x1 = 950
        """右侧可点击区域x1"""
        finish_right_x2 = 1100
        """右侧可点击区域x2"""
        finish_y1 = 190
        """可点击区域y1"""
        finish_y2 = 570
        """可点击区域y2"""
        x: int
        y: int
        if is_yuling:
            finish_y2 = finish_y2 - 200
        # 获取系统当前时间戳
        random.seed(time.time_ns())
        if random.random() * 10 > 5:
            x, y = self.random_coor(
                finish_left_x1, finish_left_x2, finish_y1, finish_y2)
        else:
            x, y = self.random_coor(
                finish_right_x1, finish_right_x2, finish_y1, finish_y2)
        if click:
            pyautogui.moveTo(x + window.window_left, y + window.window_top,
                             duration=0.5)
            pyautogui.click()
        return x, y

    def screenshot(self, screenshotpath: str) -> None:
        """截图

        Args:
            screenshotpath (str): 截图存放路径
        """
        window_width_screenshot = 1138  # 截图宽度
        window_height_screenshot = 679  # 截图高度
        # screenshotpath = "cache_baiguiyexing"  # 截图路径
        fpath = Path.cwd()
        filepath = fpath / screenshotpath
        if not filepath.exists():
            filepath.mkdir()
        picname = f"{screenshotpath}./screenshot-{time.strftime('%Y%m%d%H%M%S')}.png"
        pyautogui.screenshot(imageFilename=picname, region=(
            window.window_left - 1, window.window_top, window_width_screenshot, window_height_screenshot))

    class TimeProgram:
        """程序耗时统计"""

        def start(self) -> None:
            self._time_program_start = time.perf_counter()

        def end(self) -> None:
            self._time_program_end = time.perf_counter()

        def print(self) -> str:
            try:
                if (self._time_program_end - self._time_program_start) >= 60:
                    return f"耗时{int((self._time_program_end - self._time_program_start) // 60)}分{int((self._time_program_end - self._time_program_start) % 60)}秒"
                else:
                    return f"耗时{int(self._time_program_end - self._time_program_start)}秒"
            except:
                return ""

    # 未启用
    '''
    def fighting(self):
        """战斗场景"""

        def ready(self):
            """准备"""
            self.judge_click('zhunbei.png')

        def finish(self):
            self.result()
            x, y = self.random_finish_left_right()
    '''
