"""模拟器后台支持包（MuMu 模拟器）。"""
from __future__ import annotations

from typing import Optional

from .backend import EmulatorBackend, create_backend
from .mumu_backend import MumuBackend

_BACKEND_CACHE: dict[tuple, "MumuBackend"] = {}


def get_backend(root_hwnd: int, instance_index: int, mumu_folder: str = "",
                ipc_dll_override: str = "") -> Optional[MumuBackend]:
    key = (int(root_hwnd), int(instance_index), mumu_folder or "", ipc_dll_override or "")
    if key in _BACKEND_CACHE:
        return _BACKEND_CACHE[key]
    b = create_backend("mumu", handle_spec=key[0], instance_index=key[1],
                       mumu_folder=key[2], ipc_dll_override=key[3])
    if b is not None:
        _BACKEND_CACHE[key] = b
    return b


def drop_backend(root_hwnd: int, instance_index: int, mumu_folder: str = "",
                 ipc_dll_override: str = "") -> None:
    """按 get_backend 相同 key 丢弃缓存条目（仅移除，不 close —— 由调用方决定时机）。

    供 mumu_backend 在确定性失效（重连+重试仍失败）时调用，使下一次 get_backend 重建实例。
    为规避 import 环（本包 __init__ 导入 mumu_backend），mumu_backend 在调用点以函数级 import 引入。
    """
    key = (int(root_hwnd), int(instance_index), mumu_folder or "", ipc_dll_override or "")
    _BACKEND_CACHE.pop(key, None)


def clear_backends() -> None:
    for b in _BACKEND_CACHE.values():
        try:
            b.close()
        except Exception:
            pass
    _BACKEND_CACHE.clear()