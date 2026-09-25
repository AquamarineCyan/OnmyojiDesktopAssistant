"""MuMu 截图：nemu_ipc → PrintWindow → BitBlt，统一 BGR 输出。

输出尺寸与窗口客户区一致（模板按该尺度制作，必须同帧匹配才能命中）；
IPC 原生帧（如 1280x720）会按比例缩放到客户区大小。
Win32 部分复用 OAT/tools/GetDC.py 的 PW_CLIENTONLY→RENDERFULLCONTENT 策略，
黑屏门限 mean<5 与 GetDC.capture_window_bitblt 一致。
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Optional

import cv2
import numpy as np
import win32con
import win32gui
import win32ui

from .mumu_handle import MumuHandle
from .nemu_ipc import NemuIpc

REF_W, REF_H = 1280, 720
PW_CLIENTONLY = 1
PW_RENDERFULLCONTENT = 2

# pywin32 部分版本没有 win32gui.PrintWindow，统一走 ctypes（与 GetDC.py 同款）
try:
    _user32 = ctypes.windll.user32
    _PrintWindow = _user32.PrintWindow
    _PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
    _PrintWindow.restype = wintypes.BOOL
except Exception:
    _PrintWindow = None


def _is_black(img: np.ndarray) -> bool:
    try:
        return float(np.mean(img)) < 5.0
    except Exception:
        return True


def normalize_to(img: np.ndarray, width: int, height: int) -> np.ndarray:
    """缩放到指定尺寸；尺寸非法或已一致时原样返回。"""
    try:
        width, height = int(width), int(height)
    except (ValueError, TypeError):
        return img
    h, w = img.shape[:2]
    if width <= 0 or height <= 0 or (w, h) == (width, height):
        return img
    return cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)


class MumuCapture:
    def __init__(self, handle: MumuHandle, ipc: Optional[NemuIpc] = None):
        self.handle = handle
        self.ipc = ipc

    def _target_size(self) -> tuple[int, int]:
        """目标帧尺寸 = 渲染子窗口客户区实时尺寸（模板以此尺度制作）。"""
        hwnd = getattr(self.handle, "shot_hwnd", 0)
        try:
            cr = win32gui.GetClientRect(hwnd)
            w, h = cr[2] - cr[0], cr[3] - cr[1]
            if w > 0 and h > 0:
                return w, h
        except Exception:
            pass
        w = int(getattr(self.handle, "client_w", 0) or 0)
        h = int(getattr(self.handle, "client_h", 0) or 0)
        if w > 0 and h > 0:
            return w, h
        return REF_W, REF_H

    def capture(self) -> Optional[np.ndarray]:
        # 通道顺序：PrintWindow 原生像素（模板保真最高）→ IPC（最小化/遮挡兜底）→ BitBlt
        img = self._via_printwindow()
        if img is not None:
            return normalize_to(img, *self._target_size())
        img = self._via_ipc() if self.ipc is not None else None
        if img is not None:
            return normalize_to(img, *self._target_size())
        img = self._via_bitblt()
        if img is not None:
            return normalize_to(img, *self._target_size())
        return None

    def _via_ipc(self) -> Optional[np.ndarray]:
        try:
            raw = self.ipc.capture()
        except Exception:
            return None
        try:
            # MuMu IPC 返回 RGBA（实测：按 BGRA 处理会红蓝互换），倒置后转 BGR
            img = cv2.flip(raw, 0)
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        except Exception:
            return None
        return None if _is_black(img) else img

    def _grab(self, use_printwindow: bool) -> Optional[np.ndarray]:
        hwnd = self.handle.shot_hwnd
        hdc = None
        try:
            cr = win32gui.GetClientRect(hwnd)
            w, h = cr[2] - cr[0], cr[3] - cr[1]
            if w <= 0 or h <= 0:
                return None
            hdc = win32gui.GetDC(hwnd)
            mfc = win32ui.CreateDCFromHandle(hdc)
            mem = mfc.CreateCompatibleDC()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(mfc, w, h)
            mem.SelectObject(bmp)
            try:
                if use_printwindow:
                    if _PrintWindow is None:
                        return None
                    img = self._printwindow_grab(hwnd, mem, bmp, w, h)
                    if img is None:
                        return None
                    return img
                else:
                    mem.BitBlt((0, 0), (w, h), mfc, (0, 0), win32con.SRCCOPY)
                    bits = bmp.GetBitmapBits(True)
            finally:
                try:
                    win32gui.DeleteObject(bmp.GetHandle())
                except Exception:
                    pass
                try:
                    mem.DeleteDC()
                except Exception:
                    pass
                try:
                    mfc.DeleteDC()
                except Exception:
                    pass
                try:
                    win32gui.ReleaseDC(hwnd, hdc)
                except Exception:
                    pass
            img = np.frombuffer(bits, dtype=np.uint8).reshape((h, w, 4))
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        except Exception:
            if hdc is not None:
                try:
                    win32gui.ReleaseDC(hwnd, hdc)
                except Exception:
                    pass
            return None

    @staticmethod
    def _printwindow_grab(hwnd: int, mem, bmp, w: int, h: int) -> Optional[np.ndarray]:
        """PrintWindow 抓取：CLIENTONLY 可能返回成功但全黑（实测 MuMu），需按黑图回退。"""
        for f in (PW_CLIENTONLY, PW_RENDERFULLCONTENT):
            ok = _PrintWindow(hwnd, mem.GetSafeHdc(), f)
            if not ok:
                continue
            bits = bmp.GetBitmapBits(True)
            img = np.frombuffer(bits, dtype=np.uint8).reshape((h, w, 4))
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            if not _is_black(img):
                return img
        return None

    def _via_printwindow(self) -> Optional[np.ndarray]:
        img = self._grab(use_printwindow=True)
        return None if img is None or _is_black(img) else img

    def _via_bitblt(self) -> Optional[np.ndarray]:
        img = self._grab(use_printwindow=False)
        return None if img is None or _is_black(img) else img
