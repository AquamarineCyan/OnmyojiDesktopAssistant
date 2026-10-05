"""决策 A：enable_mumu 开关（默认关）。关闭后完全退回旧版（仅桌面版）行为。"""
from src.utils import window as wm
from src.utils.config import config


def _patch_win32(monkeypatch):
    monkeypatch.setattr(wm.win32gui, "GetWindowText", lambda hwnd: "t")
    monkeypatch.setattr(wm.win32gui, "GetWindowRect", lambda hwnd: (0, 0, 100, 100))
    monkeypatch.setattr(wm.win32gui, "GetClientRect", lambda hwnd: (0, 0, 100, 100))
    monkeypatch.setattr(wm.win32gui, "ClientToScreen", lambda hwnd, p: (0, 0))


def test_gamewindow_probe_disabled_when_switch_off(monkeypatch):
    _patch_win32(monkeypatch)
    called = []
    monkeypatch.setattr(
        "src.utils.emulator.mumu_handle.build_handle",
        lambda *a, **k: called.append(1) or None,
    )
    monkeypatch.setattr(
        "src.utils.emulator.mumu_handle.detect_mumu_folder", lambda *a, **k: "E:\\MuMuPlayer"
    )
    monkeypatch.setattr(config.user.interaction_mode.backend, "enable_mumu", False)

    w = wm.GameWindow(100, family="mumu", instance_index=0)

    assert w.family == "pc"
    assert called == []  # 开关关闭时不做任何句柄树探测


def test_discover_passes_enable_flag(monkeypatch):
    import src.utils.client_discovery as cd

    seen = {}
    monkeypatch.setattr(config.user.interaction_mode.backend, "enable_mumu", False)
    monkeypatch.setattr(
        cd,
        "discover_process_clients",
        lambda folder="", enable_emulator=True: seen.update(enable_emulator=enable_emulator) or [],
    )
    monkeypatch.setattr(cd, "build_client_items", lambda clients, fallback_titles=None: [])

    wm.window_manager.discover()

    assert seen["enable_emulator"] is False
