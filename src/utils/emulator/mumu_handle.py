"""MuMu 句柄层：安装目录探测 + 窗口枚举 + 句柄树判定（适配 Qt/nemuwin 树）。
移植参考：OnmyojiAuto OAT/tools/emulator/mumu_handle.py（本机窗口树实测不同：根/子类名为
Qt5156QWindowIcon，游戏表面为 class=nemuwin title=nemudisplay）。"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Optional

import psutil
import win32api
import win32gui
from win32con import DESKTOPHORZRES, SW_RESTORE
from win32print import GetDeviceCaps

# 供测试整体替换的 win32 门面（默认即真实 win32gui）
_gui = win32gui

MUMU_PROCESS_NAMES = ("MuMuNxDevice.exe", "MuMuPlayer.exe", "NemuPlayer.exe")
# 进程 exe 反推安装根时关注的主进程（不含 MuMuNxSVC.exe —— VBox 服务，目录无价值）
ROOT_PROBE_PROCESS_NAMES = (
    "mumunxmain.exe",
    "mumunxdevice.exe",
    "mumunxservice.exe",
    "mumuremoteservice.exe",
    "mumuremotebackend.exe",
)
MUMU_TITLES = ("MuMu模拟器12", "MuMu安卓设备", "MuMuPlayer")
IGNORED_TITLE_SUBSTRINGS = ("MessageWnd",)
# 同属 MuMu 进程但必须排除的辅助窗口（本机实测清单，避免误判为设备窗口）
EXCLUDED_WINDOW_CLASSES = {
    "IME",
    "Default IME",
    "MSCTFIME UI",
    "Sogou_TSF_UI",
    "SoPY_Hint",
    "SoPY_UI",
    "SoPY_Status",
    "NVOpenGLPbuffer",
    "Chrome_WidgetWin_0",
    "Chrome_SystemMessageWindow",
    "Base_PowerMessageWindow",
    "Static",
    "Qt5156QWindowToolSaveBits",
}
EXCLUDED_WINDOW_TITLES = {"HintWnd", "MSCTFIME UI", "Default IME", "Sogou_TSF_UI", "__wglDummyWindowFodder"}
# 旧版 MuMu 树的渲染子窗口类名（保留兼容）
SHOT_CHILD_NAMES = ("MuMuPlayer", "MuMuNxDevice", "NemuPlayer")
# 新版 MuMu 树的游戏显示表面
NEMUWIN_CLASS = "nemuwin"
NEMUWIN_TITLE = "nemudisplay"
COMMON_MUMU_ROOTS = (
    r"E:\MuMuPlayer",
    r"D:\MuMuPlayer",
    r"C:\Program Files\Netease\MuMuPlayer-12.0",
    r"C:\Program Files\MuMuPlayer",
)


@dataclass
class MumuHandle:
    root_hwnd: int
    root_title: str
    shot_hwnd: int
    control_hwnds: list[int]
    scale_rate: float
    client_w: int
    client_h: int


def is_window(hwnd: int) -> bool:
    try:
        return bool(_gui.IsWindow(int(hwnd)))
    except Exception:
        return False


def window_scale_rate() -> float:
    try:
        hdc = _gui.GetDC(0)
        try:
            return round(GetDeviceCaps(hdc, DESKTOPHORZRES) / win32api.GetSystemMetrics(0), 2)
        finally:
            try:
                _gui.ReleaseDC(0, hdc)
            except Exception:
                pass
    except Exception:
        return 1.0


def _valid_root(root: str) -> bool:
    r = (root or "").strip()
    if not r:
        return False
    return os.path.isfile(os.path.join(r, "nx_main", "mumu-cli.exe"))


def is_valid_mumu_folder(root: str) -> bool:
    """校验安装目录：<root>\\nx_main\\mumu-cli.exe 存在。"""
    return _valid_root(root)


def mumu_root_from_dll(dll_path: str) -> str:
    """由 external_renderer_ipc.dll 路径反推安装根（nx_main/… 或 nx_device/… 的父目录）。

    仅配 ipc_dll_override、未填安装目录时使用；反推不到返回 ""。
    """
    try:
        p = os.path.abspath(dll_path or "")
    except Exception:
        return ""
    while True:
        parent = os.path.dirname(p)
        if parent == p:
            return ""
        if os.path.basename(parent) in ("nx_main", "nx_device"):
            return os.path.dirname(parent)
        p = parent


def _running_mumu_exes() -> list[str]:
    out: list[str] = []
    for proc in psutil.process_iter(["name", "exe"]):
        try:
            name = (proc.info["name"] or "").lower()
            exe = proc.info["exe"] or ""
        except Exception:
            continue
        if name in ROOT_PROBE_PROCESS_NAMES and exe:
            out.append(exe)
    return out


def _exe_to_root(exe: str) -> str:
    """从 MuMu 进程 exe 路径向上找含 nx_main\\mumu-cli.exe 的祖先目录（上限 4 级）。"""
    d = os.path.dirname(exe or "")
    for _ in range(4):
        if _valid_root(d):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return ""


try:
    import winreg as _winreg
except ImportError:  # 非 Windows 环境（仅理论；本项目仅 Windows）
    _winreg = None


def _uninstall_locations() -> list[str]:
    """查询卸载注册表 InstallLocation（DisplayName 含 'mumu'）；任何异常返回 []。

    注意：winreg 的 API 是模块级函数（QueryInfoKey/EnumKey/QueryValueEx），
    PyHKEY 只有数据与上下文管理，没有同名方法——必须按模块级调用。
    """
    if _winreg is None:
        return []
    paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    out: list[str] = []
    for path in paths:
        try:
            with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, path) as k:
                for i in range(_winreg.QueryInfoKey(k)[0]):
                    try:
                        with _winreg.OpenKey(k, _winreg.EnumKey(k, i)) as sk:
                            name, _ = _winreg.QueryValueEx(sk, "DisplayName")
                            loc, _ = _winreg.QueryValueEx(sk, "InstallLocation")
                    except OSError:
                        continue
                    if name and "mumu" in str(name).lower() and loc:
                        out.append(str(loc))
        except OSError:
            continue
    return out


_detect_cache: Optional[str] = None


def reset_detect_cache() -> None:
    """清空安装目录探测缓存（测试隔离 / 配置变更时手动失效）。"""
    global _detect_cache
    _detect_cache = None


def _probe() -> str:
    """执行 2-4 级降级探测：进程 exe 反推 → 卸载注册表 → 常见路径 → ""（未找到）。"""
    for exe in _running_mumu_exes():
        r = _exe_to_root(exe)
        if r:
            return r
    try:  # 注册表异常不允许逃逸（_probe 运行在主循环 tick 路径上）
        for r in _uninstall_locations():
            if _valid_root(r):
                return r
    except Exception:
        pass
    for r in COMMON_MUMU_ROOTS:
        if _valid_root(r):
            return r
    return ""


def detect_mumu_folder(configured: str = "") -> str:
    """五级降级探测：显式配置 → 进程 exe 反推 → 卸载注册表 → 常见路径 → ""（未找到）。

    进程内缓存仅作用于空配置（spec §4.1.0）：显式配置每次实时判定且不读写缓存；
    空配置首次探测（含 "" 结果）写入缓存，后续调用直接命中。"""
    global _detect_cache
    root = (configured or "").strip().strip('"').strip()
    if root:
        if _valid_root(root):
            return root
        # 显式配置无效：仍走 2-4 级降级，但不缓存（避免残留配置污染空配置缓存）
        return _probe()
    if _detect_cache is not None:
        return _detect_cache
    _detect_cache = _probe()
    return _detect_cache


def _exe_of(pid: int) -> str:
    try:
        return psutil.Process(pid).name() or ""
    except Exception:
        return ""


def _is_excluded_window(hwnd: int) -> bool:
    try:
        cls = _gui.GetClassName(hwnd) or ""
        title = _gui.GetWindowText(hwnd) or ""
    except Exception:
        return True
    if cls in EXCLUDED_WINDOW_CLASSES or title in EXCLUDED_WINDOW_TITLES:
        return True
    if any(ign.lower() in title.lower() for ign in IGNORED_TITLE_SUBSTRINGS):
        return True
    return False


def enum_mumu_by_process() -> list[int]:
    """按所属进程枚举（与标题无关）；排除辅助窗口。"""
    import win32process

    found: list[int] = []

    def _cb(hwnd: int, _) -> bool:
        try:
            if _is_excluded_window(hwnd):
                return True
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]
            if _exe_of(pid).lower() in {n.lower() for n in MUMU_PROCESS_NAMES}:
                found.append(hwnd)
        except Exception:
            pass
        return True

    try:
        _gui.EnumWindows(_cb, None)
    except Exception:
        return []
    return sorted(set(found))


def _mumu_cli_json(mumu_folder: str) -> list[dict]:
    cli = os.path.join((mumu_folder or "").strip(), "nx_main", "mumu-cli.exe")
    if not os.path.isfile(cli):
        return []
    try:
        # 不用 capture_output：管道会迫使 CPython 为 stdout/stderr 各起一个读取线程，
        # 空闲期每次查询都会让它们在堆栈里闪现/消失。stdout 重定向到临时文件、
        # stderr 丢弃，保留 10s 超时保护且不产生任何读取线程。
        with tempfile.TemporaryFile() as f:
            subprocess.run(
                [cli, "info", "--vmindex", "all"],
                stdout=f,
                stderr=subprocess.DEVNULL,
                timeout=10,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            f.seek(0)
            data = json.loads(f.read().decode("utf-8", "replace"))
    except Exception:
        return []
    out: list[dict] = []
    if isinstance(data, dict):
        for key, val in data.items():
            v = dict(val or {})
            if v.get("is_android_started") or v.get("is_process_started"):
                try:
                    v["index"] = int(key)
                except (ValueError, TypeError):
                    continue
                out.append(v)
    return out


# 每 tick（~200ms）的 discover/build_handle 都会查 cli；mumu-cli 子进程启动 + 10s 超时风险
# 让这一个 daemon 线程（同时跑悬赏封印）卡死。TTL=3s 缓存把每 tick 2-3 次 cli 查询压成
# 最多每 3s 一次子进程，避免空闲期每秒起一次进程。
MUMU_CLI_TTL = 3.0  # 秒

_cli_cache: dict[str, tuple] = {}
"""folder -> (func_ref, monotonic_ts, rows)；func_ref 变化（测试 monkeypatch/热替换）即失效。"""


def reset_mumu_cli_cache() -> None:
    """清空 cli 查询缓存（测试隔离 / 配置变更时手动失效）。"""
    _cli_cache.clear()


def _mumu_cli_json_cached(mumu_folder: str) -> list[dict]:
    """_mumu_cli_json 的 TTL 包装：缓存条目同时记录底层函数对象引用，
    函数被替换（monkeypatch）时自动重算，保证测试/热替换语义不变。"""
    now = time.monotonic()
    key = (mumu_folder or "").strip()
    hit = _cli_cache.get(key)
    if hit is not None:
        func_ref, ts, rows = hit
        if func_ref is _mumu_cli_json and now - ts < MUMU_CLI_TTL:
            return rows
    rows = _mumu_cli_json(mumu_folder)
    _cli_cache[key] = (_mumu_cli_json, now, rows)
    return rows


def query_cli_windows(mumu_folder: str) -> list[tuple[int, int, str]]:
    """→ [(root_hwnd, instance_index, name)]；标题无关的最权威映射。"""
    rows: list[tuple[int, int, str]] = []
    for v in _mumu_cli_json_cached(mumu_folder):
        try:
            hwnd = int(str(v.get("main_wnd") or ""), 16)
        except (ValueError, TypeError):
            continue
        if hwnd and is_window(hwnd):
            rows.append((hwnd, int(v["index"]), str(v.get("name", ""))))
    return rows


def _render_wnd_from_cli(root_hwnd: int, mumu_folder: str) -> Optional[int]:
    for v in _mumu_cli_json_cached(mumu_folder):
        try:
            if int(str(v.get("main_wnd") or ""), 16) == int(root_hwnd):
                return int(str(v.get("render_wnd") or ""), 16)
        except (ValueError, TypeError):
            continue
    return None


def direct_children(hwnd: int) -> list[int]:
    out: list[int] = []
    _gui.EnumChildWindows(hwnd, lambda h, p: p.append(h) or True, out)
    return [h for h in out if _gui.GetParent(h) == hwnd]


def _find_nemuwin(root: int) -> Optional[int]:
    """BFS 深度 ≤3 找 class=nemuwin title=nemudisplay 的显示表面。"""
    seen: set[int] = {root}
    frontier = [root]
    for _ in range(3):
        nxt: list[int] = []
        for h in frontier:
            for c in direct_children(h):
                if c in seen:
                    continue
                seen.add(c)
                try:
                    if _gui.GetClassName(c) == NEMUWIN_CLASS and _gui.GetWindowText(c) == NEMUWIN_TITLE:
                        return c
                except Exception:
                    pass
                nxt.append(c)
        frontier = nxt
    return None


def _client_size(hwnd: int) -> tuple[int, int]:
    try:
        cr = _gui.GetClientRect(hwnd)
        return cr[2] - cr[0], cr[3] - cr[1]
    except Exception:
        return 1280, 720


def fit_display_size(
    root_hwnd: int,
    shot_hwnd: int,
    target_w: int,
    target_h: int,
    tolerance: int = 2,
    tries: int = 8,
) -> tuple[int, int]:
    """把模拟器显示子窗口的客户区规范化到目标尺寸（缩放 root 窗口，迭代逼近）。

    模拟器显示区小于某个尺寸时不会等比缩小、而是裁剪画面，导致截图/坐标与屏幕不符；
    统一到基准尺寸（1136x640）后，坐标换算系数为 1，识别与点击都按 PC 基准走。

    Returns:
        (w, h): 调整后的显示区客户区尺寸
    """
    if _gui.IsIconic(int(root_hwnd)):
        # 最小化时 MoveWindow 对显示区不生效：先恢复并置于前台，再走尺寸迭代；
        # 恢复失败/仍在最小化时下面的收敛失败会由调用方给出明确错误提示
        try:
            _gui.ShowWindow(int(root_hwnd), SW_RESTORE)
            _gui.SetForegroundWindow(int(root_hwnd))
        except Exception:
            pass
        time.sleep(0.3)

    for _ in range(max(1, int(tries))):
        cw, ch = _client_size(shot_hwnd)
        dw, dh = int(target_w) - cw, int(target_h) - ch
        if abs(dw) <= tolerance and abs(dh) <= tolerance:
            break
        try:
            wx, wy, wr, wb = _gui.GetWindowRect(int(root_hwnd))
            _gui.MoveWindow(int(root_hwnd), wx, wy, (wr - wx) + dw, (wb - wy) + dh, True)
        except Exception:
            break
        time.sleep(0.3)
    return _client_size(shot_hwnd)


def build_handle(spec, mumu_folder: str = "", wait_tries: int = 10) -> MumuHandle:
    """解析 spec → 校验 MuMu 树 → MumuHandle；非 MuMu 树抛 ValueError。

    判定优先级：cli 的 render_wnd 下找 nemuwin → 根树里找 nemuwin →
    首子类名 ∈ SHOT_CHILD_NAMES（legacy）→ 抛异常。
    """
    root, title = _resolve_root(spec)
    kids = _wait_children(root, tries=max(1, int(wait_tries)))
    render = _render_wnd_from_cli(root, mumu_folder)
    shot = _find_nemuwin(render or root)
    if shot is None and kids:
        try:
            if _gui.GetClassName(kids[0]) in SHOT_CHILD_NAMES:
                shot = kids[0]
        except Exception:
            pass
    if shot is None:
        raise ValueError(f"not a MuMu window tree (root={root})")
    cw, ch = _client_size(shot)
    return MumuHandle(
        root_hwnd=root,
        root_title=title,
        shot_hwnd=shot,
        control_hwnds=[root, shot],
        scale_rate=window_scale_rate(),
        client_w=cw,
        client_h=ch,
    )


def _suffix_id(title: str, fallback: int) -> int:
    m = re.search(r"-(\d+)\s*$", title or "")
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return fallback


def discover_clients(mumu_folder: str = "") -> list[tuple[int, int, str]]:
    """→ [(instance_index, root_hwnd, title)]，按实例号升序（实例1、实例2…）。

    优先 cli 权威映射；cli 不可用时进程扫描 + build_handle 校验兜底。
    """
    rows = query_cli_windows(mumu_folder)
    if rows:
        return sorted([(i, h, n) for h, i, n in rows], key=lambda t: (t[0], t[1]))
    out: list[tuple[int, int, str]] = []
    for hwnd in enum_mumu_by_process():
        try:
            h = build_handle(hwnd)
        except Exception:
            continue
        out.append((_suffix_id(h.root_title, len(out)), h.root_hwnd, h.root_title))
    return sorted(out, key=lambda t: (t[0], t[1]))


def _resolve_root(spec) -> tuple[int, str]:
    if isinstance(spec, int) or (isinstance(spec, str) and spec.lstrip("-").isdigit()):
        hwnd = int(spec)
        if not is_window(hwnd):
            raise ValueError(f"handle {hwnd} is not a valid window")
        return hwnd, _gui.GetWindowText(hwnd)
    hwnd = _gui.FindWindow(None, spec)
    if not hwnd:
        raise ValueError(f"window title not found: {spec}")
    return hwnd, spec


def _wait_children(root: int, tries: int = 10) -> list[int]:
    kids = direct_children(root)
    for _ in range(tries - 1):
        if kids:
            return kids
        time.sleep(1.0)
        kids = direct_children(root)
    return kids


def resolve_auto(instance_index: int = 0, mumu_folder: str = "") -> tuple[int, int]:
    """auto 解析 → (HWND, instance id)；cli 权威 → 进程扫描兜底。"""
    idx = int(instance_index)
    rows = query_cli_windows(mumu_folder)
    if rows:
        ordered = sorted(rows, key=lambda t: t[1])
        if idx >= len(ordered):
            raise ValueError(f"instance_index {idx} out of range ({len(ordered)} running instances)")
        hwnd, iid, _ = ordered[idx]
        return hwnd, iid
    handles = []
    for hwnd in enum_mumu_by_process():
        try:
            handles.append(build_handle(hwnd))
        except Exception:
            continue
    if not handles:
        raise ValueError("auto: no MuMu window found")
    handles.sort(key=lambda h: h.root_hwnd)
    if idx >= len(handles):
        raise ValueError(f"instance_index {idx} out of range ({len(handles)} emulator windows)")
    h = handles[idx]
    return h.root_hwnd, _suffix_id(h.root_title, idx)
