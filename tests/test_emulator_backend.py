"""Task 6: 工厂 + MumuBackend 组装 + get_backend 缓存。"""
import numpy as np

import src.utils.emulator as E
from src.utils.emulator.mumu_backend import MumuBackend


def test_factory_returns_none_for_pc():
    assert E.create_backend("", handle_spec=1) is None
    assert E.create_backend("pc", handle_spec=1) is None


def _make_backend(monkeypatch):
    from src.utils.emulator.mumu_handle import MumuHandle
    h = MumuHandle(root_hwnd=100, root_title="MuMu安卓设备-1", shot_hwnd=111,
                   control_hwnds=[100, 111], scale_rate=1.0, client_w=700, client_h=400)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.build_handle", lambda spec: h)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.find_ipc_dll", lambda *a, **k: None)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuCapture", _FakeCap)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuInput", _FakeInp)
    return E.create_backend("mumu", handle_spec=100)


class _FakeCap:
    def __init__(self, handle, ipc=None):
        pass

    def capture(self):
        return np.full((400, 700, 3), 50, np.uint8)


class _FakeInp:
    def __init__(self, handle, ipc=None):
        self.calls = []

    def click(self, x, y):
        self.calls.append(("click", x, y))


def test_mumu_backend_screenshot_and_click(monkeypatch):
    b = _make_backend(monkeypatch)
    img = b.screenshot()
    assert img is not None and img.shape[:2] == (400, 700)


def test_get_backend_cached(monkeypatch):
    monkeypatch.setattr("src.utils.emulator.mumu_backend.build_handle", lambda spec: _H())
    monkeypatch.setattr("src.utils.emulator.mumu_backend.find_ipc_dll", lambda *a, **k: None)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuCapture", _FakeCap)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuInput", _FakeInp)
    a = E.get_backend(100, 1, "E:\\MuMuPlayer")
    b = E.get_backend(100, 1, "E:\\MuMuPlayer")
    assert a is b
    E.clear_backends()
    c = E.get_backend(100, 1, "E:\\MuMuPlayer")
    assert c is not a


def _patch_mumu_deps(monkeypatch, cap):
    """统一替换 MumuBackend 的 win32/cli 依赖（与 _make_backend 一致的隔离面）。"""
    monkeypatch.setattr("src.utils.emulator.mumu_backend.build_handle", lambda spec: _H())
    monkeypatch.setattr("src.utils.emulator.mumu_backend.find_ipc_dll", lambda *a, **k: None)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuCapture", lambda h, ipc=None: cap)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuInput", lambda h, ipc=None: _FakeInp(h, ipc))


class _FlakyCap:
    """前 fail_times 次 capture 返回 None（模拟器重启后 IPC 陈旧），之后返回帧。"""

    def __init__(self, fail_times=1):
        self.fail_times = fail_times
        self.attempts = 0

    def capture(self):
        self.attempts += 1
        if self.attempts <= self.fail_times:
            return None
        return np.full((400, 700, 3), 50, np.uint8)


class _DeadCap:
    def capture(self):
        return None


def test_screenshot_reconnects_and_retries_once(monkeypatch):
    """Imp #3: capture 返回 None → reconnect 一次 → 重试一次拿到帧；成功路径不掉缓存。"""
    E.clear_backends()
    cap = _FlakyCap(fail_times=1)
    _patch_mumu_deps(monkeypatch, cap)
    b = E.get_backend(100, 1, "E:\\MuMuPlayer")
    monkeypatch.setattr(b, "reconnect", lambda: None)  # 重连成功（生产为 NemuIpc 重建）
    img = b.screenshot()
    assert img is not None and img.shape[:2] == (400, 700)
    assert cap.attempts == 2  # 首次失败 + 重试一次
    assert E.get_backend(100, 1, "E:\\MuMuPlayer") is b  # 成功路径不丢弃缓存


def test_screenshot_drops_cache_when_reconnect_and_retry_fail(monkeypatch):
    """Imp #3: reconnect 抛异常且重试仍 None → 丢弃缓存条目，下次 get_backend 重建实例。"""
    E.clear_backends()
    dead = _DeadCap()
    _patch_mumu_deps(monkeypatch, dead)
    b = E.get_backend(100, 1, "E:\\MuMuPlayer")

    def _broken_reconnect():
        raise RuntimeError("nemu ipc unreachable, take over manually")

    monkeypatch.setattr(b, "reconnect", _broken_reconnect)
    img = b.screenshot()
    assert img is None  # 瞬时黑屏不误伤：这里确实死了
    c = E.get_backend(100, 1, "E:\\MuMuPlayer")
    assert c is not b  # 缓存已丢弃 → 构造全新实例


class _H:
    root_hwnd = 100
    root_title = "MuMu安卓设备-1"
    shot_hwnd = 111
    control_hwnds = [100, 111]
    scale_rate = 1.0
    client_w = 700
    client_h = 400