"""copy from pyautogui"""

import ctypes
import ctypes.wintypes
import random
import time

import pytweening

from .event import event_thread
from .log import logger
from .paddleocr import OcrData
from .point import AbsolutePoint, RelativePoint
from .window import SCREEN_SIZE

__all__ = ["mouse_move", "mouse_click"]

# In seconds. Any duration less than this is rounded to 0.0 to instantly move
# the mouse.
MINIMUM_DURATION = 0.1
# If sleep_amount is less than MINIMUM_DURATION, time.sleep() will be a no-op and the mouse cursor moves there instantly.
# TODO: This value should vary with the platform. http://stackoverflow.com/q/1133857
MINIMUM_SLEEP = 0.05


def position() -> tuple[int, int]:
    cursor = ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
    return cursor.x, cursor.y


def getPointOnLine(x1, y1, x2, y2, n):
    """
    Returns an (x, y) tuple of the point that has progressed a proportion ``n`` along the line defined by the two
    ``x1``, ``y1`` and ``x2``, ``y2`` coordinates.

    This function was copied from pytweening module, so that it can be called even if PyTweening is not installed.
    """
    x = ((x2 - x1) * n) + x1
    y = ((y2 - y1) * n) + y1
    return (x, y)


def mouse_move(
    x: float = None,
    y: float = None,
    xOffset: float = None,
    yOffset: float = None,
    duration: float = None,
    tween=None,
):
    """Handles the actual move or drag event, since different platforms
    implement them differently.

    On Windows & Linux, a drag is a normal mouse move while a mouse button is
    held down. On OS X, a distinct "drag" event must be used instead.

    The code for moving and dragging the mouse is similar, so this function
    handles both. Users should call the moveTo() or dragTo() functions instead
    of calling _mouseMoveDrag().

    Args:
      moveOrDrag (str): Either 'move' or 'drag', for the type of action this is.
      x (int, float, None, optional): How far left (for negative values) or
        right (for positive values) to move the cursor. 0 by default.
      y (int, float, None, optional): How far up (for negative values) or
        down (for positive values) to move the cursor. 0 by default.
      xOffset (int, float, None, optional): How far left (for negative values) or
        right (for positive values) to move the cursor. 0 by default.
      yOffset (int, float, None, optional): How far up (for negative values) or
        down (for positive values) to move the cursor. 0 by default.
      duration (float, optional): The amount of time it takes to move the mouse
        cursor to the new xy coordinates. If 0, then the mouse cursor is moved
        instantaneously. 0.0 by default.
      tween (func, optional): The tweening function used if the duration is not
        0. A linear tween is used by default.
    """

    xOffset = int(xOffset) if xOffset else 0
    yOffset = int(yOffset) if yOffset else 0

    startx, starty = position()

    x = int(x) if x else startx
    y = int(y) if y else starty

    x += xOffset
    y += yOffset

    width, height = SCREEN_SIZE

    # Make sure x and y are within the screen bounds.
    x = max(0, min(x, width - 1))
    y = max(0, min(y, height - 1))

    # If the duration is small enough, just move the cursor there instantly.
    steps = [(x, y)]

    if duration > MINIMUM_DURATION:
        # Non-instant moving/dragging involves tweening:
        num_steps = max(width, height)
        sleep_amount = duration / num_steps
        if sleep_amount < MINIMUM_SLEEP:
            num_steps = int(duration / MINIMUM_SLEEP)
            sleep_amount = duration / num_steps

        for n in range(num_steps):
            point = getPointOnLine(startx, starty, x, y, tween(n / num_steps))
            steps.append(point)
        # Making sure the last position is the actual destination.
        steps.append((x, y))

    for tweenX, tweenY in steps:
        if len(steps) > 1:
            # A single step does not require tweening.
            time.sleep(sleep_amount)

        tweenX = int(round(tweenX))
        tweenY = int(round(tweenY))

        if 0 in [tweenX, tweenY]:
            logger.ui_error("鼠标移动失败，请检查是否点击了屏幕左上角，请重启后使用")
        else:
            ctypes.windll.user32.SetCursorPos(tweenX, tweenY)


def click(x, y):
    width, height = SCREEN_SIZE
    convertedX = int(65536 * x // width + 1)
    convertedY = int(65536 * y // height + 1)
    ctypes.windll.user32.mouse_event(
        0x6, ctypes.c_long(convertedX), ctypes.c_long(convertedY), 0, 0
    )


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
        _x, _y = position()
    elif isinstance(point, RelativePoint):
        _x, _y = point.rela_to_abs().coor
    else:
        _x, _y = point.coor

    # try:
    mouse_move(_x, _y, duration=duration, tween=random.choice(list_tween))
    logger.info(f"click at ({_x},{_y})")
    click(_x, _y)
    # except pyautogui.FailSafeException:
    #     logger.error(f"click error at ({_x},{_y})")
    #     logger.ui("安全错误，可能是您点击了屏幕左上角，请重启后使用", "error")
