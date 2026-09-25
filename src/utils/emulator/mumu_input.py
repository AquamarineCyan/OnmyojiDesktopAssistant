"""MuMu 输入：Send 主 + Post 辅，打控制子句柄。

OAS 对应逻辑：module/device/method/windows_impl.py（click/long/swipe_window_message）。
差异：IPC 可用时三者全走 IPC down/up；无 IPC 才走消息。
"""
from __future__ import annotations

import random
import time
from typing import Optional

import win32con
from win32api import PostMessage, SendMessage

from .mumu_handle import MumuHandle


def _send(hwnd: int, msg: int, w: int, l: int) -> None:
    SendMessage(hwnd, msg, w, l)


def _post(hwnd: int, msg: int, w: int, l: int) -> None:
    PostMessage(hwnd, msg, w, l)


def _sleep(s: float) -> None:
    time.sleep(max(0.0, s))


def pack_lparam(x: int, y: int) -> int:
    from win32api import MAKELONG
    return MAKELONG(int(x), int(y))


def phys(handle: MumuHandle, x: float, y: float) -> tuple[int, int]:
    s = getattr(handle, "scale_rate", 1.0) or 1.0
    if s <= 0:
        s = 1.0
    return (int(float(x) / s), int(float(y) / s))


def build_trace(x1: int, y1: int, x2: int, y2: int, n: int = 20) -> list[tuple[int, int]]:
    n = max(2, int(n))
    pts: list[tuple[int, int]] = []
    for i in range(n):
        t = i / (n - 1)
        px = x1 + (x2 - x1) * t + random.uniform(-3, 3)
        py = y1 + (y2 - y1) * t + random.uniform(-3, 3)
        pts.append((int(px), int(py)))
    pts[0] = (int(x1), int(y1))
    pts[-1] = (int(x2), int(y2))
    return pts


class MumuInput:
    def __init__(self, handle: MumuHandle, ipc: Optional[object] = None):
        self.handle = handle
        self.ipc = ipc

    def _target(self) -> int:
        hwnds = self.handle.control_hwnds
        return hwnds[1] if len(hwnds) > 1 else hwnds[0]

    def _to_ipc(self, x: float, y: float) -> tuple[int, int]:
        """客户区坐标 → IPC 原生坐标（窗口缩放时按比例换算）。"""
        try:
            iw = int(getattr(self.ipc, "width", 0) or 0)
            ih = int(getattr(self.ipc, "height", 0) or 0)
            if iw <= 0 or ih <= 0:
                self.ipc.get_resolution()
                iw = int(getattr(self.ipc, "width", 0) or 0)
                ih = int(getattr(self.ipc, "height", 0) or 0)
            cw = int(getattr(self.handle, "client_w", 0) or 0)
            ch = int(getattr(self.handle, "client_h", 0) or 0)
            if iw > 0 and ih > 0 and cw > 0 and ch > 0 and (cw != iw or ch != ih):
                return (int(round(float(x) * iw / cw)), int(round(float(y) * ih / ch)))
        except Exception:
            pass
        return int(x), int(y)

    def click(self, x: int, y: int) -> None:
        if self.ipc is not None:
            ix, iy = self._to_ipc(x, y)
            self.ipc.down(ix, iy)
            _sleep(random.uniform(0.05, 0.11))
            self.ipc.down(ix + random.randint(-2, 2), iy + random.randint(-2, 2))
            _sleep(random.uniform(0.008, 0.02))
            self.ipc.up()
            return
        px, py = phys(self.handle, x, y)
        lp = pack_lparam(px, py)
        t = self._target()
        _send(t, win32con.WM_ACTIVATE, 1, 0)
        _send(t, win32con.WM_LBUTTONDOWN, 0, lp)
        _sleep(random.uniform(0.1, 0.2))
        _send(t, win32con.WM_LBUTTONUP, 0, lp)

    def down(self, x: int, y: int) -> None:
        """按下：IPC 走 down；无 IPC 打 control 子句柄（深层）的 WM_LBUTTONDOWN。"""
        if self.ipc is not None:
            ix, iy = self._to_ipc(x, y)
            self.ipc.down(ix, iy)
            return
        px, py = phys(self.handle, x, y)
        t = self._target()
        _send(t, win32con.WM_ACTIVATE, 1, 0)
        _send(t, win32con.WM_LBUTTONDOWN, 0, pack_lparam(px, py))

    def move(self, x: int, y: int, pressed: bool = False) -> None:
        """移动：IPC 只有 down/up，按住时用 down 续点模拟拖拽（悬停 IPC 无能力）。

        无 IPC 时打 WM_MOUSEMOVE，按住带 MK_LBUTTON。
        """
        if self.ipc is not None:
            if not pressed:
                return
            ix, iy = self._to_ipc(x, y)
            self.ipc.down(ix, iy)
            return
        px, py = phys(self.handle, x, y)
        _post(self._target(), win32con.WM_MOUSEMOVE,
              win32con.MK_LBUTTON if pressed else 0, pack_lparam(px, py))

    def up(self, x: int, y: int) -> None:
        """抬起：IPC 走 up；无 IPC 打 WM_LBUTTONUP（坐标按 scale 换算）。"""
        if self.ipc is not None:
            self.ipc.up()
            return
        px, py = phys(self.handle, x, y)
        _send(self._target(), win32con.WM_LBUTTONUP, 0, pack_lparam(px, py))

    def long_click(self, x: int, y: int, duration: float) -> None:
        duration = max(0.0, float(duration))
        if self.ipc is not None:
            ix, iy = self._to_ipc(x, y)
            self.ipc.down(ix, iy)
            _sleep(duration)
            self.ipc.up()
            return
        px, py = phys(self.handle, x, y)
        lp = pack_lparam(px, py)
        t = self._target()
        _send(t, win32con.WM_ACTIVATE, 1, 0)
        _send(t, win32con.WM_LBUTTONDOWN, 0, lp)
        _sleep(duration)
        _send(t, win32con.WM_LBUTTONUP, 0, lp)

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> None:
        if self.ipc is not None:
            for px, py in build_trace(int(x1), int(y1), int(x2), int(y2)):
                ix, iy = self._to_ipc(px, py)
                self.ipc.down(ix, iy)
                _sleep(random.uniform(0.006, 0.015))
            self.ipc.up()
            return
        t = self._target()
        p1 = phys(self.handle, x1, y1)
        p2 = phys(self.handle, x2, y2)
        trace = build_trace(*p1, *p2)
        first = pack_lparam(*trace[0])
        _send(t, win32con.WM_NCHITTEST, 0, first)
        _send(t, win32con.WM_SETCURSOR, t, pack_lparam(1, win32con.WM_LBUTTONDOWN))
        _post(t, win32con.WM_LBUTTONDOWN, 0, first)
        for px, py in trace:
            _post(t, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, pack_lparam(px, py))
            _sleep(0.01)
        _post(t, win32con.WM_LBUTTONUP, 0, pack_lparam(*trace[-1]))
