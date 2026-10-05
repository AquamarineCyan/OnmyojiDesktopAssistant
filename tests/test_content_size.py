"""C3 回归：mumu 窗口的内容（帧）尺寸取 shot 客户区，而不是 root 客户区。

root（Qt 播放器窗口）与 nemudisplay（渲染表面）客户区高度实测恒定差 ~40px；
模板缩放若用 root 会系统性拉伸模板。
"""
from src.utils import window as wm
from src.utils.config import config
from src.utils.emulator.mumu_handle import MumuHandle


def test_gamewindow_mumu_content_size_uses_shot(monkeypatch):
    # 模拟器支持默认关闭；本用例验证 mumu 分支，需显式开启开关
    monkeypatch.setattr(config.user.interaction_mode.backend, "enable_mumu", True)
    h = MumuHandle(root_hwnd=100, root_title="t", shot_hwnd=111,
                   control_hwnds=[100, 111], scale_rate=1.0, client_w=1084, client_h=610)
    monkeypatch.setattr("src.utils.emulator.mumu_handle.build_handle", lambda *a, **k: h)
    monkeypatch.setattr(
        "src.utils.emulator.mumu_handle.detect_mumu_folder", lambda *a, **k: "E:\\MuMuPlayer"
    )
    monkeypatch.setattr(wm.win32gui, "GetWindowText", lambda hwnd: "t")
    monkeypatch.setattr(wm.win32gui, "GetWindowRect", lambda hwnd: (0, 0, 100, 100))
    monkeypatch.setattr(
        wm.win32gui,
        "GetClientRect",
        lambda hwnd: (0, 0, 1084, 650) if int(hwnd) == 100 else (0, 0, 1084, 610),
    )
    monkeypatch.setattr(wm.win32gui, "ClientToScreen", lambda hwnd, p: (0, 0))

    w = wm.GameWindow(100, family="mumu", instance_index=0)

    assert w.family == "mumu"
    assert w.client_height == 650  # root 仍是 root
    assert getattr(w, "content_height", None) == 610  # 内容尺寸 = shot
    assert getattr(w, "content_width", None) == 1084
