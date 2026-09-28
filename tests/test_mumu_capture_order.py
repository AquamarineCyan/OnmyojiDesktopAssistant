"""MuMu 截图通道优先级：IPC 优先（权威帧），PrintWindow/BitBlt 兜底。"""
import numpy as np

from src.utils.emulator.mumu_capture import MumuCapture


class _Handle:
    shot_hwnd = 0
    client_w = 4
    client_h = 4


def _frame():
    return np.full((4, 4, 3), 80, np.uint8)


def test_capture_prefers_ipc(monkeypatch):
    """IPC 是模拟器权威帧，必须优先于 PrintWindow（后者可能拿到陈旧 backing store）。"""
    cap = MumuCapture(_Handle(), ipc=object())
    monkeypatch.setattr(cap, "_via_ipc", lambda: _frame())

    def _boom():
        raise AssertionError("IPC 可用时不应走 PrintWindow")

    monkeypatch.setattr(cap, "_via_printwindow", _boom)
    monkeypatch.setattr(cap, "_via_bitblt", _boom)

    assert cap.capture() is not None
    assert cap.last_source == "ipc"


def test_capture_falls_back_to_printwindow(monkeypatch):
    """IPC 失败（无 IPC / 黑屏）时回退 PrintWindow。"""
    cap = MumuCapture(_Handle(), ipc=None)
    monkeypatch.setattr(cap, "_via_printwindow", lambda: _frame())
    monkeypatch.setattr(cap, "_via_bitblt", lambda: None)

    assert cap.capture() is not None
    assert cap.last_source == "printwindow"


def test_capture_falls_back_to_bitblt(monkeypatch):
    """IPC 与 PrintWindow 都失败时回退 BitBlt。"""
    cap = MumuCapture(_Handle(), ipc=object())
    monkeypatch.setattr(cap, "_via_ipc", lambda: None)
    monkeypatch.setattr(cap, "_via_printwindow", lambda: None)
    monkeypatch.setattr(cap, "_via_bitblt", lambda: _frame())

    assert cap.capture() is not None
    assert cap.last_source == "bitblt"
