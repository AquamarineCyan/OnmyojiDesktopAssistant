"""CPU 采样与火焰图生成（py-spy 封装）

用法（必须使用项目虚拟环境的 Python 运行）:
    .venv\\Scripts\\python.exe tools\\profile_cpu.py                  # 自动定位 main.py 进程，采样 60s 并打开火焰图
    .venv\\Scripts\\python.exe tools\\profile_cpu.py -d 120 -r 200    # 采样 120s，200Hz
    .venv\\Scripts\\python.exe tools\\profile_cpu.py -t               # 火焰图按线程分组（配合多线程分析）
    .venv\\Scripts\\python.exe tools\\profile_cpu.py --top            # 仅实时 top 视图（不生成火焰图）
    .venv\\Scripts\\python.exe tools\\profile_cpu.py --pid 1234       # 指定进程 PID

说明:
- 目标程序（main.py）以管理员身份运行，py-spy 需要相同权限：采样失败时会自动提权重试（UAC）
- 火焰图输出到 profiles/cpu-<时间戳>.svg，采样结束后自动用默认浏览器打开
"""

from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
import time
from pathlib import Path
from shutil import which

import psutil

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "profiles"
DEFAULT_MATCH = "main.py"


def is_admin() -> bool:
    """当前进程是否管理员权限"""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def find_pyspy() -> str:
    """定位 py-spy 可执行文件（优先项目虚拟环境）"""
    for candidate in (REPO_ROOT / ".venv" / "Scripts" / "py-spy.exe", which("py-spy")):
        if candidate and Path(candidate).exists():
            return str(candidate)
    raise SystemExit("未找到 py-spy，请先执行 uv sync --group dev（或 pip install py-spy）")


def find_target(match: str, auto_elevate: bool = False) -> tuple[int, str]:
    """按命令行关键字定位目标进程，返回 (pid, 描述)

    - 优先只看 Python 进程（排除 shell/IDE 等包装进程），无命中再放宽为全部进程
    - venv 的 python.exe 是转发 stub，真正执行代码的是它命令行相同的子进程，
      因此命中多个时取进程链最深的一个（py-spy 只能识别真实解释器进程）
    """
    self_pid = os.getpid()
    denied = 0
    matches: list[tuple[psutil.Process, str]] = []
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.pid == self_pid:
            continue
        try:
            cmdline = " ".join(proc.cmdline() or [])
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except psutil.AccessDenied:
            denied += 1  # 以管理员运行的进程无法读取命令行
            continue
        if match.lower() in cmdline.lower():
            matches.append((proc, cmdline))
    if not matches:
        if denied and auto_elevate:
            print("无法读取目标进程命令行（目标可能以管理员运行），尝试提权后重试（UAC）...")
            relaunch_elevated()
        hint = "（存在无法读取命令行的进程，若目标以管理员运行，请以管理员身份运行本脚本）" if denied else ""
        raise SystemExit(f"未找到命令行包含“{match}”的进程{hint}；可用 --pid 指定")

    python_named = [(p, c) for p, c in matches if "python" in (p.info["name"] or "").lower()]
    candidates = python_named or matches
    by_pid = {p.pid: p for p, _ in candidates}

    def depth(proc: psutil.Process) -> int:
        """命令行相同的进程链深度（stub → 真实解释器）"""
        d, cur = 0, proc
        while d < 10:
            try:
                parent = by_pid.get(cur.ppid())
            except Exception:
                break
            if parent is None:
                break
            d += 1
            cur = parent
        return d

    target, cmdline = max(candidates, key=lambda item: depth(item[0]))
    for proc, _ in candidates:
        if proc.pid != target.pid:
            print(f"忽略同命令行的上层进程: PID {proc.pid}（{proc.name()}）")
    return target.pid, f"{target.name()} (PID {target.pid}) {cmdline}"


def relaunch_elevated() -> None:
    """以管理员身份重新启动本脚本（UAC 提权），原进程退出"""
    params = " ".join([f'"{Path(__file__).resolve()}"', *(f'"{a}"' for a in sys.argv[1:]), "--elevated"])
    ret = int(ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1))
    if ret <= 32:
        print("提权失败，请手动以管理员身份打开终端后重试")
        sys.exit(1)
    sys.exit(0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="py-spy 封装：进程 CPU 采样与火焰图生成")
    parser.add_argument("-p", "--pid", type=int, default=0, help="目标进程 PID（默认按 --match 自动查找）")
    parser.add_argument("--match", default=DEFAULT_MATCH, help=f"自动查找时匹配的命令行关键字（默认 {DEFAULT_MATCH}）")
    parser.add_argument("-d", "--duration", type=int, default=60, help="采样时长（秒，默认 60）")
    parser.add_argument("-r", "--rate", type=int, default=100, help="采样频率 Hz（默认 100）")
    parser.add_argument("-t", "--threads", action="store_true", help="火焰图按线程分组")
    parser.add_argument("--top", action="store_true", help="仅显示实时 top 视图（不生成火焰图）")
    parser.add_argument("--nonblocking", action="store_true", help="非阻塞采样：降低对目标进程的影响，精度略降")
    parser.add_argument("--elevate", action="store_true", help="直接以管理员身份重启本脚本")
    parser.add_argument("--no-elevate", action="store_true", help="采样失败时不自动提权重试")
    parser.add_argument("--no-open", action="store_true", help="不自动打开火焰图")
    parser.add_argument("--elevated", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.elevate and not args.elevated and not is_admin():
        relaunch_elevated()

    pyspy = find_pyspy()
    if args.pid:
        pid, desc = args.pid, f"PID {args.pid}"
    else:
        pid, desc = find_target(args.match, auto_elevate=not (args.elevated or args.no_elevate))
    print(f"目标进程: {desc}")

    out: Path | None = None
    if args.top:
        cmd = [pyspy, "top", "--pid", str(pid)]
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUTPUT_DIR / f"cpu-{time.strftime('%Y%m%d-%H%M%S')}.svg"
        cmd = [
            pyspy,
            "record",
            "--pid",
            str(pid),
            "--duration",
            str(args.duration),
            "--rate",
            str(args.rate),
            "--output",
            str(out),
        ]
        if args.threads:
            cmd.append("--threads")
    if args.nonblocking:
        cmd.append("--nonblocking")

    print("执行:", " ".join(cmd))
    if not args.top:
        print(f"采样中（{args.duration}s），期间请让目标程序保持正常运行...")
    code = subprocess.run(cmd, check=False).returncode

    if code != 0 and not args.elevated and not args.no_elevate and not is_admin():
        print("采样失败：目标可能以管理员运行，尝试提权重试（UAC）...")
        relaunch_elevated()

    if code != 0:
        raise SystemExit(f"py-spy 退出码 {code}")

    if out is not None:
        print(f"火焰图已生成: {out}")
        if not args.no_open:
            os.startfile(out)  # 默认浏览器打开火焰图


if __name__ == "__main__":
    main()
