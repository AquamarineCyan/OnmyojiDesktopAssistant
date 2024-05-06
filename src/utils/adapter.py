import random
import time
import pyautogui
import pytweening

from .event import event_thread, event_xuanshang
from .log import logger
from .paddleocr import OcrData
from .point import AbsolutePoint, RelativePoint
from .window import window

__all__ = ["Mouse", "KeyBoard"]


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
        duration: float = 0,
        tween=linear,
    ):
        try:
            if xOffset and yOffset:
                pyautogui.move(xOffset, yOffset, duration, tween)
            else:
                if point is None:
                    startx, starty = pyautogui.position()
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
                        "The point argument must be an RelativePoint or a AbsolutePoint."
                    )
                pyautogui.moveTo(x, y, duration, tween)

        except pyautogui.FailSafeException:
            logger.error("鼠标移动失败，请检查是否点击了屏幕左上角，请重启后使用")
            return

    @staticmethod
    def random_tween():
        """补间移动，模拟真人运动轨迹"""
        list_tween = [
            pytweening.easeInQuad,
            pytweening.easeOutQuad,
            pytweening.easeInOutQuad,
        ]
        random.seed(time.time_ns())
        return random.choice(list_tween)

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

        if isinstance(point, OcrData):
            point = point.rect.get_rela_center_coor()

        if point is None:
            _x, _y = pyautogui.position()
        elif isinstance(point, RelativePoint):
            _x, _y = point.rela_to_abs().coor
        else:
            _x, _y = point.coor

        # cls.move(x=_x, y=_y, duration=duration, tween=random.choice(list_tween))
        logger.info(f"click at ({_x},{_y})")
        # cls.send_mouse_event(0x6, _x, _y, 0)
        try:
            pyautogui.click(_x, _y, duration=duration, tween=cls.random_tween())
        except pyautogui.FailSafeException:
            logger.error(f"click error at ({_x},{_y})")
            logger.ui_error("安全错误，可能是您点击了屏幕左上角，请重启后使用")

    @classmethod
    def drag(cls, x_offset: int = None, y_offset: int = None, duration: float = 0.5):
        """拖动，使用前需要先移动鼠标至当前位置

        参数:
            x_offset (int): 横轴拖动量
            y_offset (int): 纵轴拖动量
            duration (float): 持续时间
        """
        pyautogui.dragRel(
            x_offset, y_offset, duration=duration, tween=cls.random_tween()
        )

    @classmethod
    def scroll(cls, distance: int) -> None:
        """
        滚轮
        Scrolls the mouse wheel.

        参数:
        distance (int): How far to scroll the mouse wheel. Positive values
            scroll up/away from the user, negative values scroll down/toward the
            user.
        """
        pyautogui.scroll(distance)
        logger.info(f"scroll at ({distance})")


class KeyBoard:
    """键盘事件"""

    @staticmethod
    def _keyboard_input(key: str):
        """模拟键盘输入"""
        pyautogui.press(key)

    @classmethod
    def enter(cls, wait: float = 0):
        """键入`回车键`"""
        if wait:
            time.sleep(wait)
        event_xuanshang.wait()
        cls._keyboard_input("enter")

    @classmethod
    def esc(cls, wait: float = 0):
        """键入`ESC键`"""
        if wait:
            time.sleep(wait)
        event_xuanshang.wait()
        cls._keyboard_input("esc")
