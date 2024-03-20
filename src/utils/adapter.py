import random
import time

import pyautogui
import pytweening

from .event import event_thread
from .log import logger
from .paddleocr import OcrData
from .point import AbsolutePoint, RelativePoint


def mouse_click(
    point: AbsolutePoint | RelativePoint | OcrData = None,
    duration: float = 0.5,
    wait: float = 0,
) -> None:
    if bool(event_thread):
        return
    # 延迟
    if wait:
        time.sleep(wait)
    # 补间移动，模拟真人运动轨迹
    list_tween = [
        pytweening.easeInQuad,
        pytweening.easeOutQuad,
        pytweening.easeInOutQuad,
    ]
    random.seed(time.time_ns())

    if isinstance(point, OcrData):
        point = point.rect.get_rela_center_coor()

    if point is None:
        _x, _y = pyautogui.position()
    elif isinstance(point, RelativePoint):
        _x, _y = point.rela_to_abs().coor
    else:
        _x, _y = point.coor

    try:
        pyautogui.moveTo(_x, _y, duration=duration, tween=random.choice(list_tween))
        logger.info(f"click at ({_x},{_y})")
        pyautogui.click()
    except pyautogui.FailSafeException:
        logger.error(f"click error at ({_x},{_y})")
        logger.ui("安全错误，可能是您点击了屏幕左上角，请重启后使用", "error")
