"""模拟器窗口尺寸规范化：复用桌面版「强制缩放」确认流程（弹窗 + 不再提醒）。"""

import pytest

import src.utils.window as W
from src.utils.coordinate import STANDARD_CLIENT_HEIGHT, STANDARD_CLIENT_WIDTH
from src.utils.emulator import mumu_handle as MH
from src.utils.message import MessageBoxPayload
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
def manager(monkeypatch):
    """隔离真实 config.yaml 中已持久化的自定义尺寸（运行应用做缩放会真实写入）。"""
    monkeypatch.setattr(W.config.user, "custom_window_width", 0)
    monkeypatch.setattr(W.config.user, "custom_window_height", 0)
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
    monkeypatch.setattr(W, "is_window", lambda h: True)
    monkeypatch.setattr(W, "fit_display_size", lambda *a, **k: calls.append(a) or (1136, 640))
    rebuilt = []
    monkeypatch.setattr(W, "GameWindow", lambda *a, **k: rebuilt.append(a) or _FakeWindow())

    manager.current = _FakeWindow()
    assert manager.resize_window() is True

    assert calls[0][2] == STANDARD_CLIENT_WIDTH
    assert calls[0][3] == STANDARD_CLIENT_HEIGHT
    assert rebuilt, "尺寸变化后未重建窗口对象"


def test_mumu_force_zoom_skips_invalid_window(manager, monkeypatch):
    monkeypatch.setattr(W, "is_window", lambda h: False)
    monkeypatch.setattr(MH, "fit_display_size", lambda *a, **k: (_ for _ in ()).throw(AssertionError("不应调用")))
    assert manager.resize_window() is False


def test_mumu_update_asks_user_before_resize(manager, monkeypatch):
    """尺寸不匹配时走桌面版同款弹窗，不静默改窗口。"""
    emitted = []
    monkeypatch.setattr(W, "signal_manager", _FakeSignalManager(emitted))
    monkeypatch.setattr(W.config.user, "remember_force_zoom_choice", False)
    monkeypatch.setattr(MH, "fit_display_size", lambda *a, **k: (_ for _ in ()).throw(AssertionError("未确认不应缩放")))

    manager._update(_FakeWindow())

    assert any(
        isinstance(args[0], MessageBoxPayload) and args[0].action == MessageBoxPayload.Action.FORCE_ZOOM
        for args in emitted
    ), "未弹出强制缩放确认框"


def test_mumu_update_auto_resize_when_remembered(manager, monkeypatch):
    """用户此前勾选「不再提醒 + 确定」时，检测到尺寸不符直接缩放。"""
    emitted = []
    monkeypatch.setattr(W, "signal_manager", _FakeSignalManager(emitted))
    monkeypatch.setattr(W.config.user, "remember_force_zoom_choice", True)
    monkeypatch.setattr(W.config.user, "force_zoom_accepted", True)
    monkeypatch.setattr(W, "is_window", lambda h: True)
    calls = []
    monkeypatch.setattr(W, "fit_display_size", lambda *a, **k: calls.append(a) or (1136, 640))
    monkeypatch.setattr(W, "GameWindow", lambda *a, **k: _FakeWindow())

    manager._update(_FakeWindow())

    assert calls, "已记住选择时未自动缩放"
    assert not emitted


def test_mumu_update_noop_when_size_ok(manager, monkeypatch):
    """尺寸达标时不动窗口、不弹窗。"""
    emitted = []
    monkeypatch.setattr(W, "signal_manager", _FakeSignalManager(emitted))
    monkeypatch.setattr(MH, "fit_display_size", lambda *a, **k: (_ for _ in ()).throw(AssertionError("不应缩放")))

    w = _FakeWindow()
    w.content_width, w.content_height = STANDARD_CLIENT_WIDTH, STANDARD_CLIENT_HEIGHT
    manager._update(w)

    assert not emitted


def test_custom_size_survives_apply(manager, monkeypatch):
    """自定义缩放后点「应用」不应回弹基准：检测基准跟随自定义尺寸（回归：原实现始终以 1136x640 为基准）。"""
    emitted = []
    monkeypatch.setattr(W, "signal_manager", _FakeSignalManager(emitted))
    monkeypatch.setattr(W.config.user, "remember_force_zoom_choice", True)
    monkeypatch.setattr(W.config.user, "force_zoom_accepted", True)
    monkeypatch.setattr(W, "is_window", lambda h: True)
    calls = []
    monkeypatch.setattr(W, "fit_display_size", lambda *a, **k: calls.append(a) or (1200, 700))
    monkeypatch.setattr(W, "GameWindow", lambda *a, **k: _FakeWindow())
    monkeypatch.setattr(W.config, "update", lambda k, v: None)  # 测试不写真实 config.yaml

    manager.current = _FakeWindow()
    assert manager.resize_window(1200, 700) is True
    calls.clear()

    w = _FakeWindow()
    w.content_width, w.content_height = 1200, 700
    manager._update(w)  # 「应用」按钮触发 force_update → _update

    assert not calls, "自定义尺寸被判为不匹配，又被强制缩放回默认"
    assert not emitted


def test_force_zoom_normalizes_to_custom_target(manager, monkeypatch):
    """偏离自定义尺寸时，无参 resize_window 规范化到自定义目标而非默认 1136x640。"""
    monkeypatch.setattr(W, "is_window", lambda h: True)
    calls = []
    monkeypatch.setattr(W, "fit_display_size", lambda *a, **k: calls.append(a) or (1200, 700))
    monkeypatch.setattr(W, "GameWindow", lambda *a, **k: _FakeWindow())
    monkeypatch.setattr(W.config, "update", lambda k, v: None)  # 测试不写真实 config.yaml

    manager.current = _FakeWindow()
    assert manager.resize_window(1200, 700) is True

    w = _FakeWindow()
    w.content_width, w.content_height = STANDARD_CLIENT_WIDTH, STANDARD_CLIENT_HEIGHT
    manager.current = w
    assert manager._need_force_zoom() is True
    assert manager.resize_window() is True
    assert calls[-1][2] == 1200
    assert calls[-1][3] == 700


def test_failed_resize_breaks_prompt_loop(manager, monkeypatch):
    """缩放失败不记录自定义目标、不解除提示拦截，避免「确认→失败→下一秒再弹」循环。"""
    monkeypatch.setattr(W, "is_window", lambda h: True)
    # fit 不收敛（模拟 MuMu 锁画面比例时目标不可达）
    monkeypatch.setattr(W, "fit_display_size", lambda *a, **k: (856, 482))
    monkeypatch.setattr(W, "GameWindow", lambda *a, **k: _FakeWindow())
    emitted = []
    monkeypatch.setattr(W, "signal_manager", _FakeSignalManager(emitted))

    manager.current = _FakeWindow()
    manager._force_zoom_flag = True  # 模拟弹窗已提示、用户已确认
    assert manager.resize_window(1200, 700) is False

    # 失败不记录自定义目标，规范化目标仍是基准
    assert manager.zoom_target == (STANDARD_CLIENT_WIDTH, STANDARD_CLIENT_HEIGHT)
    # 失败保持拦截：检测不弹窗
    manager.current = _FakeWindow()
    assert manager._check_force_zoom() is False
    assert not emitted


def test_check_force_zoom_suspended_while_resizing(manager, monkeypatch):
    """缩放进行中（窗口尺寸为中间态）时，检测线程挂起强制缩放判断，不再弹窗。"""
    emitted = []
    monkeypatch.setattr(W, "signal_manager", _FakeSignalManager(emitted))
    monkeypatch.setattr(W.config.user, "remember_force_zoom_choice", False)

    manager.current = _FakeWindow()  # 856x482，不匹配
    manager._resizing = True
    assert manager._check_force_zoom() is False
    assert not emitted

    manager._resizing = False
    assert manager._check_force_zoom() is True  # 缩放结束后恢复检测


def test_custom_size_persisted_and_loaded(manager, monkeypatch):
    """显式缩放成功后写入配置；新管理器初始化时读取为规范化目标（重启后记住缩放偏好）。"""
    monkeypatch.setattr(W, "is_window", lambda h: True)
    monkeypatch.setattr(W, "fit_display_size", lambda *a, **k: (1200, 700))
    monkeypatch.setattr(W, "GameWindow", lambda *a, **k: _FakeWindow())
    saved = {}
    monkeypatch.setattr(W.config, "update", lambda k, v: saved.update({k: v}))

    manager.current = _FakeWindow()
    assert manager.resize_window(1200, 700) is True
    assert saved == {"custom_window_width": 1200, "custom_window_height": 700}

    # 模拟重启：配置已持久化，新管理器初始化时读取
    monkeypatch.setattr(W.config.user, "custom_window_width", 1200)
    monkeypatch.setattr(W.config.user, "custom_window_height", 700)
    fresh = GameWindowManager()
    assert fresh.zoom_target == (1200, 700)


def test_custom_size_not_persisted_on_failure(manager, monkeypatch):
    """缩放失败不写配置，避免不可达的目标被持久化。"""
    monkeypatch.setattr(W, "is_window", lambda h: True)
    monkeypatch.setattr(W, "fit_display_size", lambda *a, **k: (856, 482))  # 不收敛
    monkeypatch.setattr(W, "GameWindow", lambda *a, **k: _FakeWindow())
    saved = {}
    monkeypatch.setattr(W.config, "update", lambda k, v: saved.update({k: v}))

    manager.current = _FakeWindow()
    assert manager.resize_window(1200, 700) is False
    assert saved == {}


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
    monkeypatch.setattr(W, "is_window", lambda h: True)
    monkeypatch.setattr(W, "fit_display_size", lambda *a, **k: (856, 482))
    monkeypatch.setattr(W, "GameWindow", lambda *a, **k: _FakeWindow())

    manager.current = _FakeWindow()
    assert manager.resize_window() is False
