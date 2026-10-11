"""模拟器后台支持包（MuMu 模拟器）。"""
from __future__ import annotations

import threading
from typing import Optional

from ..log import logger
from .backend import EmulatorBackend, create_backend
from .mumu_backend import MumuBackend

_BACKEND_CACHE: dict[tuple, "MumuBackend"] = {}
_CREATE_FAILED_WARNED: set[tuple] = set()
_CACHE_LOCK = threading.RLock()
"""缓存锁

`get_backend` 同时被截图线程（ScreenShot）、输入线程（adapter）调用，
而 key 里带着用户可改的 mumu_folder / ipc_dll_override：
并发 miss 会各自 create 出一个 backend，落败的那个 IPC 连接再也无法被 close，
随进程常驻。
"""


def get_backend(root_hwnd: int, instance_index: int, mumu_folder: str = "",
                ipc_dll_override: str = "") -> Optional[MumuBackend]:
    key = (int(root_hwnd), int(instance_index), mumu_folder or "", ipc_dll_override or "")
    with _CACHE_LOCK:
        if key in _BACKEND_CACHE:
            return _BACKEND_CACHE[key]
    try:
        b = create_backend("mumu", handle_spec=key[0], instance_index=key[1],
                           mumu_folder=key[2], ipc_dll_override=key[3])
    except Exception as e:
        # 窗口树失效等构造失败不得抛给输入/截图分发链路（键盘 enter/esc 也会走到这里）；
        # 同一窗口只提示一次，避免按键循环刷屏
        with _CACHE_LOCK:
            first_time = key not in _CREATE_FAILED_WARNED
            _CREATE_FAILED_WARNED.add(key)
        if first_time:
            logger.warning(f"创建模拟器后端失败（同一窗口后续失败不再提示）：{e!r}")
        return None
    if b is not None:
        with _CACHE_LOCK:
            # 构造期间可能已被另一个线程抢先填好，此时要关掉自己这个，
            # 否则多出来的 IPC 连接泄漏
            existing = _BACKEND_CACHE.setdefault(key, b)
            if existing is not b:
                try:
                    b.close()
                except Exception:
                    pass
                return existing
    return b


def drop_backend(root_hwnd: int, instance_index: int, mumu_folder: str = "",
                 ipc_dll_override: str = "") -> None:
    """按 get_backend 相同 key 丢弃缓存条目并关闭底层资源。

    供 mumu_backend 在确定性失效（重连+重试仍失败）时调用，使下一次 get_backend 重建实例。
    为规避 import 环（本包 __init__ 导入 mumu_backend），mumu_backend 在调用点以函数级 import 引入。

    注意必须 close：原先只 pop 不关，模拟器重启/黑屏恢复每发生一次
    就泄漏一个 nemu_connect 会话，反复失败会持续累积。
    """
    key = (int(root_hwnd), int(instance_index), mumu_folder or "", ipc_dll_override or "")
    with _CACHE_LOCK:
        backend = _BACKEND_CACHE.pop(key, None)
        _CREATE_FAILED_WARNED.discard(key)
    if backend is not None:
        try:
            backend.close()
        except Exception as e:
            logger.warning(f"关闭模拟器后端失败: {e!r}")


def clear_backends() -> None:
    with _CACHE_LOCK:
        backends = list(_BACKEND_CACHE.values())
        _BACKEND_CACHE.clear()
        _CREATE_FAILED_WARNED.clear()
    for b in backends:
        try:
            b.close()
        except Exception:
            pass
