import copy
import random
import time
from typing import ClassVar

import pyautogui
import pytweening
import win32api
import win32con

from .config import InteractionMode, config
from .coordinate import get_scale, to_actual, to_reference
from .event import event_thread, event_xuanshang
from .exception import GUIStopException
from .log import logger
from .point import Point
from .window import window_manager

_back_click_point = Point(0, 0)  # 当前位置


def linear(n):
    """
    Returns ``n``, where ``n`` is the float argument between ``0.0`` and ``1.0``. This function is for the default
    linear tween for mouse moving functions.

    This function was copied from PyTweening module, so that it can be called even if PyTweening is not installed.
    """

    # We use this function instead of pytweening.linear for the default tween function just in case pytweening couldn't be imported.
    if not 0.0 <= n <= 1.0:
        raise ValueError("Argument must be between 0.0 and 1.0.")
    return n


class Mouse:
    """鼠标事件"""

    @classmethod
    def position(cls) -> Point:
        abs_x, abs_y = pyautogui.position()
        point = Point.from_screen(abs_x, abs_y)
        return Point(*to_reference(point.client_x, point.client_y))

    @staticmethod
    def random_tween():
        """补间移动，模拟真人运动轨迹"""
        tweens = [
            pytweening.easeInQuad,
            pytweening.easeOutQuad,
            pytweening.easeInOutQuad,
        ]
        return random.choice(tweens)

    @staticmethod
    def _mumu_backend() -> object | None:
        """当前窗口是 mumu 时返回缓存后端，否则 None（按窗口归属自动路由）。"""
        from .emulator import get_backend

        w = window_manager.current
        if w is None or getattr(w, "family", "pc") != "mumu":
            return None
        return get_backend(
            w.handle,
            w.instance_index,
            config.user.interaction_mode.backend.mumu_folder,
            config.user.interaction_mode.backend.ipc_dll_override,
        )

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
        dst_point: Point | None = None,
        x: float | None = None,
        y: float | None = None,
        xOffset: float | None = None,
        yOffset: float | None = None,
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
                else:
                    x, y = dst_point.to_screen()
                pyautogui.moveTo(x, y, duration, tween)

        except pyautogui.FailSafeException:
            logger.error("鼠标移动失败，请检查是否点击了屏幕左上角，请重启后使用")
            return

    @classmethod
    def _move_backend(
        cls,
        dst_point: Point | None = None,
        x: float | None = None,
        y: float | None = None,
        xOffset: float | None = None,
        yOffset: float | None = None,
    ):
        global _back_click_point

        if cls._mumu_backend() is not None:
            if dst_point is not None:
                # mumu 的 move 不下发（IPC 无悬停），但必须同步锚点，否则后续
                # _drag_backend 从陈旧点起滑（tansuo.py"移动视角"即 move 后 drag）
                _back_click_point = dst_point
            logger.info("mumu backend: move 忽略（IPC 无悬停）")
            return

        # 使用客户区坐标作为目标位置
        if dst_point is None:
            if x is not None and y is not None:
                dst_point = Point(x, y)
            else:
                return

        hwnd = window_manager.get_current_handle()
        if hwnd is None:
            return
        current_point = _back_click_point

        # 计算移动的步数
        steps = int(
            max(abs(dst_point.client_x - current_point.client_x), abs(dst_point.client_y - current_point.client_y))
        )
        if steps == 0:
            logger.warning("steps is 0")
            steps = 1

        # 计算每一步的增量
        x_step = (dst_point.client_x - current_point.client_x) / steps
        y_step = (dst_point.client_y - current_point.client_y) / steps
        logger.info(f"steps:{steps}, x_step:{x_step}, y_step:{y_step}")

        temp_point = copy.copy(current_point)
        for _ in range(steps):
            temp_point.client_x += x_step
            temp_point.client_y += y_step
            lParam = win32api.MAKELONG(int(temp_point.client_x), int(temp_point.client_y))
            cls._win_move(hwnd, lParam)

        # 最后一步确保到达目标位置
        lParam = win32api.MAKELONG(int(dst_point.client_x), int(dst_point.client_y))
        cls._win_move(hwnd, lParam)

        _back_click_point = dst_point
        logger.info(f"update ({_back_click_point.client_x},{_back_click_point.client_y})")

    @classmethod
    def move(
        cls,
        point: Point | None = None,
        x: float | None = None,
        y: float | None = None,
        xOffset: float | None = None,
        yOffset: float | None = None,
        duration: float = 0,
        tween=linear,
    ):
        # 业务侧坐标是基准空间；xOffset/yOffset 是相对位移，不做换算
        if point is not None:
            point = Point(*to_actual(point.client_x, point.client_y))
        elif x is not None and y is not None:
            x, y = to_actual(x, y)
        if config.user.interaction_mode.mode == InteractionMode.BACKEND:
            cls._move_backend(point, x, y, xOffset, yOffset)
        else:
            cls._move_front(point, x, y, xOffset, yOffset, duration, tween)

    @classmethod
    def _click_front(cls, point: Point | None = None, duration: float = 0.5):
        if point is None:
            x, y = pyautogui.position()
            logger.info("click at current position")
        else:
            x, y = point.to_screen()
            logger.info(f"Point:({x},{y})")

        # cls.move(x=_x, y=_y, duration=duration, tween=random.choice(list_tween))
        # logger.info(f"click at ({x},{y})")
        # cls.send_mouse_event(0x6, x, y, 0)
        try:
            pyautogui.click(x, y, duration=duration, tween=cls.random_tween())
        except pyautogui.FailSafeException:
            logger.error(f"click error at ({x},{y})")
            logger.ui_error("安全错误，可能是您点击了屏幕左上角，请重启后使用")

    @classmethod
    def _click_backend(cls, point: Point | None = None):
        global _back_click_point

        if point is None:
            dst_point = _back_click_point
        else:
            dst_point = point

        backend = cls._mumu_backend()
        if backend is not None:
            backend.click(int(dst_point.client_x), int(dst_point.client_y))
            _back_click_point = dst_point
            return

        hwnd = window_manager.get_current_handle()
        if hwnd is None:
            return
        current_point = _back_click_point

        # 计算移动的步数
        steps = int(
            max(
                abs(dst_point.client_x - current_point.client_x),
                abs(dst_point.client_y - current_point.client_y),
            )
        )
        if steps == 0:
            logger.info("steps is 0")
            steps = 1

        # 计算每一步的增量
        x_step = (dst_point.client_x - current_point.client_x) / steps
        y_step = (dst_point.client_y - current_point.client_y) / steps
        logger.info(f"steps:{steps}, x_step:{x_step}, y_step:{y_step}")

        temp_point = copy.copy(current_point)
        for _ in range(steps):
            temp_point.client_x += x_step
            temp_point.client_y += y_step
            lParam = win32api.MAKELONG(int(temp_point.client_x), int(temp_point.client_y))
            cls._win_move(hwnd, lParam)

        # 最后一步确保到达目标位置
        lParam = win32api.MAKELONG(int(dst_point.client_x), int(dst_point.client_y))
        cls._win_move(hwnd, lParam)

        # 模拟鼠标按下和释放
        cls._win_left_click(hwnd, lParam)

        _back_click_point = dst_point
        logger.info(f"update ({_back_click_point.client_x},{_back_click_point.client_y})")

    @classmethod
    def click(
        cls,
        point: Point | None = None,
        duration: float = 0.5,
        wait: float = 0,
    ) -> None:
        """点击

        参数:
            point (Point | None): 坐标
            duration (float): 持续时间
            wait (float): 前置等待时间
        """
        if bool(event_thread):
            raise GUIStopException

        # 延迟
        if wait:
            time.sleep(wait)

        if point is not None:
            # 业务侧坐标是基准空间 → 实际客户区
            point = Point(*to_actual(point.client_x, point.client_y))

        if config.user.interaction_mode.mode == InteractionMode.BACKEND:
            # logger.info(f"backend click {point.x},{point.y}")
            cls._click_backend(point)
        else:
            # logger.info(f"front click {point.x},{point.y}")
            cls._click_front(point, duration)

    @classmethod
    def _drag_front(cls, x_offset: int | None = None, y_offset: int | None = None, duration: float = 0.5):
        pyautogui.dragRel(x_offset, y_offset, duration=duration, tween=cls.random_tween())

    @classmethod
    def _drag_backend(cls, x_offset: int | None = None, y_offset: int | None = None):
        global _back_click_point

        backend = cls._mumu_backend()
        if backend is not None:
            sx, sy = _back_click_point.client_x, _back_click_point.client_y
            backend.swipe(sx, sy, sx + x_offset, sy + y_offset)
            _back_click_point = Point(sx + x_offset, sy + y_offset)
            return

        hwnd = window_manager.get_current_handle()
        if hwnd is None:
            return
        temp_point = copy.copy(_back_click_point)
        # 计算移动的步数
        steps = max(abs(x_offset), abs(y_offset)) // 10
        if steps == 0:
            logger.info("steps is 0")
            steps = 1

        # 计算每一步的增量
        x_step = x_offset / steps
        y_step = y_offset / steps
        logger.info(f"steps:{steps}, x_step:{x_step}, y_step:{y_step}")

        lParam = win32api.MAKELONG(int(temp_point.client_x), int(temp_point.client_y))
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)

        for _ in range(steps):
            temp_point.client_x += x_step
            temp_point.client_y += y_step
            lParam = win32api.MAKELONG(int(temp_point.client_x), int(temp_point.client_y))
            win32api.PostMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, lParam)
            time.sleep(0.01)  # 必要的等待时间，防止移动过快

        win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)

        _back_click_point = temp_point
        logger.info(f"update ({_back_click_point.client_x},{_back_click_point.client_y})")

    @classmethod
    def drag(cls, x_offset: int | None = None, y_offset: int | None = None, duration: float = 0.5):
        """拖动，使用前需要先移动鼠标至当前位置

        参数:
            x_offset (int): 横轴拖动量
            y_offset (int): 纵轴拖动量
            duration (float): 持续时间
        """
        if x_offset is not None and y_offset is not None:
            # 业务侧拖动量是基准空间位移 → 实际客户区
            fx, fy = get_scale()
            x_offset, y_offset = x_offset * fx, y_offset * fy
        if config.user.interaction_mode.mode == InteractionMode.BACKEND:
            cls._drag_backend(x_offset, y_offset)
        else:
            cls._drag_front(x_offset, y_offset, duration)

    @classmethod
    def _scroll_front(cls, distance: int):
        pyautogui.scroll(distance)

    @classmethod
    def _scroll_backend(cls, distance: int):
        if cls._mumu_backend() is not None:
            logger.ui_warn("模拟器后台暂不支持滚轮（范围外）")
            return
        hwnd = window_manager.get_current_handle()
        if hwnd is None:
            return
        temp_point = copy.copy(_back_click_point)
        lParam = win32api.MAKELONG(int(temp_point.client_x), int(temp_point.client_y))
        cls._win_scroll(hwnd, distance, lParam)

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
        if config.user.interaction_mode.mode == InteractionMode.BACKEND:
            cls._scroll_backend(distance)
        else:
            cls._scroll_front(distance)
        logger.info(f"scroll at ({distance})")


class KeyBoard:
    """键盘事件"""

    _KEY_MAPPING: ClassVar[dict[str, int]] = {
        "enter": win32con.VK_RETURN,
        "esc": win32con.VK_ESCAPE,
    }

    @classmethod
    def _front_operation(cls, key: str) -> None:
        pyautogui.press(key)

    @classmethod
    def _backend_operation(cls, key: str) -> None:
        if Mouse._mumu_backend() is not None:
            logger.ui_warn("模拟器后台暂不支持键盘输入（范围外）")
            return

        vk_code = cls._KEY_MAPPING.get(key.lower())
        if not vk_code:
            raise ValueError(f"Unsupported key: {key}")

        hwnd = window_manager.get_current_handle()
        if hwnd is None:
            return
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 1)

    @classmethod
    def _dispatch(cls, key: str) -> None:
        """按交互模式分发按键"""
        if config.user.interaction_mode.mode == InteractionMode.BACKEND:
            cls._backend_operation(key)
        else:
            cls._front_operation(key)

    @classmethod
    def send(cls, key: str, delay: float = 0) -> None:
        """发送按键事件"""
        if delay:
            time.sleep(delay)

        event_xuanshang.wait()
        logger.info(f"Sending key: {key.upper()}")
        cls._dispatch(key)

    @classmethod
    def enter(cls, delay: float = 0) -> None:
        """发送回车键

        注意：模拟器里回车无法确认弹窗（游戏不响应），确认请改用 `BasePackage.confirm()`。
        """
        if Mouse._mumu_backend() is not None:
            logger.ui_warn("模拟器下回车无法确认弹窗，请改用 BasePackage.confirm()")
        cls.send("enter", delay)

    @classmethod
    def esc(cls, delay: float = 0) -> None:
        """发送「返回」键

        模拟器改用鼠标后退侧键（XBUTTON1）——模拟器后端不转发键盘输入，
        但鼠标后退侧键会被识别为安卓返回，效果等价 esc；桌面版行为不变。
        """
        if delay:
            time.sleep(delay)

        event_xuanshang.wait()
        backend = Mouse._mumu_backend()
        if backend is not None:
            logger.info("Sending back button: mouse XBUTTON1")
            backend.press_back()
            return
        logger.info("Sending key: ESC (back)")
        cls._dispatch("esc")
