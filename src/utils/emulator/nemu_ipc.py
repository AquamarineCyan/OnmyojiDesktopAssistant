"""NemuIPC：DLL 定位 + ctypes 封装（MuMu ≥ 3.8.13）。

OAS 对应逻辑：module/device/method/nemu_ipc.py（NemuIpcImpl / serial_to_id）。
本机差异：候选首位为 nx_main/sdk（OAS 缺失的新版主路径）。
注意：capture 返回倒置 RGBA，调用方必须 flip(0) 后转 BGR。
"""
from __future__ import annotations

import ctypes
import os
from typing import Optional

import numpy as np


class NemuIpcIncompatible(Exception):
    pass


class NemuIpcError(Exception):
    pass


DLL_CANDIDATES = (
    "nx_main/sdk/external_renderer_ipc.dll",
    "nx_device/12.0/shell/sdk/external_renderer_ipc.dll",
    "nx_device/15.0/shell/sdk/external_renderer_ipc.dll",
    "shell/sdk/external_renderer_ipc.dll",
)


def find_ipc_dll(mumu_folder: str, override: str = "") -> Optional[str]:
    if override and os.path.isfile(override):
        return override
    root = (mumu_folder or "").strip()
    if not root:
        return None
    for rel in DLL_CANDIDATES:
        cand = os.path.join(root, *rel.split("/"))
        if os.path.isfile(cand):
            return os.path.abspath(cand)
    return None


class NemuIpc:
    def __init__(self, dll_path: str, instance_id: int, mumu_root: str = ""):
        try:
            self.lib = ctypes.CDLL(dll_path)
        except OSError as e:
            raise NemuIpcIncompatible(f"cannot load {dll_path}: {e}") from e
        lib = self.lib
        lib.nemu_connect.argtypes = [ctypes.c_wchar_p, ctypes.c_int]
        lib.nemu_connect.restype = ctypes.c_int
        lib.nemu_disconnect.argtypes = [ctypes.c_int]
        lib.nemu_disconnect.restype = ctypes.c_int
        lib.nemu_capture_display.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
            ctypes.c_void_p,
        ]
        lib.nemu_capture_display.restype = ctypes.c_int
        lib.nemu_input_event_touch_down.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        lib.nemu_input_event_touch_down.restype = ctypes.c_int
        lib.nemu_input_event_touch_up.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.nemu_input_event_touch_up.restype = ctypes.c_int
        lib.nemu_input_event_finger_touch_down.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        lib.nemu_input_event_finger_touch_down.restype = ctypes.c_int
        lib.nemu_input_event_finger_touch_up.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        lib.nemu_input_event_finger_touch_up.restype = ctypes.c_int
        lib.nemu_get_display_id.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        lib.nemu_get_display_id.restype = ctypes.c_int
        self.instance_id = int(instance_id)
        self.connect_id = 0
        self.width = 0
        self.height = 0
        self.display_id = 0
        # nemu_connect 要的是安装根目录（如 E:\MuMuPlayer），不是 DLL 所在目录
        self._mumu_root = mumu_root or os.path.dirname(dll_path)

    def connect(self) -> None:
        if self.connect_id > 0:
            return
        folder = self._mumu_root
        cid = self.lib.nemu_connect(folder, self.instance_id)
        if cid == 0:
            raise NemuIpcError("nemu_connect failed: emulator not running or folder wrong")
        self.connect_id = int(cid)

    def disconnect(self) -> None:
        if self.connect_id:
            try:
                self.lib.nemu_disconnect(self.connect_id)
            finally:
                self.connect_id = 0

    def get_resolution(self) -> None:
        if not self.connect_id:
            self.connect()
        w = ctypes.pointer(ctypes.c_int(0))
        h = ctypes.pointer(ctypes.c_int(0))
        ret = self.lib.nemu_capture_display(self.connect_id, self.display_id, 0, w, h, None)
        if ret > 0:
            raise NemuIpcError("nemu_capture_display failed in get_resolution")
        self.width, self.height = w.contents.value, h.contents.value

    def refresh_display_id(self, package: str = "", cloned_index: int = 0) -> int:
        """按包名解析游戏 display（MAA 同款）；失败保持原 display_id。"""
        if not self.connect_id:
            self.connect()
        pkg = (package or "").strip() or "default"
        try:
            did = self.lib.nemu_get_display_id(
                self.connect_id, pkg.encode("utf-8"), int(cloned_index))
        except Exception:
            return self.display_id
        if isinstance(did, int) and did >= 0:
            self.display_id = did
        return self.display_id

    def capture(self) -> np.ndarray:
        if not self.connect_id:
            self.connect()
        if self.width <= 0 or self.height <= 0:
            self.get_resolution()
        length = self.width * self.height * 4
        buf = (ctypes.c_ubyte * length)()
        w = ctypes.pointer(ctypes.c_int(self.width))
        h = ctypes.pointer(ctypes.c_int(self.height))
        ret = self.lib.nemu_capture_display(
            self.connect_id, self.display_id, length, w, h, ctypes.cast(buf, ctypes.c_void_p))
        if ret > 0:
            raise NemuIpcError("nemu_capture_display failed in capture")
        return np.ctypeslib.as_array(buf).reshape((self.height, self.width, 4))

    def down(self, x: int, y: int, contact: int = 0) -> None:
        """finger 版触摸按下（MAA 同款：contact 从 1 起，原生坐标，无需翻转）"""
        if not self.connect_id:
            self.connect()
        if self.height == 0:
            self.get_resolution()
        ret = self.lib.nemu_input_event_finger_touch_down(
            self.connect_id, self.display_id, int(contact) + 1, int(x), int(y))
        if ret > 0:
            raise NemuIpcError("nemu_input_event_finger_touch_down failed")

    def up(self, contact: int = 0) -> None:
        """finger 版触摸抬起"""
        if not self.connect_id:
            self.connect()
        ret = self.lib.nemu_input_event_finger_touch_up(
            self.connect_id, self.display_id, int(contact) + 1)
        if ret > 0:
            raise NemuIpcError("nemu_input_event_finger_touch_up failed")
