"""MumuBackend：组装 handle + capture + input + IPC，对外实现 EmulatorBackend。"""
from __future__ import annotations

import ctypes
from typing import Optional

import numpy as np

from ..log import logger

from .backend import EmulatorBackend
from .mumu_capture import MumuCapture
from .mumu_handle import build_handle, is_window
from .mumu_input import MumuInput
from .nemu_ipc import NemuIpc, find_ipc_dll


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


class MumuBackend(EmulatorBackend):
    _admin_warned = False

    def __init__(self, handle_spec: str = "auto", instance_index: int = 0,
                 mumu_folder: str = "", ipc_dll_override: str = ""):
        from . import mumu_handle as _mh
        if str(handle_spec) == "auto":
            # resolve_auto 返回 HWND；build_handle 校验句柄树
            spec, self._instance_id = _mh.resolve_auto(instance_index, mumu_folder)
        else:
            spec = handle_spec
            self._instance_id = int(instance_index)
            # 显式句柄时用 cli 反查真实实例号（多开/改名场景下 IPC 才对得上号）
            try:
                spec_int = int(spec)
            except (ValueError, TypeError):
                spec_int = None
            if spec_int is not None:
                try:
                    for hwnd, iid, _n in _mh.query_cli_windows(mumu_folder):
                        if int(hwnd) == spec_int:
                            self._instance_id = int(iid)
                            break
                except Exception:
                    pass
        self._handle = build_handle(spec)
        self._folder = mumu_folder
        self._override = ipc_dll_override
        self._ipc: Optional[NemuIpc] = None
        self._connect_ipc()
        if self._ipc is not None:
            # v6 真前台在 "default" display（如 5）上，不主动解析则停留在桌面 display 0
            try:
                self._ipc.refresh_display_id("default")
            except Exception:
                pass
        self.is_elevated = is_admin()
        if not self.is_elevated and not MumuBackend._admin_warned:
            MumuBackend._admin_warned = True
            logger.warning("not running as admin; SendMessage to MuMu child window may fail — prefer NemuIPC input or relaunch elevated")
        self._cap = MumuCapture(self._handle, self._ipc)
        self._input = MumuInput(self._handle, self._ipc)

    def _connect_ipc(self) -> None:
        dll = find_ipc_dll(self._folder, self._override)
        if not dll:
            self._ipc = None
            return
        try:
            ipc = NemuIpc(dll, self._instance_id, self._folder or "E:\\MuMuPlayer")
            ipc.connect()
            self._ipc = ipc
        except Exception:
            self._ipc = None

    def reconnect(self) -> None:
        last: Optional[Exception] = None
        for _ in range(3):
            try:
                if self._ipc is not None:
                    try:
                        self._ipc.disconnect()
                    except Exception:
                        pass
                self._connect_ipc()
                if self._ipc is not None:
                    return
            except Exception as e:
                last = e
        raise RuntimeError("nemu ipc unreachable, take over manually") from last

    def screenshot(self) -> Optional[np.ndarray]:
        if not is_window(self._handle.root_hwnd):
            self._handle = build_handle(self._handle.root_hwnd)
            self._cap = MumuCapture(self._handle, self._ipc)
            self._input = MumuInput(self._handle, self._ipc)
        try:
            img = self._cap.capture()
        except Exception:
            return None
        if img is not None:
            return img
        # capture 返回 None（模拟器重启后 IPC connect_id 仍 >0，connect() 短路 → 永久黑屏）：
        # 重连一次 → 重试一次；重试仍失败（或重连抛异常）才丢弃缓存条目，让下次 get_backend 重建。
        # 瞬时黑屏/遮挡等偶发 None 不在此列（重试成功则不丢缓存）。
        try:
            self.reconnect()
            self._cap = MumuCapture(self._handle, self._ipc)
            self._input = MumuInput(self._handle, self._ipc)
            retry = self._cap.capture()
        except Exception:
            retry = None
        if retry is None:
            # 函数级 import 避免环：包 __init__ 导入本模块（创建缓存），本模块不能在模块级导入包
            from . import drop_backend
            drop_backend(self._handle.root_hwnd, self._instance_id,
                         self._folder, self._override)
            return None
        return retry

    def click(self, x: int, y: int) -> None:
        self._input.click(int(x), int(y))

    def down(self, x: int, y: int) -> None:
        """拖拽按下（同步器链路用）."""
        self._input.down(int(x), int(y))

    def move(self, x: int, y: int, pressed: bool = False) -> None:
        """拖拽移动（同步器链路用）."""
        self._input.move(int(x), int(y), bool(pressed))

    def up(self, x: int, y: int) -> None:
        """拖拽抬起（同步器链路用）."""
        self._input.up(int(x), int(y))

    def long_click(self, x: int, y: int, duration: float) -> None:
        self._input.long_click(int(x), int(y), float(duration))

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> None:
        self._input.swipe(int(x1), int(y1), int(x2), int(y2), float(duration))

    def instance_hwnds(self) -> list[int]:
        return [self._handle.root_hwnd]

    def close(self) -> None:
        if self._ipc is not None:
            try:
                self._ipc.disconnect()
            except Exception:
                pass
