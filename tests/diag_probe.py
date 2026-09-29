"""只读探测脚本：确认 MuMu 模拟器 / 阴阳师桌面客户端的真实窗口树、进程与实例分布。

用法（游戏/模拟器运行时执行）:
    python tests/diag_probe.py

输出:
    1. 所有 MuMu 相关进程（MuMuNxDevice.exe / MuMuPlayer.exe / NemuPlayer.exe）
    2. 标题含 MuMu/阴阳师 的顶层窗口 + 递归子窗口树（类名/标题/矩形/PID/进程名）
    3. 系统缩放率（DPI）
    4. mumu-cli 探测（常见安装目录，存在则打印 `info --vmindex all` 权威实例映射）

本脚本只做枚举与打印，不修改任何状态。
"""
from __future__ import annotations

import os
import subprocess
import sys

import win32gui
import win32process
from win32print import GetDeviceCaps
from win32con import DESKTOPHORZRES

import psutil

MUMU_PROC_NAMES = ("MuMuNxDevice.exe", "MuMuPlayer.exe", "NemuPlayer.exe")
MUMU_TITLE_KEYS = ("MuMu模拟器", "MuMuPlayer", "MuMu安卓设备", "NemuPlayer")
GAME_TITLE_KEYS = ("阴阳师", "陰陽師")
CLI_INSTALL_HINTS = (
    r"E:\MuMuPlayer", r"D:\MuMuPlayer", r"C:\Program Files\MuMuPlayer",
    r"C:\Program Files\Netease\MuMu Player 12",
)


def exe_of(pid: int) -> str:
    try:
        return psutil.Process(pid).name() or ""
    except Exception:
        return ""


def direct_children(hwnd: int) -> list[int]:
    out: list[int] = []
    win32gui.EnumChildWindows(hwnd, lambda h, p: p.append(h) or True, out)
    return [h for h in out if win32gui.GetParent(h) == hwnd]


def dump_tree(hwnd: int, indent: int = 2, depth: int = 0, max_depth: int = 3) -> None:
    if depth > max_depth:
        print(" " * indent + "... (depth limit)")
        return
    try:
        title = win32gui.GetWindowText(hwnd) or ""
        cls = win32gui.GetClassName(hwnd) or ""
        rect = win32gui.GetWindowRect(hwnd)
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    except Exception as e:
        print(" " * indent + f"<err {e}>")
        return
    print(f"{' ' * indent}hwnd={hwnd} class={cls!r} title={title!r} rect={rect} pid={pid} exe={exe_of(pid)}")
    if depth < max_depth:
        for child in direct_children(hwnd):
            dump_tree(child, indent + 2, depth + 1, max_depth)


def scale_rate() -> float:
    try:
        hdc = win32gui.GetDC(0)
        try:
            return round(GetDeviceCaps(hdc, DESKTOPHORZRES) / win32gui.GetSystemMetrics(0), 2)
        finally:
            win32gui.ReleaseDC(0, hdc)
    except Exception:
        return 1.0


def probe_cli() -> None:
    print("\n===== mumu-cli 探测 =====")
    for root in CLI_INSTALL_HINTS:
        cli = os.path.join(root, "nx_main", "mumu-cli.exe")
        if os.path.isfile(cli):
            print(f"找到 mumu-cli: {cli}")
            try:
                proc = subprocess.run(
                    [cli, "info", "--vmindex", "all"],
                    capture_output=True, timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                print("info --vmindex all 输出:")
                print((proc.stdout or b"").decode("utf-8", "replace"))
            except Exception as e:
                print(f"mumu-cli 执行失败: {e}")
            return
    print("常见目录未找到 mumu-cli，请在探测时手动确认 MuMu 安装目录")


def main() -> None:
    print(f"python: {sys.executable}")
    print(f"系统缩放率 scale_rate = {scale_rate()}")

    print("\n===== 相关进程 =====")
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if (proc.info["name"] or "").lower() in {n.lower() for n in MUMU_PROC_NAMES}:
                print(f"pid={proc.info['pid']} exe={proc.info['name']}")
        except Exception:
            pass

    print("\n===== 候选顶层窗口（进程匹配 或 标题含 MuMu/阴阳师）=====")
    found = []

    def _cb(hwnd: int, _) -> bool:
        try:
            title = win32gui.GetWindowText(hwnd) or ""
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]
            exe = exe_of(pid)
            if exe.lower() in {n.lower() for n in MUMU_PROC_NAMES}:
                found.append((hwnd, f"[进程] {exe}"))
            elif any(k in title for k in MUMU_TITLE_KEYS) or any(k in title for k in GAME_TITLE_KEYS):
                found.append((hwnd, f"[标题] {title}"))
        except Exception:
            pass
        return True

    win32gui.EnumWindows(_cb, None)
    if not found:
        print("未发现 MuMu 模拟器或阴阳师窗口 —— 若游戏已开启请确认标题/进程名，或稍后重试")
        return

    for hwnd, tag in sorted(found):
        title = win32gui.GetWindowText(hwnd)
        cls = win32gui.GetClassName(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
        print(f"\n>>> 顶层窗口 {tag}")
        print(f"    hwnd={hwnd} class={cls!r} title={title!r} rect={rect} pid={pid} exe={exe_of(pid)}")
        print("    子窗口树:")
        dump_tree(hwnd)

    probe_cli()


if __name__ == "__main__":
    main()