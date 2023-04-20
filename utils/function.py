#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# function.py
"""通用函数库"""

import pyautogui
import random
import time

from pathlib import Path

from .config import config
from .decorator import *
from .log import log
from .window import window
from package.xuanshangfengyin import xuanshangfengyin


class Function:
    """通用函数"""

    def __init__(self) -> None:
        self.application_path: Path = config.application_path
        self.resource_path: Path = config.resource_path  # 资源路径
        self.screenshot_window_width: int = 1138  # 截图宽度
        self.screenshot_window_height: int = 679  # 截图高度

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

    def _image_file_format(self, file: Path | str) -> str:
        """补全图像文件后缀并转为`str`

        `pyautogui` need file path be `str`

        参数:
            file (Path | str): file

        返回:
            str: filename
        """
        if isinstance(file, str):
            if file[-4:] not in [".png", ".jpg"]:
                _file = f"{file}.png"
            else:
                _file = file
        elif isinstance(file, Path):
            if file.__str__()[-4:] not in [".png", ".jpg"]:
                _file = f"{file.__str__()}.png"
            else:
                _file = file.__str__()
        if Path(config.resource_path / _file).exists():
            return _file
        else:
            log.warn(f"no such file {_file}")

    def get_coor_info_picture(self, file: str) -> tuple[int, int]:
        """图像识别，返回图像的全屏随机坐标

        Args:
            file (str): 文件路径&图像名称(*.png)

        Returns:
            tuple[int, int]: 识别成功，返回图像的随机坐标；识别失败，返回(0,0)
        """
        # TODO 兼容Pathlib
        # filename: str = fr'./pic/{file}'
        # filename = self.resource_path / file
        # log.info(filename)
        # if isinstance(filename, Path):
        # filename = str(filename)
        # print("test", xuanshangfengyin.event_is_set())
        file = self.resource_path/file
        filename = self._image_file_format(file)
        log.info(filename)
        # 等待悬赏封印判定
        xuanshangfengyin.event_wait()
        try:
            button_location = pyautogui.locateOnScreen(
                filename, region=(
                    window.window_left,
                    window.window_top,
                    window.absolute_window_width,
                    window.absolute_window_height
                ),
                confidence=0.8
            )
            log.info(f"button_location:{button_location}")
            x, y = self.random_coor(
                button_location[0],
                button_location[0] + button_location[2],
                button_location[1],
                button_location[1] + button_location[3]
            )
        except:
            x = y = 0
        finally:
            log.info(f"random_coor_x_y:{x},{y}")
            return x, y

    def judge_scene(self, file: str, scene_name: str = None) -> bool:
        """场景判断

        Args:
            file (str): 文件路径&图像名称(*.png)
            scene_name (str, optional): 场景描述. Defaults to None.

        Returns:
            bool: 是否为指定场景
        """
        while True:
            x, y = self.get_coor_info_picture(file)
            if x != 0 and y != 0:
                if scene_name is not None:
                    log.scene(scene_name)
                return True
            else:
                return False

    # TODO
    def check_scene_multiple_once(self, scene: dict | list, resource_path: str = None) -> tuple[str, tuple[int, int]]:
        """多场景判断，仅遍历一次

        Args:
            scene (dict | list): _description_
            resource_path (str, optional): _description_. Defaults to None.

        Returns:
            tuple[str, tuple[int, int]]: _description_
        """
        # scene = {
        #     "tansuo_28_title.png": "少女与面具",
        #     "chuzhanxiaohao.png": "出战消耗"
        # }
        if isinstance(scene, dict):
            for item in scene.keys():
                if resource_path is not None:
                    file = f"{self.resource_path}/{item}"
                else:
                    file = item
                x, y = self.get_coor_info_picture(file)
                if x != 0 and y != 0:
                    return scene[item], (x, y)
        elif isinstance(scene, list):
            for item in range(len(scene)):
                # log.ui(scene[item])
                x, y = self.get_coor_info_picture(
                    f"{resource_path}/{scene[item]}"
                )
                if x != 0 and y != 0:
                    return scene[item], (x, y)
            return "none", (0, 0)

    def check_scene_multiple_while(self, scene: dict | list, resource_path: str = None) -> tuple[str, tuple[int, int]]:
        """多场景判断，循环遍历，直至符合任意一个场景"""
        while True:
            scene, (x, y) = self.check_scene_multiple_once(self, scene, resource_path)
            if x != 0 and y != 0:
                return scene, (x, y)

    def click(self, x: int, y: int, dura: float = 0.5, sleeptime: float = 0.0):
        # 延迟
        if sleeptime is not None:
            time.sleep(sleeptime)
        # 补间移动，默认启用
        list_tween = [
            pyautogui.easeInQuad,
            pyautogui.easeOutQuad,
            pyautogui.easeInOutQuad
        ]
        # XXX random for list
        random.seed(time.time_ns())
        pyautogui.moveTo(
            x,
            y,
            duration=dura,
            tween=list_tween[random.randint(0, 2)]
        )
        log.info(f"complete for (x,y):({x},{y})")
        pyautogui.click()

    def judge_click(
        self,
        file: str,
        click: bool = True,
        dura: float = 0.5,
        sleeptime: float = 0.0
    ) -> None:
        """图像识别，并点击

        Args:
            file (str): 文件路径&图像名称(*.png)
            click (bool, optional): 是否点击. Defaults to True.
            dura (float, optional): 移动速度. Defaults to 0.5.
            sleeptime (float, optional): 延迟时间. Defaults to 0.0.
        """
        # TODO use "identify" to replace "judge" in function name
        flag = False
        while True:
            x, y = self.get_coor_info_picture(file)
            if x != 0 and y != 0:
                if click:
                    self.click(x, y, dura, sleeptime)
                    # # 延迟
                    # if sleeptime is not None:
                    #     time.sleep(sleeptime)
                    # # 补间移动，默认启用
                    # list_tween = [
                    #     pyautogui.easeInQuad,
                    #     pyautogui.easeOutQuad,
                    #     pyautogui.easeInOutQuad
                    # ]
                    # # XXX random for list
                    # random.seed(time.time_ns())
                    # pyautogui.moveTo(
                    #     x,
                    #     y,
                    #     duration=dura,
                    #     tween=list_tween[random.randint(0, 2)]
                    # )
                    # log.info(f"x,y:{x},{y}")
                    # pyautogui.click()
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

    def random_finish_left_right(
            self,
            click: bool = True,
            is_multiple_drops_y: bool = False,
            is_multiple_drops_x: bool = False
    ) -> tuple[int, int]:
        """图像识别，返回图像的局部相对坐标

        参数:
            click (bool): 鼠标点击,默认是
            is_multiple_drops_y (bool): 多掉落纵向区域,默认否
            is_multiple_drops_x (bool): 多掉落横向区域,默认否

        返回:
            tuple[int, int]: 局部随机坐标(x, y)
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
        if is_multiple_drops_y:
            finish_y2 = finish_y2 - 200
        if is_multiple_drops_x:
            finish_left_x2 = 70
            finish_right_x1 = 1070
        # 获取系统当前时间戳
        random.seed(time.time_ns())
        if random.random() * 10 > 5:
            x, y = self.random_coor(
                finish_left_x1,
                finish_left_x2,
                finish_y1,
                finish_y2
            )
        else:
            x, y = self.random_coor(
                finish_right_x1,
                finish_right_x2,
                finish_y1,
                finish_y2
            )
        if click:
            pyautogui.moveTo(
                x + window.window_left,
                y + window.window_top,
                duration=0.5
            )
            pyautogui.click()
        return x, y

    def screenshot(self, screenshotpath: str = "cache") -> bool:
        """截图

        参数:
            screenshotpath (str): 截图文件存放路径，默认"cache".

        返回:
            bool: 截图成功或失败
        """

        window_width_screenshot = 1138  # 截图宽度
        window_height_screenshot = 679  # 截图高度
        self.screenshotpath = self.application_path / screenshotpath
        self.screenshotpath.mkdir(parents=True, exist_ok=True)

        file = f"{screenshotpath}/screenshot-{time.strftime('%Y%m%d%H%M%S')}.png"
        try:
            pyautogui.screenshot(
                imageFilename=file,
                region=(
                    window.window_left - 1,
                    window.window_top,
                    window_width_screenshot,
                    window_height_screenshot
                )
            )
            log.info(f"screenshot at {file}")
            return True
        except:
            log.error("screenshot failed.")
            return False

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


function = Function()
