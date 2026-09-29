"""EmulatorBackend 抽象：截图统一 BGR，坐标统一客户区逻辑坐标。"""
import abc
from typing import Optional

import numpy as np


class EmulatorBackend(abc.ABC):
    @abc.abstractmethod
    def screenshot(self) -> Optional[np.ndarray]:
        """后台截图（BGR，尺寸=shot 客户区）；失败返回 None。"""

    @abc.abstractmethod
    def click(self, x: int, y: int) -> None:
        """客户区逻辑坐标点击。"""

    @abc.abstractmethod
    def down(self, x: int, y: int) -> None:
        """拖拽按下。"""

    @abc.abstractmethod
    def move(self, x: int, y: int, pressed: bool = False) -> None:
        """拖拽移动。"""

    @abc.abstractmethod
    def up(self, x: int, y: int) -> None:
        """拖拽抬起。"""

    @abc.abstractmethod
    def long_click(self, x: int, y: int, duration: float) -> None:
        """长按，duration 秒。"""

    @abc.abstractmethod
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> None:
        """滑动。"""

    @abc.abstractmethod
    def instance_hwnds(self) -> list[int]:
        """本 backend 覆盖的顶层 HWND。"""

    def close(self) -> None:
        """释放连接（默认空实现）。"""


def create_backend(emulator_type: str, handle_spec=None, instance_index: int = 0,
                   mumu_folder: str = "", ipc_dll_override: str = "") -> Optional[EmulatorBackend]:
    if emulator_type in ("mumu", "mumu12"):
        from .mumu_backend import MumuBackend
        return MumuBackend(handle_spec=handle_spec, instance_index=int(instance_index),
                           mumu_folder=mumu_folder, ipc_dll_override=ipc_dll_override)
    return None