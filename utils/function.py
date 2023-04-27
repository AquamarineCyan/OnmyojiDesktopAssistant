#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# function.py
"""通用函数库"""

import pyautogui
import random
import time

from pathlib import Path

from .config import config
from .coordinate import Coor
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

    def random_num(self, minimum: int | float, maximum: int | float) -> float:
        """返回给定范围的随机值        

        参数:
            minimum (int | float): 最小值（含）
            maximum (int | float): 最大值（不含）

        返回:
            float: 随机值
        """
        # 获取系统当前时间戳
        random.seed(time.time_ns())
        return random.random() * (maximum - minimum) + minimum

    def random_coor(self, x1: int, x2: int, y1: int, y2: int) -> tuple[int, int]:
        """伪随机坐标，返回给定坐标区间的随机值

        参数:
            x1 (int): 左侧横坐标
            x2 (int): 右侧横坐标
            y1 (int): 顶部纵坐标
            y2 (int): 底部纵坐标

        返回:
            tuple[int, int]: 矩形区域内随机值 #TODO 适配`Coor`
        """
        # TODO 返回坐标偏中心
        x = self.random_num(x1, x2)
        y = self.random_num(y1, y2)
        log.info(f"random_coor: {x},{y}")
        return x, y

    def random_sleep(self, minimum: int | float, maximum: int | float):
        """随机延时（秒）

        参数:
            minimum (int): 最小值（含）
            maximum (int): 最大值（不含）
        """
        sleeptime = self.random_num(minimum, maximum)
        log.info(f"sleep for {sleeptime} seconds")
        time.sleep(sleeptime)

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

        # TODO 旧代码，使用新函数`get_coor_info()`
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
        if xuanshangfengyin.is_working():
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

    def get_coor_info(self, file: Path | str) -> Coor:
        """图像识别，返回图像的全屏随机坐标

        参数:
            file (str): 图像名称

        返回:
            Coor: 成功，返回图像的随机坐标；失败，返回(0,0)
        """
        _file_name = self._image_file_format(config.resource_path / file)
        log.info(_file_name)
        # 等待悬赏封印判定
        if xuanshangfengyin.is_working():
            xuanshangfengyin.event_wait()
        try:
            button_location = pyautogui.locateOnScreen(
                _file_name,
                region=(
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
            log.info(f"random_coor_x_y:{x},{y}")
            return Coor(x, y)
        except:
            return Coor(0, 0)

    def judge_scene(self, file: str, scene_name: str = None) -> bool:
        """场景判断

        Args:
            file (str): 图像文件
            scene_name (str): 场景描述

        返回:
            bool: 是否为指定场景
        """
        while True:
            coor = self.get_coor_info(file)
            if coor.is_effective:
                if scene_name:
                    log.scene(scene_name)
                return True
            else:
                return False

    def check_scene_multiple_once(self, scene: dict | list, resource_path: str = None) -> tuple[str, tuple[int, int]]:
        """多场景判断，仅遍历一次

        参数:
            scene (dict | list): 多场景列表
            resource_path (str): 路径

        返回:
            tuple[str, tuple[int, int]]: 场景名称,坐标 #TODO 适配`Coor`，涉及御魂副本
        """
        # XXX 移除对字典的适配
        if isinstance(scene, dict):
            for key, value in scene.items():
                if resource_path:
                    file = f"{self.resource_path}/{key}"
                else:
                    file = key
                coor = self.get_coor_info(file)
                if coor.is_effective:
                    return value, coor.coor
        elif isinstance(scene, list):
            for item in scene:
                coor = self.get_coor_info(f"{resource_path}/{item}")
                if coor.is_effective:
                    return item, coor.coor
            return None, (0, 0)

    def check_scene_multiple_while(self,
                                   scene: dict | list = None,
                                   resource_path: str = None,
                                   text: str = None
                                   ) -> tuple[str, tuple[int, int]]:
        """多场景判断，循环遍历，直至符合任意一个场景

        参数:
            scene (dict | list): 多场景列表
            resource_path (str): 路径 
            text (str): 提示

        返回:
            tuple[str, tuple[int, int]]: 场景名称, (x,y)
        """
        _flag: bool = True  # 提示
        _text = text if text else "请检查游戏场景"
        while True:
            scene, (x, y) = self.check_scene_multiple_once(self, scene, resource_path)
            if Coor(x, y).is_effective():
                log.info(f"{scene}, ({x},{y})")
                return scene, (x, y)
            elif _flag:
                _flag = False
                log.warn(_text, True)

    def click(self, x: int, y: int, dura: float = 0.5, sleeptime: float = 0.0):
        # 延迟
        if sleeptime:
            time.sleep(sleeptime)
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
            duration=dura,
            tween=random.choice(list_tween)
        )
        log.info(f"complete for (x,y):({x},{y})")
        pyautogui.click()

    def judge_click(  # TODO 使用`check`替换`judge`
        self,
        file: str = None,
        click: bool = True,
        dura: float = 0.5,
        sleeptime: float = 0
    ) -> None:
        """图像识别，并点击

        参数:
            file (str): 图像名称
            click (bool): 是否点击，默认是
            dura (float): 移动速度，默认0.5
            sleeptime (float): 延迟时间，默认0
        """
        while True:
            coor = self.get_coor_info(file)
            if coor.is_effective:
                if click:
                    self.click(coor.x, coor.y, dura, sleeptime)
                log.info("move to right coor successfully")
                return

    @log_function_call
    def result(self) -> bool:
        """结果判断

        返回:
            bool: Success or Fail
        """
        while True:
            coor = self.get_coor_info("victory.png")
            if coor.is_effective:
                log.ui("胜利")
                return True
            coor = self.get_coor_info("fail.png")
            if coor.is_effective:
                log.ui("失败")
                return False

    def result_once(self) -> bool | None:
        """结果判断，遍历一次

        返回:
            bool | None: Success or Fail or None
        """
        coor = self.get_coor_info("victory.png")
        if coor.is_effective:
            log.ui("胜利")
            return True
        coor = self.get_coor_info("fail.png")
        if coor.is_effective:
            log.ui("失败")
            return False
        return None

    def result_while(self) -> bool | None:
        """结果判断，循环遍历

        返回:
            bool | None: Success or Fail
        """
        while True:
            result = self.result_once()
            if result != None: # 可能Fail
                break

    def random_finish_left_right(
            self,
            click: bool = True,
            is_multiple_drops_y: bool = False,
            is_multiple_drops_x: bool = False
    ) -> tuple[int, int]:  # TODO 适配`Coor`
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
            self.click(x + window.window_left, y + window.window_top)
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


function = Function()
