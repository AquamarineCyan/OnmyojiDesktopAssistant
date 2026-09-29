"""Task 9: family=mumu 时后台输入走 MumuBackend；pc/前台分支不受影响。"""
import pytest

import src.utils.adapter as ad
import src.utils.emulator as E


@pytest.fixture(autouse=True)
def _family_routing_only(monkeypatch):
    # 开关已移除：仅按窗口 family 路由，无需配置
    pass


class _Backend:
    def __init__(self):
        self.calls = []

    def click(self, x, y):
        self.calls.append(("click", x, y))

    def swipe(self, x1, y1, x2, y2, duration=0.5):
        self.calls.append(("swipe", x1, y1, x2, y2))

    def press_back(self):
        self.calls.append(("back",))


class _NoWait:
    """替换 event_xuanshang，避免测试里 .wait() 阻塞。"""

    def wait(self, *a, **k):
        pass


class _Win:
    family = "mumu"
    handle = 100
    instance_index = 1


class _PcWin:
    family = "pc"
    handle = 200
    instance_index = 0


def test_mumu_click_routes(monkeypatch):
    backend = _Backend()
    monkeypatch.setattr(E, "get_backend", lambda *a, **k: backend)
    monkeypatch.setattr(ad.window_manager, "current", _Win())
    monkeypatch.setattr(ad.config.user.interaction_mode, "mode", "后台")
    monkeypatch.setattr(ad.Mouse, "_back_click_point", _P(10, 10), raising=False)
    ad.Mouse.click(_P(50, 60))
    assert backend.calls[-1] == ("click", 50, 60)


def test_mumu_drag_routes_to_swipe(monkeypatch):
    backend = _Backend()
    monkeypatch.setattr(E, "get_backend", lambda *a, **k: backend)
    monkeypatch.setattr(ad.window_manager, "current", _Win())
    monkeypatch.setattr(ad.config.user.interaction_mode, "mode", "后台")
    monkeypatch.setattr(ad.Mouse, "_back_click_point", _P(10, 10), raising=False)
    ad.Mouse.drag(5, 6)
    assert any(c[0] == "swipe" for c in backend.calls)


def test_mumu_move_keeps_anchor_for_drag(monkeypatch):
    """Imp #4: mumu move 必须更新 _back_click_point，否则 move 后 drag 从陈旧点起滑。"""
    backend = _Backend()
    monkeypatch.setattr(E, "get_backend", lambda *a, **k: backend)
    monkeypatch.setattr(ad.window_manager, "current", _Win())
    monkeypatch.setattr(ad.config.user.interaction_mode, "mode", "后台")
    monkeypatch.setattr(ad.Mouse, "_back_click_point", _P(0, 0), raising=False)
    ad.Mouse.move(_P(30, 40))  # mumu：move 本身不下发（IPC 无悬停），但必须更新锚点
    ad.Mouse.drag(10, 20)
    assert backend.calls[-1] == ("swipe", 30, 40, 40, 60)  # 起点是 move 后的位置


def test_mumu_esc_routes_to_side_button(monkeypatch):
    """模拟器下 KeyBoard.esc() 走鼠标侧键（XBUTTON1），不再依赖键盘。"""
    backend = _Backend()
    monkeypatch.setattr(E, "get_backend", lambda *a, **k: backend)
    monkeypatch.setattr(ad.window_manager, "current", _Win())
    monkeypatch.setattr(ad.config.user.interaction_mode, "mode", "后台")
    monkeypatch.setattr(ad, "event_xuanshang", _NoWait())
    ad.KeyBoard.esc()
    assert backend.calls[-1] == ("back",)


def test_pc_esc_still_sends_key(monkeypatch):
    """桌面版 KeyBoard.esc() 保持发 ESC 键，模拟器改动不影响它。"""
    pressed = []
    monkeypatch.setattr(ad.window_manager, "current", _PcWin())
    monkeypatch.setattr(ad.config.user.interaction_mode, "mode", "前台")
    monkeypatch.setattr(ad, "event_xuanshang", _NoWait())
    monkeypatch.setattr(ad.KeyBoard, "_front_operation", classmethod(lambda cls, key: pressed.append(key)))
    ad.KeyBoard.esc()
    assert pressed == ["esc"]


class _WinScaled:
    """mumu 窗口：实际客户区 1393x784（基准 1136x640 的 1.226 倍）"""

    family = "mumu"
    handle = 300
    instance_index = 0
    client_width = 1393
    client_height = 784
    content_width = 1393
    content_height = 784


def test_mumu_click_scales_reference_to_actual(monkeypatch):
    """业务侧传的是基准空间坐标，注入前必须换算到实际客户区。"""
    backend = _Backend()
    monkeypatch.setattr(E, "get_backend", lambda *a, **k: backend)
    monkeypatch.setattr(ad.window_manager, "current", _WinScaled())
    monkeypatch.setattr(ad.config.user.interaction_mode, "mode", "后台")
    monkeypatch.setattr(ad.Mouse, "_back_click_point", _P(10, 10), raising=False)

    ad.Mouse.click(_P(500, 300))

    fx, fy = 1393 / 1136, 784 / 640
    assert backend.calls[-1] == ("click", int(500 * fx), int(300 * fy))


def test_mumu_position_returns_reference(monkeypatch):
    """鼠标真实位置（实际客户区）读出来要换算回基准空间。"""
    import pyautogui

    from src.utils.point import Point

    class _Cur:
        pass

    monkeypatch.setattr(ad.window_manager, "current", _WinScaled())
    monkeypatch.setattr(ad.Point, "from_screen", classmethod(lambda cls, x, y: Point(x, y)))
    monkeypatch.setattr(pyautogui, "position", lambda: (613, 367))

    point = ad.Mouse.position()

    fx, fy = 1393 / 1136, 784 / 640
    assert point.client_x == int(613 / fx)
    assert point.client_y == int(367 / fy)


class _P:
    def __init__(self, x, y):
        self.client_x = x
        self.client_y = y