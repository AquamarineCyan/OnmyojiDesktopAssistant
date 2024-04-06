import ctypes
import ctypes.wintypes
import random
import time

import pytweening

from .event import event_thread, event_xuanshang
from .log import logger
from .paddleocr import OcrData
from .point import AbsolutePoint, RelativePoint
from .window import SCREEN_SIZE, window

__all__ = ["Mouse", "KeyBoard"]

"""copy from pyautogui"""
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


def linear(n):
    """
    Returns ``n``, where ``n`` is the float argument between ``0.0`` and ``1.0``. This function is for the default
    linear tween for mouse moving functions.

    This function was copied from PyTweening module, so that it can be called even if PyTweening is not installed.
    """

    # We use this function instead of pytweening.linear for the default tween function just in case pytweening couldn't be imported.
    if not 0.0 <= n <= 1.0:
        raise ("Argument must be between 0.0 and 1.0.")
    return n


def getPointOnLine(x1, y1, x2, y2, n):
    """
    Returns an (x, y) tuple of the point that has progressed a proportion ``n`` along the line defined by the two
    ``x1``, ``y1`` and ``x2``, ``y2`` coordinates.

    This function was copied from pytweening module, so that it can be called even if PyTweening is not installed.
    """
    x = ((x2 - x1) * n) + x1
    y = ((y2 - y1) * n) + y1
    return (x, y)


class Mouse:
    """鼠标事件"""

    @classmethod
    def move(
        cls,
        point: AbsolutePoint | RelativePoint | None = None,
        x: float = None,
        y: float = None,
        xOffset: float = None,
        yOffset: float = None,
        duration: float = None,
        tween=linear,
    ):
        """
        移动
        Handles the actual move or drag event, since different platforms
        implement them differently.

        On Windows & Linux, a drag is a normal mouse move while a mouse button is
        held down. On OS X, a distinct "drag" event must be used instead.

        The code for moving and dragging the mouse is similar, so this function
        handles both. Users should call the moveTo() or dragTo() functions instead
        of calling _mouseMoveDrag().

        Args:
        moveOrDrag (str): Either 'move' or 'drag', for the type of action this is.
        x (int, float, None): How far left (for negative values) or
            right (for positive values) to move the cursor. 0 by default.
        y (int, float, None): How far up (for negative values) or
            down (for positive values) to move the cursor. 0 by default.
        xOffset (int, float, None): How far left (for negative values) or
            right (for positive values) to move the cursor. 0 by default.
        yOffset (int, float, None): How far up (for negative values) or
            down (for positive values) to move the cursor. 0 by default.
        duration (float): The amount of time it takes to move the mouse
            cursor to the new xy coordinates. If 0, then the mouse cursor is moved
            instantaneously. 0.0 by default.
        tween (function): The tweening function used if the duration is not
            0. A linear tween is used by default.
        """

        xOffset = int(xOffset) if xOffset else 0
        yOffset = int(yOffset) if yOffset else 0

        startx, starty = position()

        if point is None:
            x = int(x) if x else startx
            y = int(y) if y else starty
        elif isinstance(point, RelativePoint):
            x = int(window.window_left + point.x)
            y = int(window.window_top + point.y)
        elif isinstance(point, AbsolutePoint):
            x = int(point.x)
            y = int(point.y)
        else:
            raise TypeError(
                "The point argument must be an AbsolutePoint or a RelativePoint."
            )
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

            steps = [
                getPointOnLine(startx, starty, x, y, tween(n / num_steps))
                for n in range(num_steps)
            ]
            # Making sure the last position is the actual destination.
            steps.append((x, y))

        for tweenX, tweenY in steps:
            if len(steps) > 1:
                # A single step does not require tweening.
                time.sleep(sleep_amount)

            tweenX = int(round(tweenX))
            tweenY = int(round(tweenY))

            if 0 in [tweenX, tweenY]:
                logger.ui_error(
                    "鼠标移动失败，请检查是否点击了屏幕左上角，请重启后使用"
                )
            else:
                ctypes.windll.user32.SetCursorPos(tweenX, tweenY)

    @staticmethod
    def send_mouse_event(event_type, x, y, data):
        """
        Send a mouse event to the system.

        Args:
        event_type (str): The type of event to send.
        x (int): The x coordinate of the mouse event.
        y (int): The y coordinate of the mouse event.
        """
        width, height = SCREEN_SIZE
        convertedX = int(65536 * x // width + 1)
        convertedY = int(65536 * y // height + 1)
        ctypes.windll.user32.mouse_event(
            event_type, ctypes.c_long(convertedX), ctypes.c_long(convertedY), data, 0
        )

    @classmethod
    def click(
        cls,
        point: AbsolutePoint | RelativePoint | OcrData | None = None,
        duration: float = 0.5,
        wait: float = 0,
    ) -> None:
        """点击

        参数:
            point (AbsolutePoint | RelativePoint | OcrData | None): 坐标
            duration (float): 持续时间
            wait (float): 前置等待时间
        """
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

        cls.move(x=_x, y=_y, duration=duration, tween=random.choice(list_tween))
        logger.info(f"click at ({_x},{_y})")
        cls.send_mouse_event(0x6, _x, _y, 0)
        # try:
        # except pyautogui.FailSafeException:
        #     logger.error(f"click error at ({_x},{_y})")
        #     logger.ui("安全错误，可能是您点击了屏幕左上角，请重启后使用", "error")

    @classmethod
    def drag(cls, x_offset: int = None, y_offset: int = None, duration: float = 0.5):
        """拖动，使用前需要先移动鼠标至当前位置

        参数:
            x_offset (int): 横轴拖动量
            y_offset (int): 纵轴拖动量
            duration (float): 持续时间
        """
        # 按下鼠标
        cls.send_mouse_event(0x0002, 0, 0, 0)
        # 拖动鼠标
        cls.move(xOffset=x_offset, yOffset=y_offset, duration=duration)
        # 释放鼠标
        cls.send_mouse_event(0x0004, 0, 0, 0)

    @classmethod
    def scroll(cls, distance: int) -> None:
        """
        滚轮
        Scrolls the mouse wheel.

        Args:
        distance (int): How far to scroll the mouse wheel. Positive values
            scroll up/away from the user, negative values scroll down/toward the
            user.

        Raises:
        ValueError: If the distance is not an integer.
        """
        if not isinstance(distance, int):
            raise ValueError("Distance must be an integer.")

        if distance == 0:
            return

        x, y = position()
        cls.send_mouse_event(0x800, x, y, distance)
        logger.info(f"scroll at ({distance})")


class KeyBoard:
    """键盘事件"""

    @staticmethod
    def _keyboard_input(key: int):
        """模拟键盘输入"""
        ctypes.windll.user32.keybd_event(key, 0, 0, 0)
        ctypes.windll.user32.keybd_event(key, 0, 0x0002, 0)

    @classmethod
    def enter(cls, wait: float = 0):
        """键入`回车键`"""
        if wait:
            time.sleep(wait)
        event_xuanshang.wait()
        cls._keyboard_input(0x0D)

    @classmethod
    def esc(cls, wait: float = 0):
        """键入`ESC键`"""
        if wait:
            time.sleep(wait)
        event_xuanshang.wait()
        cls._keyboard_input(0x1B)
