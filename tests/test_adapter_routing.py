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


class _Win:
    family = "mumu"
    handle = 100
    instance_index = 1


def test_mumu_click_routes(monkeypatch):
    backend = _Backend()
    monkeypatch.setattr(E, "get_backend", lambda *a, **k: backend)
    monkeypatch.setattr(ad.window_manager, "current", _Win())
    monkeypatch.setattr(ad.config.user.interaction_mode, "mode", "后台")
    ad.Mouse._back_click_point = _P(10, 10)
    ad.Mouse.click(_P(50, 60))
    assert backend.calls[-1] == ("click", 50, 60)


def test_mumu_drag_routes_to_swipe(monkeypatch):
    backend = _Backend()
    monkeypatch.setattr(E, "get_backend", lambda *a, **k: backend)
    monkeypatch.setattr(ad.window_manager, "current", _Win())
    monkeypatch.setattr(ad.config.user.interaction_mode, "mode", "后台")
    ad.Mouse._back_click_point = _P(10, 10)
    ad.Mouse.drag(5, 6)
    assert any(c[0] == "swipe" for c in backend.calls)


def test_mumu_move_keeps_anchor_for_drag(monkeypatch):
    """Imp #4: mumu move 必须更新 _back_click_point，否则 move 后 drag 从陈旧点起滑。"""
    backend = _Backend()
    monkeypatch.setattr(E, "get_backend", lambda *a, **k: backend)
    monkeypatch.setattr(ad.window_manager, "current", _Win())
    monkeypatch.setattr(ad.config.user.interaction_mode, "mode", "后台")
    ad.Mouse._back_click_point = _P(0, 0)
    ad.Mouse.move(_P(30, 40))  # mumu：move 本身不下发（IPC 无悬停），但必须更新锚点
    ad.Mouse.drag(10, 20)
    assert backend.calls[-1] == ("swipe", 30, 40, 40, 60)  # 起点是 move 后的位置


class _P:
    def __init__(self, x, y):
        self.client_x = x
        self.client_y = y