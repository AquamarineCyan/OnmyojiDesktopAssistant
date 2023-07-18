#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# function.py
"""通用函数库"""

import random
import time
from pathlib import Path
from subprocess import Popen

import pyautogui

from .application import (APP_EXE_NAME, RESOURCE_DIR_PATH, RESOURCE_FIGHT_PATH,
                          SCREENSHOT_DIR_PATH)
from .coordinate import Coor
from .decorator import log_function_call
from .event import event_thread, event_xuanshang, event_xuanshang_enable
from .log import log, logger
from .mysignal import global_ms as ms
from .window import window

RESOURCE_FIGHT_PATH = RESOURCE_FIGHT_PATH
"""通用战斗资源路径"""
RESTART_BAT_PATH: str = "restart.bat"
"""重启脚本路径"""


class FightResource:
    """通用战斗资源"""

    def __init__(self):
        self.resource_path: str = "fight"  # 路径
        self.resource_list: list = [  # 资源列表
            "accept_invitation",  # 接受邀请
            "fail",  # 失败
            "finish",  # 结束
            "fighting_friend_default",  # 战斗中好友图标-怀旧/简约
            "fighting_friend_linshuanghanxue",  # 战斗中好友图标-凛霜寒雪
            "fighting_friend_chunlvhanqing",  # 战斗中好友图标-春缕含青
            "passenger_2",  # 队员2
            "passenger_3",  # 队员3
            "start_single",  # 单人挑战
            "start_team",  # 组队挑战
            "tanchigui",  # 贪吃鬼
            "victory",  # 成功
            "zhunbei",  # 准备-怀旧主题
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
    return round((random.random() * (maximum - minimum) + minimum), 2)


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
    # 即使传了RESOURCE_FIGHT_PATH，Pathlib会自动合并相同路径
    if Path(RESOURCE_DIR_PATH / _file).exists():
        return _file
    else:
        log.warn(f"no such file {_file}", False)


def get_coor_info(file: Path | str) -> Coor:
    """图像识别，返回图像的全屏随机坐标

    参数:
        file (Path | str): 图像名称

    用法：
        `self.resource_path / filename`

    返回:
        Coor: 成功，返回图像的全屏随机坐标；失败，返回(0,0)
    """
    _file_name = image_file_format(RESOURCE_DIR_PATH / file)
    log.info(f"looking for file: {_file_name}")
    # 等待悬赏封印判定
    if event_thread.is_set():
        return Coor(0, 0)
    if event_xuanshang_enable.is_set():
        event_xuanshang.wait()

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
        logger.debug(f"button_location: {button_location}")
        if button_location:
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


def get_coor_info_center(file: Path | str, is_log: bool = True) -> Coor:
    """图像识别，返回图像的中心坐标

    参数:
        file (Path | str): 图像名称

    用法：
        `self.resource_path / filename`

    返回:
        Coor: 识别成功，返回图像的随机坐标，识别失败，返回(0,0)
    """
    _file_name = image_file_format(RESOURCE_DIR_PATH / file)
    if is_log:
        logger.info(f"looking for file: {_file_name}")
    try:
        button_location = pyautogui.locateCenterOnScreen(
            _file_name,
            region=(
                window.window_left,
                window.window_top,
                window.absolute_window_width,
                window.absolute_window_height
            ),
            confidence=0.8
        )
        if is_log:
            logger.debug(f"button_location: {button_location}")
        if button_location:
            logger.info(f"button_location: {button_location}")
        return Coor(button_location.x, button_location.y)
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
        if event_thread.is_set():
            return
        coor = get_coor_info(file)
        if coor.is_zero:
            return False
        if scene_name:
            log.scene(scene_name)
        return True


def check_scene_multiple_once(scene: list, resource_path: str = None) -> tuple[str | None, Coor]:
    """
    多场景判断，仅遍历一次

    可传带RESOURCE_FIGHT_PATH资源，

    参数:
        scene (list): 多场景列表
        resource_path (str): 路径

    返回:
        tuple[str | None, Coor]: 场景名称, 坐标
    """
    for item in scene:
        if event_thread.is_set():
            return
        """
        1.如果没传路径，说明全部文件名自带路径
        2.传参路径，可能存在RESOURCE_FIGHT_PAHT的资源，用斜杠判断列表值
        3.剩下的便是普通情况，即路径+文件
        多数情况下会是第2种
        """
        if (resource_path is None) or (resource_path and "/" in item):
            _file = item
        else:
            _file = f"{resource_path}/{item}"
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
        if event_thread.is_set():
            return
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
        if event_thread.is_set():
            return
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
        if event_thread.is_set():
            return
        coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/victory")
        if coor.is_effective:
            log.ui("胜利")
            return True
        coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")  # 手快导致提前结束
        if coor.is_effective:
            log.ui("结束")
            return True
        coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/fail")  # TODO `fail` 需要更新素材
        if coor.is_effective:
            log.ui("失败")
            return False


@log_function_call
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


@log_function_call
def result_while() -> bool | None:
    """结果判断，循环遍历

    返回:
        bool | None: Success or Fail
    """
    while True:
        if event_thread.is_set():
            return
        result = result_once()
        if result != None:  # 可能Fail
            break


@log_function_call
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


def check_finish_once() -> bool | None:
    """结束/掉落判断，遍历一次

    返回:
        bool: 结束/失败/None
    """
    coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")
    if coor.is_effective:
        log.ui("胜利")
        return True
    coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/fail")
    if coor.is_effective:
        log.ui("失败")
        return False
    return None


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
    if event_thread.is_set():
        return
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
    try:
        pyautogui.click()
    except pyautogui.FailSafeException:
        log.error("安全错误，可能是您点击了屏幕左上角，请重启后使用", True)


def check_click(file: str = None, is_click: bool = True, dura: float = 0.5, sleep_time: float = 0) -> None:
    """图像识别，并点击

    参数:
        file (str): 图像名称
        is_click (bool): 是否点击，默认是
        dura (float): 移动速度，默认0.5
        sleep_time (float): 延迟时间，默认0
    """
    while True:
        if event_thread.is_set():
            return
        coor = get_coor_info(file)
        if coor.is_effective:
            if is_click:
                click(coor, dura, sleep_time)
            log.info("move to right coor successfully")
            return


@log_function_call
def drag_in_window(x_offset: int = None, y_offset: int = None, duration: float = 0.5):
    """在当前窗口内移动

    参数:
        x_offset (int): 横轴偏移值
        y_offset (int): 纵轴偏移值
        duration (float): 移动速度，默认0.5
    """
    # 160,300
    # 930,550
    x1 = 160
    x2 = 930
    y1 = 300
    y2 = 550
    x = random_num(x1, x2)
    y = random_num(y1, y2)
    # TODO 需要先判断当前鼠标是否在移动区域内，减少不必要的移动
    pyautogui.moveTo(
        x+window.window_left,
        y+window.window_top,
        duration=random_num(0.5, 0.8)
    )
    pyautogui.drag(x_offset, y_offset, duration, button="left")
    # pyautogui.drag(-400,0, 1,button="left")


def screenshot(screenshot_path: str = "cache") -> bool:
    """截图

    参数:
        screenshotpath (str): 截图文件存放路径，默认"cache"

    返回:
        bool: 截图成功或失败
    """

    window_width_screenshot = 1138  # 截图宽度
    window_height_screenshot = 679  # 截图高度
    _screenshot_path = SCREENSHOT_DIR_PATH / screenshot_path
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


def write_restart_bat() -> None:
    """编写通用重启脚本"""
    bat_text = f"""@echo off
@echo 当前为重启程序，等待自动完成
set "program_name={APP_EXE_NAME}"

:a
tasklist | findstr /I /C:"%program_name%" > nul
if errorlevel 1 (
    echo %program_name% is closed.
    goto :b
) else (
    echo %program_name% is still running, waiting...
    ping 123.45.67.89 -n 1 -w 1000 > nul
    goto :a
)

:b
echo Continue restart...
timeout /T 3 /NOBREAK
start {APP_EXE_NAME}
"""
    with open(RESTART_BAT_PATH, "w", encoding="ANSI") as f:
        f.write(bat_text)


def write_upgrage_restart_bat(zip_path: str = None) -> None:
    """编写更新重启脚本"""
    bat_text = f"""@echo off
@echo 当前为更新程序，等待自动完成
set "program_name={APP_EXE_NAME}"

:a
tasklist | findstr /I /C:"%program_name%" > nul
if errorlevel 1 (
    echo %program_name% is closed.
    goto :b
) else (
    echo %program_name% is still running, waiting...
    ping 123.45.67.89 -n 1 -w 1000 > nul
    goto :a
)

:b
echo Continue updating...

if not exist zip_files\{APP_EXE_NAME} exit
timeout /T 3 /NOBREAK
move /y zip_files\{APP_EXE_NAME} .
rd /s /q zip_files
del {zip_path}
start {APP_EXE_NAME}
"""

    with open(RESTART_BAT_PATH, "w", encoding="ANSI") as f:
        f.write(bat_text)


def app_restart(is_upgrade: bool = False) -> None:
    """程序重启

    参数:
        is_upgrade (bool): 是否更新重启，默认否
    """
    log.info("重启中")
    # 更新重启有独立的脚本
    if not is_upgrade:
        write_restart_bat()
    # 启动.bat文件
    Popen([RESTART_BAT_PATH])
    # 关闭当前exe程序
    log.info("App Exiting...")
    ms.sys_exit_update.emit(True)


def remove_restart_bat_file() -> None:
    """删除重启脚本"""
    Path(RESTART_BAT_PATH).unlink(missing_ok=True)
    Path("reload.bat").unlink(missing_ok=True)  # FIXME v1.7.3引入的更新重启脚本未被删除
