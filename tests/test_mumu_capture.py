"""Task 4: 截图链 + 归一化 + 黑屏门限（monkeypatch 假通道）。"""
import numpy as np

from src.utils.emulator import mumu_capture as mc
from src.utils.emulator.mumu_handle import MumuHandle


def _handle(shot=111, cw=700, ch=400):
    return MumuHandle(root_hwnd=100, root_title="t", shot_hwnd=shot,
                      control_hwnds=[100, shot], scale_rate=1.0,
                      client_w=cw, client_h=ch)


def test_normalize_to_scales():
    img = np.zeros((200, 400, 3), np.uint8)
    out = mc.normalize_to(img, 700, 400)
    assert out.shape[:2] == (400, 700)
    assert mc.normalize_to(img, 0, 0) is img
    assert mc.normalize_to(img, 400, 200) is img


def test_is_black_threshold():
    assert mc._is_black(np.zeros((10, 10, 3), np.uint8))
    assert not mc._is_black(np.full((10, 10, 3), 128, np.uint8))


def test_capture_prefers_printwindow(monkeypatch):
    h = _handle()
    cap = mc.MumuCapture(h, ipc=None)
    frame = np.full((400, 700, 3), 60, np.uint8)
    monkeypatch.setattr(cap, "_via_printwindow", lambda: frame.copy())
    monkeypatch.setattr(cap, "_via_ipc", lambda: (_ for _ in ()).throw(AssertionError("ipc should not run")))
    monkeypatch.setattr(cap, "_via_bitblt", lambda: (_ for _ in ()).throw(AssertionError("bitblt should not run")))
    out = cap.capture()
    assert out is not None and out.shape[:2] == (400, 700)


def test_capture_black_falls_through(monkeypatch):
    h = _handle()
    cap = mc.MumuCapture(h, ipc=None)
    monkeypatch.setattr(cap, "_via_printwindow", lambda: None)  # 黑/失败
    frame = np.full((400, 700, 3), 90, np.uint8)
    monkeypatch.setattr(cap, "_via_bitblt", lambda: frame.copy())
    out = cap.capture()
    assert out is not None


def test_capture_ipc_channel(monkeypatch):
    h = _handle()
    cap = mc.MumuCapture(h, ipc=object())
    monkeypatch.setattr(cap, "_via_printwindow", lambda: None)
    frame = np.full((400, 700, 3), 111, np.uint8)
    monkeypatch.setattr(cap, "_via_ipc", lambda: frame.copy())
    out = cap.capture()
    assert out is not None