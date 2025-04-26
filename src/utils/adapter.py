import random
import time
from typing import Literal

import pyautogui
import pytweening
import win32api
import win32con

from .config import config
from .event import event_thread, event_xuanshang
from .exception import GUIStopException
from .log import logger
from .paddleocr import OcrData
from .point import AbsolutePoint, RelativePoint
from .window import window

__all__ = ["Mouse", "KeyBoard"]

_back_click_x: int = 0
_back_click_y: int = 0


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
    def position(cls) -> RelativePoint:
        return AbsolutePoint(*pyautogui.position()).abs_to_rela()

    @staticmethod
    def random_tween():
        """补间移动，模拟真人运动轨迹"""
        tweens = [
            pytweening.easeInQuad,
            pytweening.easeOutQuad,
            pytweening.easeInOutQuad,
        ]
        return random.choice(tweens)

    # 鼠标后台点击事件参考 https://learn.microsoft.com/zh-cn/windows/win32/inputdev/mouse-input-notifications

    @staticmethod
    def _win_move(hwnd, lParam):
        # 没法发送原始输入(WM_INPUT)
        # win32api.SendMessage(hwnd, win32con.WM_NCHITTEST, 0, lParam) # NC前缀表示鼠标在屏幕的坐标
        # win32api.SendMessage(hwnd, win32con.WM_SETCURSOR, win32con.HTCLIENT, lParam) #未生效，不影响使用
        win32api.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lParam)

    @staticmethod
    def _win_left_click(hwnd, lParam):
        # 没法发送原始输入(WM_INPUT)
        # win32api.SendMessage(hwnd, win32con.WM_NCHITTEST, 0, lParam)
        # win32api.SendMessage(hwnd, win32con.WM_SETCURSOR, win32con.HTCLIENT, lParam) #未生效，不影响使用
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
        win32api.SendMessage(hwnd, win32con.WM_CAPTURECHANGED, 0, 0)
        # win32api.SendMessage(hwnd, win32con.WM_NCHITTEST, 0, lParam)
        win32api.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lParam)

    @staticmethod
    def _win_scroll(hwnd, wheel_delta, lParam):
        win32api.PostMessage(hwnd, win32con.WM_MOUSEWHEEL, win32api.MAKELONG(0, wheel_delta), lParam)

    @classmethod
    def _move_front(
        cls,
        dst_point: AbsolutePoint | RelativePoint | None = None,
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
                if dst_point is None:
                    startx, starty = pyautogui.position()
                    x = int(x) if x else startx
                    y = int(y) if y else starty
                elif isinstance(dst_point, RelativePoint):
                    x = int(window.window_left + dst_point.x)
                    y = int(window.window_top + dst_point.y)
                elif isinstance(dst_point, AbsolutePoint):
                    x = int(dst_point.x)
                    y = int(dst_point.y)
                else:
                    raise TypeError("The point argument must be an RelativePoint or a AbsolutePoint.")
                pyautogui.moveTo(x, y, duration, tween)

        except pyautogui.FailSafeException:
            logger.error("鼠标移动失败，请检查是否点击了屏幕左上角，请重启后使用")
            return

    @classmethod
    def _move_backend(
        cls,
        dst_point: AbsolutePoint | RelativePoint | None = None,
        x: float = None,
        y: float = None,
        xOffset: float = None,
        yOffset: float = None,
    ):
        global _back_click_x, _back_click_y

        # if point is None:
        #     x = _back_click_x
        #     y = _back_click_y
        # else:
        #     x, y = point.coor

        hwnd = window.handle
        current_x = _back_click_x
        current_y = _back_click_y
        dst_x = dst_point.x if dst_point else x
        dst_y = dst_point.y if dst_point else y

        # 计算移动的步数
        steps = int(max(abs(dst_x - current_x), abs(dst_y - current_y)))
        if steps == 0:
            logger.info("steps == 0")
            steps = 1

        # 计算每一步的增量
        x_step = (dst_x - current_x) / steps
        y_step = (dst_y - current_y) / steps
        logger.info(f"steps:{steps}, x_step:{x_step}, y_step:{y_step}")

        for _ in range(steps):
            current_x += x_step
            current_y += y_step
            lParam = win32api.MAKELONG(int(current_x), int(current_y))
            cls._win_move(hwnd, lParam)

        # 最后一步确保到达目标位置
        lParam = win32api.MAKELONG(int(dst_x), int(dst_y))
        cls._win_move(hwnd, lParam)

        _back_click_x = current_x
        _back_click_y = current_y
        logger.info(f"update ({_back_click_x},{_back_click_y})")

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
        if config.backend:
            cls._move_backend(point, x, y, xOffset, yOffset)
        else:
            cls._move_front(point, x, y, xOffset, yOffset, duration, tween)

    @classmethod
    def _click_front(cls, point: AbsolutePoint | RelativePoint | None = None, duration: float = 0.5):
        if point is None:
            x, y = pyautogui.position()
            logger.info("click at current position")
        elif isinstance(point, RelativePoint):
            x, y = point.rela_to_abs().coor
            logger.info(f"RelativePoint:({x},{y})")
        else:
            x, y = point.coor
            logger.warning(f"AbsolutePoint:({x},{y})")

        # cls.move(x=_x, y=_y, duration=duration, tween=random.choice(list_tween))
        # logger.info(f"click at ({x},{y})")
        # cls.send_mouse_event(0x6, x, y, 0)
        try:
            pyautogui.click(x, y, duration=duration, tween=cls.random_tween())
        except pyautogui.FailSafeException:
            logger.error(f"click error at ({x},{y})")
            logger.ui_error("安全错误，可能是您点击了屏幕左上角，请重启后使用")

    @classmethod
    def _click_backend(cls, point: AbsolutePoint | RelativePoint | None = None):
        global _back_click_x, _back_click_y

        if point is None:
            dst_x = _back_click_x
            dst_y = _back_click_y
        else:
            dst_x, dst_y = point.coor

        hwnd = window.handle
        current_x = _back_click_x
        current_y = _back_click_y

        # 计算移动的步数
        steps = int(max(abs(dst_x - current_x), abs(dst_y - current_y)))
        if steps == 0:
            logger.info("steps == 0")
            steps = 1

        # 计算每一步的增量
        x_step = (dst_x - current_x) / steps
        y_step = (dst_y - current_y) / steps
        logger.info(f"steps:{steps}, x_step:{x_step}, y_step:{y_step}")

        for _ in range(steps):
            current_x += x_step
            current_y += y_step
            lParam = win32api.MAKELONG(int(current_x), int(current_y))
            cls._win_move(hwnd, lParam)

        # 最后一步确保到达目标位置
        lParam = win32api.MAKELONG(int(dst_x), int(dst_y))
        cls._win_move(hwnd, lParam)

        # 模拟鼠标按下和释放
        cls._win_left_click(hwnd, lParam)

        _back_click_x = current_x
        _back_click_y = current_y
        logger.info(f"update ({_back_click_x},{_back_click_y})")

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
            raise GUIStopException

        # 延迟
        if wait:
            time.sleep(wait)

        if isinstance(point, OcrData):
            point = point.center

        if config.backend:
            # logger.info(f"backend click {point.x},{point.y}")
            cls._click_backend(point)
        else:
            # logger.info(f"front click {point.x},{point.y}")
            cls._click_front(point, duration)

    @classmethod
    def _drag_front(cls, x_offset: int = None, y_offset: int = None, duration: float = 0.5):
        pyautogui.dragRel(x_offset, y_offset, duration=duration, tween=cls.random_tween())

    @classmethod
    def _drag_backend(cls, x_offset: int = None, y_offset: int = None):
        global _back_click_x, _back_click_y

        hwnd = window.handle
        current_x = _back_click_x
        current_y = _back_click_y

        # 计算移动的步数
        steps = max(abs(x_offset), abs(y_offset)) // 10
        if steps == 0:
            logger.info("steps == 0")
            steps = 1

        # 计算每一步的增量
        x_step = x_offset / steps
        y_step = y_offset / steps
        logger.info(f"steps:{steps}, x_step:{x_step}, y_step:{y_step}")

        lParam = win32api.MAKELONG(int(current_x), int(current_y))
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)

        for _ in range(steps):
            current_x += x_step
            current_y += y_step
            lParam = win32api.MAKELONG(int(current_x), int(current_y))
            win32api.PostMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, lParam)
            time.sleep(0.01)  # 必要的等待时间，防止移动过快

        win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)

        _back_click_x = current_x
        _back_click_y = current_y
        logger.info(f"update ({_back_click_x},{_back_click_y})")

    @classmethod
    def drag(cls, x_offset: int = None, y_offset: int = None, duration: float = 0.5):
        """拖动，使用前需要先移动鼠标至当前位置

        参数:
            x_offset (int): 横轴拖动量
            y_offset (int): 纵轴拖动量
            duration (float): 持续时间
        """
        if config.backend:
            cls._drag_backend(x_offset, y_offset)
        else:
            cls._drag_front(x_offset, y_offset, duration)

    @classmethod
    def _scroll_front(cls, distance: int):
        pyautogui.scroll(distance)

    @classmethod
    def _scroll_backend(cls, distance: int):
        hwnd = window.handle
        current_x = _back_click_x
        current_y = _back_click_y

        cls._win_scroll(hwnd, distance, win32api.MAKELONG(int(current_x), int(current_y)))

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
        if config.backend:
            cls._scroll_backend(distance)
        else:
            cls._scroll_front(distance)
        logger.info(f"scroll at ({distance})")


class KeyBoard:
    """键盘事件"""

    _KEY_MAPPING = {
        "enter": win32con.VK_RETURN,
        "esc": win32con.VK_ESCAPE,
    }

    @classmethod
    def _front_operation(cls, key: str) -> None:
        pyautogui.press(key)

    @classmethod
    def _backend_operation(cls, key: str) -> None:
        vk_code = cls._KEY_MAPPING.get(key.lower())
        if not vk_code:
            raise ValueError(f"Unsupported key: {key}")

        hwnd = window.handle
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 1)

    @classmethod
    def send(cls, key: str, delay: float = 0) -> None:
        """发送按键事件"""
        if delay:
            time.sleep(delay)

        event_xuanshang.wait()
        logger.info(f"Sending key: {key.upper()}")

        if config.backend:
            cls._backend_operation(key)
        else:
            cls._front_operation(key)

    @classmethod
    def enter(cls, delay: float = 0) -> None:
        """发送回车键"""
        cls.send("enter", delay)

    @classmethod
    def esc(cls, delay: float = 0):
        """发送ESC键"""
        cls.send("esc", delay)
