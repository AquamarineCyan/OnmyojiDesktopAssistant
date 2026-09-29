"""Task 5: 输入路由——IPC 优先，消息兜底（fake ipc / monkeypatch win32api）。"""
import src.utils.emulator.mumu_input as mi
from src.utils.emulator.mumu_handle import MumuHandle


class _FakeIpc:
    def __init__(self):
        self.events = []
        self.width = 1280
        self.height = 720

    def get_resolution(self):
        pass

    def down(self, x, y, contact=0):
        self.events.append(("down", int(x), int(y), contact))

    def up(self, contact=0):
        self.events.append(("up", contact))


def _handle():
    return MumuHandle(root_hwnd=1, root_title="t", shot_hwnd=3,
                      control_hwnds=[1, 3], scale_rate=1.0, client_w=700, client_h=400)


def test_ipc_click_uses_native_scale():
    ipc = _FakeIpc()
    inp = mi.MumuInput(_handle(), ipc)
    inp.click(350, 200)
    kinds = [e[0] for e in ipc.events]
    assert kinds == ["down", "down", "up"]
    x, y = ipc.events[0][1], ipc.events[0][2]
    assert x > 300 and y > 100  # 700→1280 换算方向正确


def test_ipc_swipe_builds_trace():
    ipc = _FakeIpc()
    inp = mi.MumuInput(_handle(), ipc)
    inp.swipe(10, 10, 20, 20, duration=0.01)
    downs = [e for e in ipc.events if e[0] == "down"]
    assert len(downs) >= 2
    assert ipc.events[-1][0] == "up"


def test_message_fallback_without_ipc(monkeypatch):
    sent = []
    # 逐字源以 `from win32api import PostMessage, SendMessage` 绑定模块级名 → 直接替换模块级名
    monkeypatch.setattr(mi, "SendMessage", lambda hwnd, msg, w, l: sent.append((hwnd, msg, l)) or 0)
    monkeypatch.setattr(mi, "PostMessage", lambda hwnd, msg, w, l: sent.append((hwnd, msg, l)) or 0)
    inp = mi.MumuInput(_handle(), None)
    inp.click(350, 200)
    targets = {s[0] for s in sent}
    assert targets == {3}  # 深度目标 nemudisplay
    msgs = {s[1] for s in sent}
    assert mi.win32con.WM_LBUTTONDOWN in msgs and mi.win32con.WM_LBUTTONUP in msgs


def test_to_ipc_scale_identity():
    h = _handle()
    inp = mi.MumuInput(h, _FakeIpc())
    assert inp._to_ipc(350, 200) == (640, 360)  # 客户区→IPC 原生分辨率


def test_to_ipc_uses_live_client_size(monkeypatch):
    """窗口运行中改大小后按实时客户区换算（与截图口径一致），不用 build_handle 快照。"""
    inp = mi.MumuInput(_handle(), _FakeIpc())  # 快照 700x400，IPC 1280x720
    monkeypatch.setattr(mi.win32gui, "GetClientRect", lambda hwnd: (0, 0, 1400, 800))
    assert inp._to_ipc(700, 400) == (640, 360)  # 1400x800 恰好一半

    monkeypatch.setattr(mi.win32gui, "GetClientRect", lambda hwnd: (0, 0, 700, 400))
    assert inp._to_ipc(350, 200) == (640, 360)  # 与快照一致时保持原比例


def test_press_back_posts_xbutton1(monkeypatch):
    """无 IPC 时退回窗口消息版侧键（部分环境 MuMu 不处理，故仅作兜底）。"""
    sent = []
    monkeypatch.setattr(mi, "PostMessage", lambda hwnd, msg, w, l: sent.append((hwnd, msg, w, l)) or 0)
    monkeypatch.setattr(mi, "_sleep", lambda s: None)

    mi.MumuInput(_handle(), None).press_back()

    assert [s[1] for s in sent] == [mi.WM_XBUTTONDOWN, mi.WM_XBUTTONUP]
    assert {s[0] for s in sent} == {3}  # 深度目标 nemudisplay
    assert all(((s[2] >> 16) & 0xFFFF) == mi.XBUTTON1 for s in sent)


def test_press_back_uses_ipc_key_back(monkeypatch):
    """有 IPC 时注入 KEY_BACK（与物理侧键同一个安卓按键事件）。"""
    events = []

    class _FakeIpc:
        width = 1280
        height = 720

        def get_resolution(self):
            pass

        def key_down(self, key):
            events.append(("down", key))

        def key_up(self, key):
            events.append(("up", key))

        def down(self, *a):
            raise AssertionError("不应走触摸")

        def up(self, *a):
            raise AssertionError("不应走触摸")

    monkeypatch.setattr(mi, "_sleep", lambda s: None)
    mi.MumuInput(_handle(), _FakeIpc()).press_back()

    assert events == [("down", mi.KEY_BACK), ("up", mi.KEY_BACK)]