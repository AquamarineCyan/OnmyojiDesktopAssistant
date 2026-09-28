"""Task 6: 工厂 + MumuBackend 组装 + get_backend 缓存。"""
import numpy as np

import src.utils.emulator as E
from src.utils.emulator.mumu_backend import MumuBackend


def test_factory_returns_none_for_pc():
    assert E.create_backend("", handle_spec=1) is None
    assert E.create_backend("pc", handle_spec=1) is None


def test_get_backend_returns_none_when_create_fails(monkeypatch):
    """构造失败（窗口树失效等）不得把异常抛给输入/截图分发链路。"""
    E.clear_backends()

    def _boom(*a, **k):
        raise ValueError("not a MuMu window tree")

    monkeypatch.setattr(E, "create_backend", _boom)
    assert E.get_backend(998, 1, "E:\\MuMuPlayer") is None
    assert E.get_backend(998, 1, "E:\\MuMuPlayer") is None  # 不缓存失败，可重试


def _make_backend(monkeypatch):
    from src.utils.emulator.mumu_handle import MumuHandle
    h = MumuHandle(root_hwnd=100, root_title="MuMu安卓设备-1", shot_hwnd=111,
                   control_hwnds=[100, 111], scale_rate=1.0, client_w=700, client_h=400)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.build_handle", lambda *a, **k: h)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.detect_mumu_folder", lambda configured="": "")
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
    monkeypatch.setattr("src.utils.emulator.mumu_backend.build_handle", lambda *a, **k: _H())
    monkeypatch.setattr("src.utils.emulator.mumu_backend.detect_mumu_folder", lambda configured="": "")
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
    monkeypatch.setattr("src.utils.emulator.mumu_backend.build_handle", lambda *a, **k: _H())
    monkeypatch.setattr("src.utils.emulator.mumu_backend.detect_mumu_folder", lambda configured="": "")
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


class _FakeIpc:
    """记录 connect/refresh；refresh 后 display_id=2（游戏 display）。"""

    instances: list = []

    def __init__(self, dll, instance_id, root=""):
        self.dll = dll
        self.instance_id = instance_id
        self.root = root
        self.connect_id = 0
        self.display_id = 0
        self.refresh_calls: list = []
        _FakeIpc.instances.append(self)

    def connect(self):
        self.connect_id = 1

    def disconnect(self):
        self.connect_id = 0

    def refresh_display_id(self, package="", cloned_index=0):
        self.refresh_calls.append(package)
        self.display_id = 2
        return 2


def _patch_ipc(monkeypatch):
    _FakeIpc.instances = []
    monkeypatch.setattr("src.utils.emulator.mumu_backend.build_handle", lambda *a, **k: _H())
    monkeypatch.setattr("src.utils.emulator.mumu_backend.detect_mumu_folder", lambda configured="": "")
    monkeypatch.setattr(
        "src.utils.emulator.mumu_backend.find_ipc_dll", lambda *a, **k: "E:\\MuMuPlayer\\x.dll"
    )
    monkeypatch.setattr("src.utils.emulator.mumu_backend.NemuIpc", _FakeIpc)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuCapture", _FakeCap)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuInput", _FakeInp)


def test_reconnect_refreshes_display_id(monkeypatch):
    """C4: reconnect 重建 IPC 后必须重新解析游戏 display，否则截到/点到安卓桌面。"""
    E.clear_backends()
    _patch_ipc(monkeypatch)
    b = E.create_backend("mumu", handle_spec=100, instance_index=1, mumu_folder="E:\\MuMuPlayer")
    assert _FakeIpc.instances[-1].display_id == 2  # __init__ 已解析

    b.reconnect()

    new = _FakeIpc.instances[-1]
    assert new.refresh_calls, "reconnect 未调用 refresh_display_id"
    assert new.display_id == 2


def test_backend_resolves_empty_folder_via_detect(monkeypatch):
    """C2: 设置留空（文档默认）时后端仍须解析安装目录，否则 IPC 永不初始化。"""
    E.clear_backends()
    seen = {}

    def _fake_build(spec, mumu_folder="", wait_tries=10):
        seen["folder"] = mumu_folder
        return _H()

    def _fake_find(folder, override=""):
        seen["dll_folder"] = folder
        seen["override"] = override
        return None

    monkeypatch.setattr(
        "src.utils.emulator.mumu_backend.detect_mumu_folder",
        lambda configured="": "E:\\MuMuPlayer",
    )
    monkeypatch.setattr("src.utils.emulator.mumu_backend.build_handle", _fake_build)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.find_ipc_dll", _fake_find)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuCapture", _FakeCap)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuInput", _FakeInp)

    b = E.create_backend("mumu", handle_spec=100, instance_index=1, mumu_folder="")

    assert b._folder == "E:\\MuMuPlayer"
    assert seen["folder"] == "E:\\MuMuPlayer"  # build_handle 也拿到解析后的目录（cli render_wnd 权威）
    assert seen["dll_folder"] == "E:\\MuMuPlayer"


def test_ipc_root_derived_from_override_dll(monkeypatch):
    """C2: 只配 ipc_dll_override 时，nemu_connect 的根目录由 DLL 路径反推，不写死 E 盘。"""
    E.clear_backends()
    _FakeIpc.instances = []
    dll = "D:\\Apps\\MuMuPlayer\\nx_main\\sdk\\external_renderer_ipc.dll"
    monkeypatch.setattr("src.utils.emulator.mumu_backend.detect_mumu_folder", lambda configured="": "")
    monkeypatch.setattr("src.utils.emulator.mumu_backend.build_handle", lambda *a, **k: _H())
    monkeypatch.setattr(
        "src.utils.emulator.mumu_backend.find_ipc_dll", lambda folder="", override="": override
    )
    monkeypatch.setattr("src.utils.emulator.mumu_backend.NemuIpc", _FakeIpc)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuCapture", _FakeCap)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuInput", _FakeInp)

    E.create_backend("mumu", handle_spec=100, instance_index=1, ipc_dll_override=dll)

    assert _FakeIpc.instances[-1].root == "D:\\Apps\\MuMuPlayer"


def test_ui_warn_when_ipc_unavailable(monkeypatch):
    """C2: IPC 不可用时给用户一次可见提示（否则最小化黑屏但无从排查）。"""
    from src.utils.emulator.mumu_backend import MumuBackend

    E.clear_backends()
    warns = []

    class _L:
        def ui_warn(self, msg):
            warns.append(msg)

        def warning(self, *a, **k):
            pass

    monkeypatch.setattr("src.utils.emulator.mumu_backend.logger", _L())
    monkeypatch.setattr(MumuBackend, "_ipc_warned", False, raising=False)
    monkeypatch.setattr(
        "src.utils.emulator.mumu_backend.detect_mumu_folder",
        lambda configured="": "E:\\MuMuPlayer",
    )
    monkeypatch.setattr("src.utils.emulator.mumu_backend.build_handle", lambda *a, **k: _H())
    monkeypatch.setattr("src.utils.emulator.mumu_backend.find_ipc_dll", lambda *a, **k: None)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuCapture", _FakeCap)
    monkeypatch.setattr("src.utils.emulator.mumu_backend.MumuInput", _FakeInp)

    E.create_backend("mumu", handle_spec=100, instance_index=1)

    assert any("NemuIPC" in m for m in warns)