"""Task 7: 识别路由——进程优先、标题降级、实例排序、mumu 跳过强制检查。"""
import pytest

import src.utils.window as W
from src.utils.config import config
from src.utils.window import GameWindow, GameWindowManager


@pytest.fixture()
def _win32(monkeypatch):
    """GameWindow.__init__ 依赖的真实 win32 调用 → 假数据。"""
    import src.utils.window as W
    monkeypatch.setattr(W.win32gui, "GetWindowText", lambda h: f"title{h}")
    monkeypatch.setattr(W.win32gui, "GetWindowRect", lambda h: (0, 0, 200, 200))
    monkeypatch.setattr(W.win32gui, "GetClientRect", lambda h: (0, 0, 180, 180))
    monkeypatch.setattr(W.win32gui, "ClientToScreen", lambda h, p: (0, 0))


@pytest.fixture()
def _enable(monkeypatch):
    monkeypatch.setattr(config.user.interaction_mode.backend, "mumu_folder", "E:\\MuMuPlayer")
    monkeypatch.setattr(config.user.interaction_mode.backend, "enable_mumu", True)


def _h(hwnd):
    from src.utils.emulator.mumu_handle import MumuHandle
    return MumuHandle(root_hwnd=int(hwnd), root_title=f"t{hwnd}", shot_hwnd=int(hwnd),
                      control_hwnds=[int(hwnd), int(hwnd)], scale_rate=1.0,
                      client_w=180, client_h=180)


class _EmitRecorder:
    """信号记录器：挂在假 signal_manager 上，记录 emit 参数。"""

    def __init__(self, out):
        self.out = out

    def emit(self, *a):
        self.out.append(a)


class _FakeMain:
    def __init__(self, out):
        self.message_box_requested = _EmitRecorder(out)
        self.window_status_changed = _EmitRecorder(out)


class _FakeSignalManager:
    """替换 window.signal_manager，记录信号发射（不依赖 Qt）。"""

    def __init__(self, out):
        self.main = _FakeMain(out)


def test_game_window_family_probe(monkeypatch, _win32, _enable):
    mh = pytest.importorskip("src.utils.emulator.mumu_handle")
    monkeypatch.setattr(mh, "detect_mumu_folder", lambda cfg: "E:\\MuMuPlayer")

    def raise_for(spec, **k):
        raise ValueError("pc")

    monkeypatch.setattr(mh, "build_handle", raise_for)
    assert GameWindow(999).family == "pc"

    monkeypatch.setattr(mh, "build_handle", lambda spec, **k: _h(spec))
    g = GameWindow(999)
    assert g.family == "mumu"
    assert g.shot_hwnd == 999 and g.control_hwnds == [999, 999]


def test_family_explicit_pc_skips_probe(monkeypatch, _win32):
    """显式 family=pc 时不触发 build_handle 探测。"""
    mh = pytest.importorskip("src.utils.emulator.mumu_handle")
    called = []
    monkeypatch.setattr(mh, "detect_mumu_folder", lambda cfg: "E:\\MuMuPlayer")
    monkeypatch.setattr(mh, "build_handle",
                        lambda spec, **k: called.append(spec) or _h(spec))
    assert GameWindow(999, family="pc").family == "pc"
    assert not called


def test_discover_desktop_first_then_mumu(monkeypatch, _win32, _enable):
    import types

    import src.utils.client_discovery as CD
    import src.utils.window as W

    pc1 = types.SimpleNamespace(kind="pc", pid=10, hwnd=333, title="title333", index=1, detail="title333")
    pc2 = types.SimpleNamespace(kind="pc", pid=11, hwnd=334, title="title334", index=2, detail="title334")
    mu1 = types.SimpleNamespace(kind="emulator", pid=20, hwnd=111, title="t111", index=1, detail="MuMu安卓设备")
    mu2 = types.SimpleNamespace(kind="emulator", pid=21, hwnd=222, title="t222", index=2, detail="MuMu安卓设备-1")
    monkeypatch.setattr(CD, "discover_process_clients",
                        lambda folder="", enable_emulator=True: [pc1, pc2, mu1, mu2])
    monkeypatch.setattr(CD, "build_client_items",
                        lambda clients, fallback_titles=None: [(f"x{c.hwnd}", c) for c in clients])

    class _GW:
        def __init__(self, handle, family=None, instance_index=0):
            self.handle = int(handle)
            self.title = f"title{handle}"
            self.family = family or "pc"
            self.instance_index = int(instance_index)

        @property
        def label(self):
            n = self.instance_index + 1
            return f"{'模拟器' if self.family == 'mumu' else '桌面版'} · 实例{n} · {self.title}"

    monkeypatch.setattr(W, "GameWindow", _GW)

    wins = GameWindowManager().discover()
    assert [w.handle for w in wins] == [333, 334, 111, 222]  # 桌面版在前、模拟器在后
    assert wins[0].family == "pc" and wins[0].instance_index == 0
    assert wins[2].family == "mumu" and wins[2].instance_index == 0
    assert wins[0].label == "桌面版 · 实例1 · title333"
    assert wins[2].label == "模拟器 · 实例1 · title111"


def test_discover_title_fallback_only_when_empty(monkeypatch, _win32):
    import src.utils.client_discovery as CD
    import src.utils.window as W

    monkeypatch.setattr(CD, "discover_process_clients", lambda folder="", enable_emulator=True: [])
    monkeypatch.setattr(CD, "build_client_items",
                        lambda clients, fallback_titles=None: [("阴阳师-网易游戏", None)])
    monkeypatch.setattr(W, "get_all_target_window", lambda titles: [555])
    wins = GameWindowManager().discover()
    assert [w.handle for w in wins] == [555]
    assert wins[0].family == "pc"


def test_mumu_update_skips_background_check(monkeypatch):
    emitted = []
    monkeypatch.setattr(W, "signal_manager", _FakeSignalManager(emitted))
    mgr = GameWindowManager()
    mgr.current = _FakeWindow(100, "mumu")
    mgr._update(mgr.current)  # mumu：不得弹"请前置游戏窗口"
    assert not emitted


def test_pc_update_still_checks_background(monkeypatch):
    mgr = GameWindowManager()
    emitted = []
    monkeypatch.setattr(W, "signal_manager", _FakeSignalManager(emitted))
    w = _FakeWindow(200, "pc")
    w.window_rect = (-100, 0, 100, 100)  # 窗口在屏外 → 桌面版仍走原检查
    mgr.current = w
    assert mgr._check_background() is True
    assert emitted


class _FakeWindow(GameWindow):
    def __init__(self, hwnd, family):
        self.handle = hwnd
        self.family = family
        self.title = f"t{hwnd}"
        self.instance_index = 0
        self.shot_hwnd = hwnd
        self.control_hwnds = [hwnd, hwnd]
        self.scale_rate = 1.0
        self.window_rect = (0, 0, 200, 200)

    def display(self):
        pass