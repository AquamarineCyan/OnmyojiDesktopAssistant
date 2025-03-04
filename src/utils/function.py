import json
import math
import random
import time
from pathlib import Path

from .adapter import Mouse
from .application import APP_PATH, RESOURCE_DIR_PATH, USER_DATA_DIR_PATH
from .decorator import log_function_call
from .event import event_thread
from .exception import GUIStopException
from .log import logger
from .point import Rectangle, RelativePoint


def is_Chinese_Path() -> bool:
    """是否中文路径

    `opencv` 需要英文路径
    """
    from re import compile

    zhPattern = compile("[\u4e00-\u9fa5]+")
    match = zhPattern.search(str(APP_PATH))
    if not match:
        logger.info("English Path")
        return False
    logger.ui_error("Chinese Path")
    return True


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


def random_point(x1: int, x2: int, y1: int, y2: int) -> RelativePoint:
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
    return RelativePoint(x, y)


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


def distance_between_two_points(point1, point2):
    """计算两点之间的距离"""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


@log_function_call
def finish_random_left_right(
    is_click: bool = True,
    is_multiple_drops_x: bool = False,
    is_multiple_drops_y: bool = False,
) -> RelativePoint:
    """结算界面点击

    参数:
        is_click (bool): 鼠标点击,默认是
        is_multiple_drops_x (bool): 多掉落横向区域,默认否
        is_multiple_drops_y (bool): 多掉落纵向区域,默认否

    返回:
        RelativePoint: 相对坐标
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

    rect_left = Rectangle(finish_left_x1, finish_y1, x2=finish_left_x2, y2=finish_y2)
    rect_right = Rectangle(finish_right_x1, finish_y1, x2=finish_right_x2, y2=finish_y2)

    # 计算鼠标到两个矩形中心的距离
    position = Mouse.position()
    distance_to_left = distance_between_two_points(position.coor, rect_left.get_center())
    distance_to_right = distance_between_two_points(position.coor, rect_right.get_center())

    # 判断距离
    if distance_to_left < distance_to_right:
        chosen_rect = rect_left
        logger.info("鼠标更接近左侧")
    elif distance_to_left > distance_to_right:
        chosen_rect = rect_right
        logger.info("鼠标更接近右侧")
    else:
        # 如果距离相等，随机选择一个矩形
        chosen_rect = random.choice([rect_left, rect_right])
        logger.info(f"鼠标距离两个矩形相等，随机选择矩形{chosen_rect}")

    point = random_point(chosen_rect.x1, chosen_rect.x2, chosen_rect.y1, chosen_rect.y2)

    if bool(event_thread):
        raise GUIStopException

    if is_click:
        Mouse.click(point)
    return point


def check_user_file_exists(file: str) -> Path | None:
    """检查用户素材"""
    _full_path = RESOURCE_DIR_PATH / file
    _full_path_user = (USER_DATA_DIR_PATH / "myresource").joinpath(*_full_path.parts[-2:])
    if _full_path_user.exists():
        logger.info(f"使用用户素材{_full_path_user}")
        return _full_path_user
    elif _full_path.exists():
        return _full_path
    else:
        logger.ui_warn(f"未找到文件：{file}")
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
    _full_path_user = (USER_DATA_DIR_PATH / "myresource").joinpath(*_full_path.parts[-2:])

    data_default = open_asset_file(_full_path)
    assets_file = _full_path
    data_user = open_asset_file(_full_path_user)
    if data_user != {}:
        assets_file = _full_path_user

    return (assets_file, merge_dict(data_default, data_user))
