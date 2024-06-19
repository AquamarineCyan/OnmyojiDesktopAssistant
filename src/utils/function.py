import json
import random
import time
from pathlib import Path

import pyautogui

from .adapter import Mouse
from .application import RESOURCE_DIR_PATH, USER_DATA_DIR_PATH
from .coordinate import AbsoluteCoor, Coor, RelativeCoor
from .decorator import log_function_call
from .event import event_thread, event_xuanshang
from .log import logger
from .paddleocr import OcrData
from .point import AbsolutePoint, Point, RelativePoint
from .window import window


def random_normal(min: int | float, max: int | float) -> int:
    """正态分布"""
    mu = (min + max) / 2
    sigma = (max - mu) / 3
    while True:
        numb = random.gauss(mu, sigma)
        if numb > min and numb < max:
            logger.info(f"normal index: {round(numb)}")
            break
        else:
            logger.info(f"normal out of index: {round(numb)}")
    return int(numb)


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


def random_point(x1: int, x2: int, y1: int, y2: int) -> Point:
    """伪随机坐标，返回给定坐标区间的随机值

    参数:
        x1 (int): 左侧横坐标
        x2 (int): 右侧横坐标
        y1 (int): 顶部纵坐标
        y2 (int): 底部纵坐标

    返回:
        Point: 矩形区域内随机值
    """
    x = random_normal(x1, x2)
    y = random_normal(y1, y2)
    logger.info(f"random_coor: {x},{y}")
    return Point(x, y)


def random_sleep(minimum: int | float = 1.0, maximum: int | float = None) -> None:
    """随机延时（秒）

    参数:
        minimum (int): 最小值（含），默认1.0
        maximum (int): 最大值（不含），默认None
    """
    if maximum is None:
        maximum = minimum + 1
    _sleep_time = random_num(minimum, maximum)
    logger.info(f"sleep for {_sleep_time} seconds")
    time.sleep(_sleep_time)


sleep = random_sleep


def image_file_format(file: Path | str) -> str:
    """补全图像文件后缀并转为`str`

    参数:
        file (Path | str): file

    返回:
        str: filename
    """
    # file一般会带上所属的子素材文件夹名称
    if isinstance(file, str):
        _file = f"{file}.png" if file[-4:] not in [".png", ".jpg"] else file
    elif isinstance(file, Path):
        if file.__str__()[-4:] not in [".png", ".jpg"]:
            _file = f"{file.__str__()}.png"
        else:
            _file = file.__str__()
    # 即使传了self.global_resource_path，Pathlib会自动合并相同路径
    _full_path = RESOURCE_DIR_PATH / _file
    _full_path_user = (USER_DATA_DIR_PATH / "myresource").joinpath(
        *_full_path.parts[-2:]
    )
    # 检查用户素材
    if _full_path_user.exists():
        logger.info(f"使用用户素材{_full_path_user}")
        return str(_full_path_user)
    elif _full_path.exists():
        return str(_full_path)
    else:
        logger.ui(f"no such file {_file}", "warn")


def get_coor_info(
    file: Path | str, region: tuple[int, int, int, int] = (0, 0, 0, 0)
) -> AbsoluteCoor:
    """图像识别，返回图像的全屏随机坐标

    参数:
        file (Path | str): 图像名称

        region (tuple[int, int, int, int]): 识别区域（相对），默认(0,0,0,0)

    用法：
        `self.resource_path / filename`

    返回:
        Coor: 成功，返回图像的全屏随机坐标；失败，返回(0,0)
    """
    if event_thread.is_set():
        return Coor(0, 0)
    # 等待悬赏封印判定
    event_xuanshang.wait()

    _file_name = image_file_format(RESOURCE_DIR_PATH / file)
    # logger.debug(f"looking for file: {_file_name}")
    # if region != (0, 0, 0, 0):
    #     logger.debug(_region)
    _region = (  # TODO need test
        region[0] + window.window_left,
        region[1] + window.window_top,
        region[2] + window.window_standard_width,
        region[3] + window.window_standard_height,
    )

    # image = RuleImage(file=_file_name, region=_region)
    # if image.match():
    #     x, y = image.random_point().x, image.random_point().y
    #     return RelativeCoor(x, y).rela_to_abs()

    # else:
    #     return Coor(0, 0)
    try:
        button_location = pyautogui.locateOnScreen(
            image=_file_name, region=_region, confidence=0.8
        )
        # logger.debug(f"button_location: {button_location}")
        if button_location:
            logger.info(f"button_location: {button_location}")
        point = random_point(
            button_location[0],
            button_location[0] + button_location[2],
            button_location[1],
            button_location[1] + button_location[3],
        )
        return AbsoluteCoor(point.x, point.y)
    except Exception:
        return Coor(0, 0)


def check_scene_multiple_once(
    scene: list, resource_path: str = None
) -> tuple[str | None, Coor]:
    """
    多场景判断，仅遍历一次

    可传带`self.global_resource_path`资源

    参数:
        scene (list): 多场景列表
        resource_path (str): 路径

    返回:
        tuple[str | None, Coor]: 场景名称, 坐标
    """
    for item in scene:
        if event_thread.is_set():
            return None, Coor(0, 0)
        """
        1.如果没传路径，说明全部文件名自带路径
        2.传参路径，可能存在`RESOURCE_FIGHT_PAHT`的资源，用斜杠判断列表值
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


@log_function_call
def finish_random_left_right(
    is_click: bool = True,
    is_multiple_drops_x: bool = False,
    is_multiple_drops_y: bool = False,
) -> RelativePoint:
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
    finish_y2 = 530
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
    if random.random() > 5 / 10:
        _finish_x1 = finish_left_x1
        _finish_x2 = finish_left_x2
    else:
        _finish_x1 = finish_right_x1
        _finish_x2 = finish_right_x2
    point = random_point(_finish_x1, _finish_x2, finish_y1, finish_y2)
    x, y = point.x, point.y

    if bool(event_thread):
        return RelativePoint(0, 0)
    if is_click:
        # click(Coor(x + window.window_left, y + window.window_top))
        Mouse.click(RelativePoint(x, y))
    return RelativePoint(x, y)


def click(
    coor: AbsoluteCoor | RelativeCoor | OcrData = None,
    dura: float = 0.5,
    sleeptime: float = 0,
) -> None:
    if isinstance(coor, OcrData):
        coor = coor.rect.get_rela_center_coor()

    if coor is None:
        Mouse.click()
        return
    elif isinstance(coor, RelativeCoor):
        _x, _y = coor.rela_to_abs().coor
    elif isinstance(coor, RelativePoint):
        Mouse.click(coor)  #使用Point
        return
    else:
        _x, _y = coor.coor

    Mouse.click(AbsolutePoint(_x, _y), duration=dura, wait=sleeptime)


def check_user_file_exists(file: str) -> Path | None:
    """检查用户素材"""
    _full_path = RESOURCE_DIR_PATH / file
    _full_path_user = (USER_DATA_DIR_PATH / "myresource").joinpath(
        *_full_path.parts[-2:]
    )
    if _full_path_user.exists():
        logger.info(f"使用用户素材{_full_path_user}")
        return _full_path_user
    elif _full_path.exists():
        return _full_path
    else:
        logger.ui(f"no such file {file}", "warn")
        return None


def open_asset_file(file: Path) -> dict:
    data = {}
    try:
        with open(str(file), encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        if "myresource" not in str(file):
            logger.ui_error(f"文件未找到:{file}")
    except json.JSONDecodeError:
        logger.ui_error(f"{file}解析错误")
    except (ValueError, TypeError):
        logger.ui_error(f"{file}值错误或类型错误")
    except Exception as e:
        logger.ui_error(f"{file}打开失败: {e}")
    finally:
        return data


def merge_dict(base_dict, update_dict) -> dict:
    """合并字典

    参数:
        base_dict (dict): 源字典
        update_dict (dict): 新字典

    返回:
        dict: 合并后的字典
    """
    if not update_dict:
        return base_dict

    for data_type in ["image_data", "ocr_data"]:
        if data_type in base_dict and data_type in update_dict:
            for item_update_dict in update_dict[data_type]:
                _name = item_update_dict.get("name")
                existing = False
                for item in base_dict.get(data_type):
                    if item.get("name") == _name:
                        item.update(item_update_dict)
                        existing = True
                        break
                if not existing:
                    base_dict[data_type].append(item_update_dict)

    return base_dict


def get_asset_data(resource_path) -> tuple[Path | dict]:
    _full_path = RESOURCE_DIR_PATH / resource_path / "assets.json"
    _full_path_user = (USER_DATA_DIR_PATH / "myresource").joinpath(
        *_full_path.parts[-2:]
    )

    data_default = open_asset_file(_full_path)
    assets_file = _full_path
    data_user = open_asset_file(_full_path_user)
    if data_user != {}:
        assets_file = _full_path_user

    return (assets_file, merge_dict(data_default, data_user))
