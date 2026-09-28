"""模拟器窗口尺寸规范化：复用桌面版「强制缩放」确认流程（弹窗 + 不再提醒）。"""
import pytest

import src.utils.window as W
from src.utils.coordinate import STANDARD_CLIENT_HEIGHT, STANDARD_CLIENT_WIDTH
from src.utils.message import MessageBoxPayload
from src.utils.emulator import mumu_handle as MH
from src.utils.window import GameWindow, GameWindowManager


class _FakeWindow(GameWindow):
    def __init__(self, hwnd=300, family="mumu"):
        self.handle = hwnd
        self.family = family
        self.title = f"t{hwnd}"
        self.instance_index = 0
        self.shot_hwnd = hwnd
        self.control_hwnds = [hwnd, hwnd]
        self.scale_rate = 1.0
        self.window_rect = (0, 0, 200, 200)
        self.window_left = 10
        self.window_top = 10
        self.content_width = 856
        self.content_height = 482

    def display(self):
        pass


class _SignalRecorder:
    def __init__(self, bucket):
        self.bucket = bucket

    def emit(self, *args):
        self.bucket.append(args)


class _FakeMain:
    def __init__(self, bucket):
        self.message_box_requested = _SignalRecorder(bucket)
        self.window_status_changed = _SignalRecorder(bucket)


class _FakeSignalManager:
    """替换 window.signal_manager，记录信号发射（不依赖 Qt）。"""

    def __init__(self, bucket):
        self.main = _FakeMain(bucket)


@pytest.fixture
def manager():
    return GameWindowManager()


def test_need_force_zoom_for_mumu(manager):
    """模拟器按显示区尺寸判断，基准是 1136x640。"""
    w = _FakeWindow()
    manager.current = w
    assert manager._need_force_zoom() is True

    w.content_width, w.content_height = STANDARD_CLIENT_WIDTH, STANDARD_CLIENT_HEIGHT
    assert manager._need_force_zoom() is False


def test_need_force_zoom_tolerates_one_pixel(manager):
    """差 1~2 px 视为达标，避免每次检测都动窗口。"""
    w = _FakeWindow()
    w.content_width, w.content_height = STANDARD_CLIENT_WIDTH - 1, STANDARD_CLIENT_HEIGHT + 1
    manager.current = w
    assert manager._need_force_zoom() is False


def test_mumu_force_zoom_fits_display(manager, monkeypatch):
    """模拟器强制缩放 = 把显示区规范化到 1136x640，并重建窗口对象。"""
    calls = []
    monkeypatch.setattr(MH, "is_window", lambda h: True)
    monkeypatch.setattr(MH, "fit_display_size", lambda *a, **k: calls.append(a) or (1136, 640))
    rebuilt = []
    monkeypatch.setattr(W, "GameWindow", lambda *a, **k: rebuilt.append(a) or _FakeWindow())

    manager.current = _FakeWindow()
    assert manager.force_zoom() is True

    assert calls[0][2] == STANDARD_CLIENT_WIDTH
    assert calls[0][3] == STANDARD_CLIENT_HEIGHT
    assert rebuilt, "尺寸变化后未重建窗口对象"


def test_mumu_force_zoom_skips_invalid_window(manager, monkeypatch):
    monkeypatch.setattr(MH, "is_window", lambda h: False)
    monkeypatch.setattr(
        MH, "fit_display_size", lambda *a, **k: (_ for _ in ()).throw(AssertionError("不应调用"))
    )
    assert manager.force_zoom() is False


def test_mumu_update_asks_user_before_resize(manager, monkeypatch):
    """尺寸不匹配时走桌面版同款弹窗，不静默改窗口。"""
    emitted = []
    monkeypatch.setattr(W, "signal_manager", _FakeSignalManager(emitted))
    monkeypatch.setattr(W.config.user, "remember_force_zoom_choice", False)
    monkeypatch.setattr(
        MH, "fit_display_size", lambda *a, **k: (_ for _ in ()).throw(AssertionError("未确认不应缩放"))
    )

    manager._update(_FakeWindow())

    assert any(
        isinstance(args[0], MessageBoxPayload)
        and args[0].action == MessageBoxPayload.Action.FORCE_ZOOM
        for args in emitted
    ), "未弹出强制缩放确认框"


def test_mumu_update_auto_resize_when_remembered(manager, monkeypatch):
    """用户此前勾选「不再提醒 + 确定」时，检测到尺寸不符直接缩放。"""
    emitted = []
    monkeypatch.setattr(W, "signal_manager", _FakeSignalManager(emitted))
    monkeypatch.setattr(W.config.user, "remember_force_zoom_choice", True)
    monkeypatch.setattr(W.config.user, "force_zoom_accepted", True)
    monkeypatch.setattr(MH, "is_window", lambda h: True)
    calls = []
    monkeypatch.setattr(MH, "fit_display_size", lambda *a, **k: calls.append(a) or (1136, 640))
    monkeypatch.setattr(W, "GameWindow", lambda *a, **k: _FakeWindow())

    manager._update(_FakeWindow())

    assert calls, "已记住选择时未自动缩放"
    assert not emitted


def test_mumu_update_noop_when_size_ok(manager, monkeypatch):
    """尺寸达标时不动窗口、不弹窗。"""
    emitted = []
    monkeypatch.setattr(W, "signal_manager", _FakeSignalManager(emitted))
    monkeypatch.setattr(
        MH, "fit_display_size", lambda *a, **k: (_ for _ in ()).throw(AssertionError("不应缩放"))
    )

    w = _FakeWindow()
    w.content_width, w.content_height = STANDARD_CLIENT_WIDTH, STANDARD_CLIENT_HEIGHT
    manager._update(w)

    assert not emitted


def test_fit_display_size_restores_minimized_window(monkeypatch):
    """最小化时先恢复并置于前台，再执行尺寸迭代（修复前直接跳过，导致假成功）。"""
    events = []

    class _Gui:
        def __init__(self):
            self.size = (1000, 500)

        def IsIconic(self, hwnd):
            return True

        def ShowWindow(self, hwnd, cmd):
            events.append(("show", cmd))

        def SetForegroundWindow(self, hwnd):
            events.append(("fg", hwnd))

        def GetClientRect(self, hwnd):
            return (0, 0, *self.size)

        def GetWindowRect(self, hwnd):
            return (0, 0, 1200, 800)

        def MoveWindow(self, hwnd, x, y, w, h, repaint):
            events.append(("move", w, h))
            self.size = (1136, 640)

    monkeypatch.setattr(MH, "_gui", _Gui())
    monkeypatch.setattr(MH.time, "sleep", lambda s: None)

    assert MH.fit_display_size(1, 2, 1136, 640) == (1136, 640)
    assert events[0] == ("show", MH.SW_RESTORE)
    assert events[1] == ("fg", 1)
    assert events[2][0] == "move"


def test_mumu_force_zoom_reports_failure_when_not_converged(manager, monkeypatch):
    """显示区收敛不到基准时必须返回失败（修复前无条件报成功）。"""
    monkeypatch.setattr(MH, "is_window", lambda h: True)
    monkeypatch.setattr(MH, "fit_display_size", lambda *a, **k: (856, 482))
    monkeypatch.setattr(W, "GameWindow", lambda *a, **k: _FakeWindow())

    manager.current = _FakeWindow()
    assert manager.force_zoom() is False
