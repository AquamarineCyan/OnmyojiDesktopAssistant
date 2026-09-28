"""进程优先的客户端发现：桌面版在前、模拟器在后，各自按序编实例号。

标题仅在零发现时做兜底，不参与匹配。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

import win32con
import win32gui

ClientKind = Literal["pc", "emulator"]

EMULATOR_PROC_NAMES = ("mumunxdevice.exe", "mumuplayer.exe", "nemuplayer.exe")
PC_GAME_PROC_NAMES = ("onmyoji.exe",)
PC_LAUNCHER_PROC_NAMES = ("launch.exe",)
PC_PATH_HINT = "onmyoji"


@dataclass
class ClientInfo:
    kind: ClientKind
    pid: int
    hwnd: int
    title: str
    index: Optional[int] = None
    detail: str = ""


def _gui_enum_windows() -> list[int]:
    out: list[int] = []
    try:
        win32gui.EnumWindows(lambda h, p: p.append(h) or True, out)
    except Exception:
        pass
    return out


def _pid_of_window(hwnd: int) -> int:
    import win32process

    try:
        return win32process.GetWindowThreadProcessId(int(hwnd))[1]
    except Exception:
        return 0


def windows_of_pid(pid: int, visible_only: bool = True) -> list[int]:
    found: list[int] = []
    for hwnd in _gui_enum_windows():
        try:
            if _pid_of_window(hwnd) != pid:
                continue
            if not win32gui.IsWindow(hwnd):
                continue
            if visible_only and not win32gui.IsWindowVisible(hwnd):
                continue
            found.append(hwnd)
        except Exception:
            continue
    return found


def _iter_procs():
    import psutil

    try:
        for proc in psutil.process_iter(["pid", "name", "exe"]):
            try:
                info = proc.info or {}
            except Exception:
                continue
            yield info
    except Exception:
        return


def _exe_lower(info: dict) -> str:
    try:
        return str(info.get("exe") or "").lower()
    except Exception:
        return ""


def _proc_name(info: dict) -> str:
    try:
        return str(info.get("name") or "").lower()
    except Exception:
        return ""


def _rank_windows(pid: int) -> list[tuple[int, str]]:
    rows: list[tuple[tuple[bool, bool, int], int, str]] = []
    for hwnd in windows_of_pid(pid):
        try:
            title = win32gui.GetWindowText(hwnd) or ""
        except Exception:
            title = ""
        try:
            top_level = win32gui.GetWindow(hwnd, win32con.GW_OWNER) == 0
        except Exception:
            top_level = False
        try:
            rect = win32gui.GetClientRect(hwnd)
            area = max(0, rect[2] - rect[0]) * max(0, rect[3] - rect[1])
        except Exception:
            area = 0
        rows.append(((bool(title), top_level, area), hwnd, title))
    rows.sort(key=lambda row: row[0], reverse=True)
    return [(hwnd, title) for _key, hwnd, title in rows]


def query_cli_windows(mumu_folder: str = "") -> list[tuple[int, int, str]]:
    """mumu-cli 权威实例列表 [(hwnd, index, name)]，失败返回 []。"""
    try:
        from .emulator.mumu_handle import detect_mumu_folder, discover_clients
    except Exception:
        return []
    try:
        folder = mumu_folder or detect_mumu_folder("")
    except Exception:
        return []
    if not folder:
        return []
    try:
        return [(int(hwnd), int(idx), str(name or "")) for idx, hwnd, name in discover_clients(folder)]
    except Exception:
        return []


def build_handle_ok(hwnd: int):
    """句柄树校验通过返回 MumuHandle，否则抛异常。"""
    from .emulator.mumu_handle import build_handle

    return build_handle(int(hwnd), wait_tries=1)


def client_label(client: ClientInfo) -> str:
    n = (client.index or 1) if client.index is not None else 1
    # index 存储为 1-based；旧 cli 行号为 0-based 时在发现阶段已 +1
    name = (client.detail or client.title or f"PID {client.pid}").strip() or f"PID {client.pid}"
    if client.kind == "emulator":
        return f"模拟器 · 实例{n} · {name}"
    return f"桌面版 · 实例{n} · {name}"


def build_client_items(
    clients: list[ClientInfo], fallback_titles: list[str] | None = None
) -> list[tuple[str, "ClientInfo | None"]]:
    items: list[tuple[str, "ClientInfo | None"]] = []
    seen: set[str] = set()
    for c in clients or []:
        label = client_label(c)
        if label in seen:
            continue
        seen.add(label)
        items.append((label, c))
    if items:
        return items
    for t in fallback_titles or []:
        t = (t or "").strip()
        if not t or t in seen:
            continue
        seen.add(t)
        items.append((t, None))
    return items


def discover_process_clients(mumu_folder: str = "", enable_emulator: bool = True) -> list[ClientInfo]:
    """进程枚举：桌面版在前、模拟器在后，各自按 pid/实例序编 1-based 实例号。

    enable_emulator=False（决策 A 开关关闭）时完全不查 cli、不枚举模拟器进程，
    仅保留桌面版发现路径。
    """
    pcs: list[ClientInfo] = []
    emus: list[ClientInfo] = []
    used: set[int] = set()

    if enable_emulator:
        for hwnd, iid, name in query_cli_windows(mumu_folder or ""):
            try:
                import win32gui as _g

                if not _g.IsWindow(int(hwnd)):
                    continue
                title = _g.GetWindowText(int(hwnd)) or name or ""
            except Exception:
                title = name or ""
            try:
                pid = _pid_of_window(int(hwnd))
            except Exception:
                pid = 0
            if int(hwnd) in used:
                continue
            used.add(int(hwnd))
            emus.append(
                ClientInfo(kind="emulator", pid=pid, hwnd=int(hwnd), title=title,
                           index=int(iid) + 1, detail=name or title)
            )

    try:
        procs = list(_iter_procs())
    except Exception:
        procs = []

    for info in procs:
        name = _proc_name(info)
        try:
            pid = int(info.get("pid") or 0)
        except (ValueError, TypeError):
            continue
        if not name or not pid or name not in EMULATOR_PROC_NAMES:
            continue
        if not enable_emulator:
            continue
        for hwnd, _t in _rank_windows(pid):
            if hwnd in used:
                continue
            try:
                handle = build_handle_ok(hwnd)
            except Exception:
                continue
            try:
                root = int(handle.root_hwnd)
            except Exception:
                continue
            if root in used:
                continue
            used.add(root)
            try:
                title = win32gui.GetWindowText(root) or getattr(handle, "root_title", "") or ""
            except Exception:
                title = getattr(handle, "root_title", "") or ""
            emus.append(ClientInfo(kind="emulator", pid=pid, hwnd=root, title=title,
                                   index=None, detail=title))

    pc_procs = [i for i in procs if PC_PATH_HINT in _exe_lower(i)]
    game_procs = [i for i in pc_procs if _proc_name(i) in PC_GAME_PROC_NAMES]
    launcher_procs = [i for i in pc_procs if _proc_name(i) in PC_LAUNCHER_PROC_NAMES]
    for info in game_procs or launcher_procs:
        try:
            pid = int(info.get("pid") or 0)
        except (ValueError, TypeError):
            continue
        ranked = _rank_windows(pid) if pid else []
        if not ranked:
            continue
        hwnd, title = ranked[0]
        if hwnd in used:
            continue
        used.add(hwnd)
        pcs.append(ClientInfo(kind="pc", pid=pid, hwnd=int(hwnd), title=title or "",
                              index=None, detail=title or ""))

    pcs.sort(key=lambda c: c.pid)
    # 模拟器：cli 给的 index 优先（已是 1-based），兜底按 pid
    emus.sort(key=lambda c: (c.index if c.index is not None else 10**9, c.pid))
    for i, c in enumerate(pcs, start=1):
        c.index = i
    next_idx = 1
    for c in emus:
        if c.index is None:
            c.index = next_idx
        next_idx = max(next_idx, c.index + 1)
    # cli 可能给出非连续序号（如实例被删），压缩为连续 1..N 展示
    emus_sorted = sorted(emus, key=lambda c: (c.index, c.pid))
    for i, c in enumerate(emus_sorted, start=1):
        c.index = i

    return pcs + emus_sorted
