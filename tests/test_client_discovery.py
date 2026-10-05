"""进程优先发现：桌面版在前、模拟器在后，各自按 pid 编实例号，标题仅空时兜底。"""

import types

import pytest


def _make_win(monkeypatch, pid_map, rect_map=None, text_map=None, owner_map=None):
    import src.utils.client_discovery as cd

    hwnds = []
    for pid, lst in pid_map.items():
        hwnds.extend(lst)

    monkeypatch.setattr(cd, "_gui_enum_windows", lambda: list(hwnds))

    def _pid(hwnd):
        for pid, lst in pid_map.items():
            if hwnd in lst:
                return pid
        return 0

    monkeypatch.setattr(cd, "_pid_of_window", _pid)
    monkeypatch.setattr(cd.win32gui, "IsWindow", lambda h: True)
    monkeypatch.setattr(cd.win32gui, "IsWindowVisible", lambda h: True)
    monkeypatch.setattr(
        cd.win32gui, "GetWindowText", lambda h: (text_map or {}).get(h, f"t{h}")
    )

    def _rect(h):
        return (rect_map or {}).get(h, (0, 0, 180, 180))

    monkeypatch.setattr(cd.win32gui, "GetClientRect", _rect)
    monkeypatch.setattr(
        cd.win32gui, "GetWindow", lambda h, flag: (owner_map or {}).get(h, 0)
    )


def test_desktop_first_emulator_after_with_instance_numbers(monkeypatch):
    cd = pytest.importorskip("src.utils.client_discovery")

    procs = [
        {"pid": 30, "name": "MuMuNxDevice.exe", "exe": r"C:\MuMu\nx_main\MuMuNxDevice.exe"},
        {"pid": 31, "name": "MuMuNxDevice.exe", "exe": r"C:\MuMu\nx_main\MuMuNxDevice.exe"},
        {"pid": 10, "name": "onmyoji.exe", "exe": r"D:\game\onmyoji.exe"},
        {"pid": 11, "name": "onmyoji.exe", "exe": r"D:\game\onmyoji.exe"},
    ]
    monkeypatch.setattr(cd, "_iter_procs", lambda: list(procs))
    monkeypatch.setattr(cd, "query_cli_windows", lambda folder: [])
    monkeypatch.setattr(
        cd, "build_handle_ok", lambda hwnd: types.SimpleNamespace(root_hwnd=hwnd, root_title=f"t{hwnd}")
    )
    _make_win(monkeypatch, {10: [101], 11: [102], 30: [301], 31: [302]})

    clients = cd.discover_process_clients()
    assert [(c.kind, c.pid) for c in clients] == [
        ("pc", 10),
        ("pc", 11),
        ("emulator", 30),
        ("emulator", 31),
    ]
    labels = [cd.client_label(c) for c in clients]
    assert labels[0].startswith("桌面版 - 实例1")
    assert labels[1].startswith("桌面版 - 实例2")
    assert labels[2].startswith("模拟器 - 实例1")
    assert labels[3].startswith("模拟器 - 实例2")


def test_title_fallback_only_when_empty(monkeypatch):
    cd = pytest.importorskip("src.utils.client_discovery")

    monkeypatch.setattr(cd, "_iter_procs", lambda: [])
    monkeypatch.setattr(cd, "query_cli_windows", lambda folder: [])
    _make_win(monkeypatch, {})

    assert cd.discover_process_clients() == []
    items = cd.build_client_items([], fallback_titles=["阴阳师-网易游戏"])
    assert items == [("阴阳师-网易游戏", None)]

    # 有发现项时不掺标题兜底
    fake = [types.SimpleNamespace(kind="pc", pid=10, hwnd=101, title="t101", index=1, detail="t101")]
    items = cd.build_client_items(fake, fallback_titles=["阴阳师-网易游戏"])
    assert len(items) == 1 and items[0][1] is fake[0]


def test_discover_skips_emulator_when_disabled(monkeypatch):
    """决策 A：enable_mumu=False 时不查 cli、不枚举模拟器（PC 行为与旧版一致）。"""
    cd = pytest.importorskip("src.utils.client_discovery")

    calls = []
    monkeypatch.setattr(
        cd, "query_cli_windows", lambda folder="": calls.append(folder) or [(123, 1, "MuMu")]
    )
    monkeypatch.setattr(cd, "_iter_procs", lambda: [])
    _make_win(monkeypatch, {})

    assert cd.discover_process_clients(enable_emulator=False) == []
    assert calls == []  # cli 完全未被查询
