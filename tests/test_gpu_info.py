"""GPU 信息查询单元测试。

原先程序内通过 config.debug.gpu_debug（no_gpu / multi_gpu）模拟显卡环境，
现改为在本文件中用 mock 覆盖 nvidia-smi 与 Paddle 的返回值，覆盖无卡、多卡、
查询失败等场景，程序内不再保留调试开关。
"""

import contextlib
import importlib
import sys
import types

import pytest

from src.utils import gpu_info


class FakeLogger:
    """记录日志调用，避免测试输出污染"""

    def __init__(self):
        self.messages: list[tuple[str, str]] = []

    def __getattr__(self, level: str):
        if level not in {"info", "warning", "error", "debug", "ui", "ui_warn", "ui_error", "ui_hint"}:
            raise AttributeError(level)

        def _log(msg, *args, **kwargs):
            self.messages.append((level, str(msg)))

        return _log


def _fake_proc(returncode: int = 0, stdout: str = "", stderr: str = ""):
    return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def _install_fake_paddle(monkeypatch, *, cuda: bool = False, count: int = 0, names=()):
    """向 sys.modules 注入假 paddle，模拟 CUDA 环境"""
    module = types.ModuleType("paddle")
    module.is_compiled_with_cuda = lambda: cuda
    module.device = types.SimpleNamespace(
        cuda=types.SimpleNamespace(
            device_count=lambda: count,
            get_device_name=lambda i: names[i],
        )
    )
    monkeypatch.setitem(sys.modules, "paddle", module)


@pytest.fixture
def fake_hide_window(monkeypatch):
    """替换 paddle_hide_window_context，避免真实导入/窗口操作"""
    module = importlib.import_module("src.utils.ocr_engine.paddleocr")
    monkeypatch.setattr(module, "paddle_hide_window_context", contextlib.nullcontext)


def test_resolve_device():
    assert gpu_info.resolve_device(None) is None
    assert gpu_info.resolve_device(-1) is None
    assert gpu_info.resolve_device(0) == "gpu:0"
    assert gpu_info.resolve_device(3) == "gpu:3"


def test_find_nvidia_smi_prefers_path(monkeypatch):
    monkeypatch.setattr(gpu_info.shutil, "which", lambda name: r"C:\tools\nvidia-smi.exe")
    assert gpu_info._find_nvidia_smi() == r"C:\tools\nvidia-smi.exe"


def test_find_nvidia_smi_fallback_system32(monkeypatch, tmp_path):
    monkeypatch.setattr(gpu_info.shutil, "which", lambda name: None)
    monkeypatch.setenv("SystemRoot", str(tmp_path))
    target = tmp_path / "System32" / "nvidia-smi.exe"
    target.parent.mkdir()
    target.write_bytes(b"")
    assert gpu_info._find_nvidia_smi() == str(target)


def test_find_nvidia_smi_not_found(monkeypatch, tmp_path):
    monkeypatch.setattr(gpu_info.shutil, "which", lambda name: None)
    monkeypatch.setenv("SystemRoot", str(tmp_path))
    assert gpu_info._find_nvidia_smi() is None


def test_find_nvidia_smi_exception_returns_none(monkeypatch):
    def boom(name):
        raise OSError("boom")

    monkeypatch.setattr(gpu_info.shutil, "which", boom)
    assert gpu_info._find_nvidia_smi() is None


def test_query_nvidia_smi_success(monkeypatch):
    monkeypatch.setattr(gpu_info, "_find_nvidia_smi", lambda: "nvidia-smi.exe")
    monkeypatch.setattr(
        gpu_info.subprocess,
        "run",
        lambda *a, **k: _fake_proc(stdout="0, NVIDIA RTX, 8188, 100, 8088, 40, 617.42\n"),
    )
    assert "NVIDIA RTX" in gpu_info._query_nvidia_smi([])


def test_query_nvidia_smi_without_executable(monkeypatch):
    monkeypatch.setattr(gpu_info, "_find_nvidia_smi", lambda: None)
    assert gpu_info._query_nvidia_smi([]) is None


def test_query_nvidia_smi_nonzero_returns_none(monkeypatch):
    monkeypatch.setattr(gpu_info, "_find_nvidia_smi", lambda: "nvidia-smi.exe")
    monkeypatch.setattr(
        gpu_info.subprocess,
        "run",
        lambda *a, **k: _fake_proc(returncode=1, stderr="driver error"),
    )
    assert gpu_info._query_nvidia_smi([]) is None


def test_query_nvidia_smi_exception_returns_none(monkeypatch):
    monkeypatch.setattr(gpu_info, "_find_nvidia_smi", lambda: "nvidia-smi.exe")

    def boom(*args, **kwargs):
        raise OSError("exec failed")

    monkeypatch.setattr(gpu_info.subprocess, "run", boom)
    assert gpu_info._query_nvidia_smi([]) is None


def test_get_gpu_list_parses_multiple_gpus(monkeypatch):
    stdout = (
        "0, NVIDIA A, 8192, 1024, 7168, 40, 600.1\n"
        "1, NVIDIA B, 16384, 2048, 14336, 45, 600.1\n"
    )
    monkeypatch.setattr(gpu_info, "_query_nvidia_smi", lambda args: stdout)
    gpus = gpu_info.get_gpu_list()
    assert [g["index"] for g in gpus] == [0, 1]
    assert gpus[1]["name"] == "NVIDIA B"
    assert gpus[0]["driver"] == "600.1"


def test_get_gpu_list_no_gpu(monkeypatch):
    monkeypatch.setattr(gpu_info, "_query_nvidia_smi", lambda args: None)
    assert gpu_info.get_gpu_list() == []


def test_get_gpu_list_skips_malformed_lines(monkeypatch):
    stdout = "0, NVIDIA A, 8192, 1, 8191, 40, 600.1\nbad line\n1, NVIDIA B, x, 1, 2, 3, 4\n"
    monkeypatch.setattr(gpu_info, "_query_nvidia_smi", lambda args: stdout)
    gpus = gpu_info.get_gpu_list()
    assert len(gpus) == 1
    assert gpus[0]["name"] == "NVIDIA A"


def test_get_gpu_list_query_exception_returns_empty(monkeypatch):
    def boom(args):
        raise RuntimeError("boom")

    monkeypatch.setattr(gpu_info, "_query_nvidia_smi", boom)
    assert gpu_info.get_gpu_list() == []


@pytest.mark.usefixtures("fake_hide_window")
def test_get_cuda_device_list_no_cuda(monkeypatch):
    _install_fake_paddle(monkeypatch, cuda=False)
    assert gpu_info.get_cuda_device_list() == []


@pytest.mark.usefixtures("fake_hide_window")
def test_get_cuda_device_list_multi_gpu(monkeypatch):
    _install_fake_paddle(monkeypatch, cuda=True, count=2, names=["NVIDIA A", "NVIDIA B"])
    assert gpu_info.get_cuda_device_list() == ["NVIDIA A", "NVIDIA B"]


@pytest.mark.usefixtures("fake_hide_window")
def test_get_cuda_device_list_zero_device(monkeypatch):
    _install_fake_paddle(monkeypatch, cuda=True, count=0)
    assert gpu_info.get_cuda_device_list() == []


def test_get_cuda_device_list_import_failure(monkeypatch):
    monkeypatch.setitem(sys.modules, "paddle", None)
    assert gpu_info.get_cuda_device_list() == []


def test_log_nvidia_smi_without_gpu(monkeypatch):
    fake = FakeLogger()
    monkeypatch.setattr(gpu_info, "logger", fake)
    gpu_info._log_nvidia_smi([])
    assert fake.messages and fake.messages[0][0] == "ui_error"


def test_log_nvidia_smi_logs_each_gpu(monkeypatch):
    fake = FakeLogger()
    monkeypatch.setattr(gpu_info, "logger", fake)
    gpu_info._log_nvidia_smi(
        [
            {
                "index": 0,
                "name": "NVIDIA A",
                "memory_total": 8192,
                "memory_used": 1024,
                "memory_free": 7168,
                "temperature": 40,
                "driver": "600.1",
            }
        ]
    )
    assert any("GPU[0] NVIDIA A" in msg for _, msg in fake.messages)


def test_log_gpu_info_swallows_exception(monkeypatch):
    fake = FakeLogger()
    monkeypatch.setattr(gpu_info, "logger", fake)

    def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(gpu_info, "get_gpu_list", boom)
    gpu_info.log_gpu_info()  # 不应抛出异常
    assert any("GPU 信息查询失败" in msg for _, msg in fake.messages)


def test_log_gpu_info_normal_flow(monkeypatch):
    fake = FakeLogger()
    monkeypatch.setattr(gpu_info, "logger", fake)
    calls = []
    monkeypatch.setattr(gpu_info, "get_gpu_list", lambda: [{"index": 0}])
    monkeypatch.setattr(gpu_info, "_log_nvidia_smi", lambda gpus: calls.append("nvidia"))
    monkeypatch.setattr(gpu_info, "get_cuda_device_list", lambda: ["NVIDIA A"])
    monkeypatch.setattr(gpu_info, "_log_paddle_gpu", lambda: calls.append("paddle"))

    gpu_info.log_gpu_info()

    assert calls == ["nvidia", "paddle"]
    assert any(level == "ui_hint" for level, _ in fake.messages)
