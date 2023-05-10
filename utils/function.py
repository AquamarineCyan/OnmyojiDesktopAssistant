#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# function.py
"""通用函数库"""

import random
import time
from pathlib import Path

import pyautogui

from package.xuanshangfengyin import xuanshangfengyin

from .config import config
from .coordinate import Coor
from .decorator import *
from .log import log
from .window import window

RESOURCE_FIGHT_PATH = config.resource_path / "fight"
"""通用战斗资源路径"""


class FightSource:
    """通用战斗资源"""

    def __init__(self):
        self.resource_path: str = "fight"  # 路径
        self.resource_list: list = [  # 资源列表
            "passenger_2",  # 队员2
            "passenger_3",  # 队员3
            "victory",  # 成功
            "fail",  # 失败
            "finish",  # 结束
            "tanchigui",  # 贪吃鬼
            "accept_invitation",  # 接受邀请
            "zhunbei",  # 准备
        ]


def random_num(minimum: int | float, maximum: int | float) -> float:
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


def random_coor(x1: int, x2: int, y1: int, y2: int) -> Coor:
    """伪随机坐标，返回给定坐标区间的随机值

    参数:
        x1 (int): 左侧横坐标
        x2 (int): 右侧横坐标
        y1 (int): 顶部纵坐标
        y2 (int): 底部纵坐标

    返回:
        Coor: 矩形区域内随机值
    """
    # TODO 返回坐标偏中心
    x = random_num(x1, x2)
    y = random_num(y1, y2)
    log.info(f"random_coor: {x},{y}")
    return Coor(x, y)


def random_sleep(minimum: int | float, maximum: int | float) -> None:
    """随机延时（秒）

    参数:
        minimum (int): 最小值（含）
        maximum (int): 最大值（不含）
    """
    _sleep_time = random_num(minimum, maximum)
    log.info(f"sleep for {_sleep_time} seconds")
    time.sleep(_sleep_time)


def image_file_format(file: Path | str) -> str:
    """补全图像文件后缀并转为`str`

    `pyautogui` need file path be `str`

    参数:
        file (Path | str): file

    返回:
        str: filename
    """
    if isinstance(file, str):
        _file = f"{file}.png" if file[-4:] not in [".png", ".jpg"] else file
    elif isinstance(file, Path):
        if file.__str__()[-4:] not in [".png", ".jpg"]:
            _file = f"{file.__str__()}.png"
        else:
            _file = file.__str__()
    if Path(config.resource_path / _file).exists():
        return _file
    else:
        log.warn(f"no such file {_file}", False)


def get_coor_info(file: Path | str) -> Coor:
    """图像识别，返回图像的全屏随机坐标

    参数:
        file (Path | str): 图像名称

    返回:
        Coor: 成功，返回图像的全屏随机坐标；失败，返回(0,0)
    """
    _file_name = image_file_format(config.resource_path / file)
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
        log.info(f"button_location: {button_location}")
        coor = random_coor(
            button_location[0],
            button_location[0] + button_location[2],
            button_location[1],
            button_location[1] + button_location[3]
        )
        return coor
    except Exception:
        return Coor(0, 0)


def check_scene(file: str, scene_name: str = None) -> bool:
    """场景判断

    参数:
        file (str): 图像文件
        scene_name (str): 场景描述

    返回:
        bool: 是否为指定场景
    """
    while True:
        coor = get_coor_info(file)
        if coor.is_zero:
            return False
        if scene_name:
            log.scene(scene_name)
        return True


def check_scene_multiple_once(scene: dict | list, resource_path: str = None) -> tuple[str | None, Coor]:
    """多场景判断，仅遍历一次

    参数:
        scene (dict | list): 多场景列表
        resource_path (str): 路径

    返回:
        tuple[str | None, Coor]: 场景名称, 坐标
    """
    # XXX 移除对字典的适配
    if isinstance(scene, dict):
        for key, value in scene.items():
            file = f"{config.resource_path}/{key}" if resource_path else key
            coor = get_coor_info(file)
            if coor.is_effective:
                return str(value), coor
    elif isinstance(scene, list):
        for item in scene:
            # 如果没传路径，说明文件名自带路径
            _file = item if resource_path is None else f"{resource_path}/{item}"
            coor = get_coor_info(_file)
            if coor.is_effective:
                return str(item), coor
        return None, Coor(0, 0)


def check_scene_multiple_while(scene: dict | list = None, resource_path: str = None, text: str = None) -> tuple[str, Coor]:
    """多场景判断，循环遍历，直至符合任意一个场景

    参数:
        scene (dict | list): 多场景列表
        resource_path (str): 路径 
        text (str): 提示

    返回:
        tuple[str, Coor]: 场景名称, 坐标
    """
    _flag: bool = True  # 提示
    _text = text if text is not None else "请检查游戏场景"
    while True:
        scene, coor = check_scene_multiple_once(scene, resource_path)
        if coor.is_effective():
            log.info(f"{scene}, ({coor.x},{coor.y})")
            return scene, coor
        elif _flag:
            _flag = False
            log.warn(_text)


@log_function_call
def is_passengers_on_position(flag_passengers: int = 2):
    """队员就位"""
    log.ui("等待队员")
    while True:
        # 是否3人组队
        if flag_passengers == 3:
            coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/passenger_3")
            if coor.is_zero:
                log.ui("队员3就位")
                return
        else:
            coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/passenger_2")
            if coor.is_zero:
                log.ui("队员2就位")
                return


@log_function_call
def result() -> bool:
    """结果判断

    返回:
        bool: Success or Fail
    """
    while True:
        coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/victory")
        if coor.is_effective:
            log.ui("胜利")
            return True
        coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/fail")  # TODO `fail` 需要更新素材
        if coor.is_effective:
            log.ui("失败")
            return False


def result_once() -> bool | None:
    """结果判断，遍历一次

    返回:
        bool | None: Success or Fail or None
    """
    coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/victory")
    if coor.is_effective:
        log.ui("胜利")
        return True
    coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/fail")
    if coor.is_effective:
        log.ui("失败")
        return False
    return None


def result_while() -> bool | None:
    """结果判断，循环遍历

    返回:
        bool | None: Success or Fail
    """
    while True:
        result = result_once()
        if result != None:  # 可能Fail
            break


def finish() -> bool:
    """结束/掉落判断

    返回:
        bool: Success or Fail
    """
    while True:
        coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")
        if coor.is_effective:
            log.ui("胜利")
            return True
        coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/fail")
        if coor.is_effective:
            log.ui("失败")
            return False


def finish_random_left_right(
        is_click: bool = True,
        is_multiple_drops_x: bool = False,
        is_multiple_drops_y: bool = False
) -> Coor:
    """图像识别，返回图像的局部相对坐标

    参数:
        is_click (bool): 鼠标点击,默认是
        is_multiple_drops_x (bool): 多掉落横向区域,默认否
        is_multiple_drops_y (bool): 多掉落纵向区域,默认否

    返回:
        Coor: 坐标
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

    # 永生之海/神罚
    if is_multiple_drops_x:
        finish_left_x2 = 70
        finish_right_x1 = 1070
    # 御灵
    if is_multiple_drops_y:
        finish_y2 -= 200
    # 获取系统当前时间戳
    random.seed(time.time_ns())
    if random.random() * 10 > 5:
        _finish_x1 = finish_left_x1
        _finish_x2 = finish_left_x2
    else:
        _finish_x1 = finish_right_x1
        _finish_x2 = finish_right_x2
    x, y = random_coor(_finish_x1, _finish_x2, finish_y1, finish_y2).coor

    if is_click:
        click(Coor(x + window.window_left, y + window.window_top))
    return Coor(x, y)


def click(coor: Coor = None, dura: float = 0.5, sleeptime: float = 0) -> None:
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
    x, y = pyautogui.position() if coor is None else (coor.x, coor.y)
    pyautogui.moveTo(x, y, duration=dura, tween=random.choice(list_tween))
    log.info(f"complete for (x,y): ({x},{y})")
    pyautogui.click()


def check_click(file: str = None, is_click: bool = True, dura: float = 0.5, sleep_time: float = 0.5) -> None:
    """图像识别，并点击

    参数:
        file (str): 图像名称
        is_click (bool): 是否点击，默认是
        dura (float): 移动速度，默认0.5
        sleep_time (float): 延迟时间，默认0
    """
    while True:
        coor = get_coor_info(file)
        if coor.is_effective:
            if is_click:
                click(coor, dura, sleep_time)
            log.info("move to right coor successfully")
            return


def screenshot(screenshot_path: str = "cache") -> bool:
    """截图

    参数:
        screenshotpath (str): 截图文件存放路径，默认"cache"

    返回:
        bool: 截图成功或失败
    """

    window_width_screenshot = 1138  # 截图宽度
    window_height_screenshot = 679  # 截图高度
    _screenshot_path = config.application_path / screenshot_path
    _screenshot_path.mkdir(parents=True, exist_ok=True)

    _file = f"{_screenshot_path}/screenshot-{time.strftime('%Y%m%d%H%M%S')}.png"
    try:
        pyautogui.screenshot(
            imageFilename=_file,
            region=(
                window.window_left - 1,
                window.window_top,
                window_width_screenshot,
                window_height_screenshot
            )
        )
        log.info(f"screenshot at {_file}")
        return True
    except Exception:
        log.error("screenshot failed.")
        return False
