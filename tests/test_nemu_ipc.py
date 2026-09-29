"""Task 3: NemuIpc 封装（fake lib，无需真 DLL）。"""
import ctypes

import pytest

from src.utils.emulator import nemu_ipc as ni


class _FakeLib:
    def __init__(self, **behaviors):
        self.behaviors = behaviors
        self.calls = []

    def _set(self, name, fn):
        self.behaviors[name] = fn

    # NemuIpc 只调用这些符号并设置 argtypes/restype，故 fake 需可用属性赋值
    def __getattr__(self, item):
        if item in self.behaviors:
            return self.behaviors[item]
        # Ruling 6: NemuIpc.__init__ 会给全部 8 个 nemu_* 符号赋 argtypes/restype，
        # 未显式配置行为的 nemu_* 符号返回默认 no-op 函数；nemu_get_display_id 默认 -1，
        # 使 refresh_display_id 保持原有 display_id。其余未知属性仍抛 AttributeError。
        if item.startswith("nemu_"):
            if item == "nemu_get_display_id":
                return lambda *a, **k: -1
            return lambda *a, **k: 0
        raise AttributeError(item)


def test_load_failure_raises_incompatible(monkeypatch):
    def boom(path):
        raise OSError("no dll")

    monkeypatch.setattr(ctypes, "CDLL", boom)
    with pytest.raises(ni.NemuIpcIncompatible):
        ni.NemuIpc("x.dll", 0)


def test_find_ipc_dll(tmp_path, monkeypatch):
    dll = tmp_path / "nx_main" / "sdk" / "external_renderer_ipc.dll"
    dll.parent.mkdir(parents=True)
    dll.write_bytes(b"x")
    got = ni.find_ipc_dll(str(tmp_path))
    assert got and got.endswith("external_renderer_ipc.dll")
    assert ni.find_ipc_dll(str(tmp_path), str(dll)) == str(dll)
    assert ni.find_ipc_dll("") is None


def test_connect_and_capture(monkeypatch):
    lib = _FakeLib()
    lib._set("nemu_connect", lambda folder, iid: 7)
    lib._set("nemu_disconnect", lambda cid: 0)
    lib._set("nemu_capture_display", lambda cid, did, length, pw, ph, buf: _fill(buf, length, pw, ph))
    lib._set("nemu_get_display_id", lambda cid, pkg, idx: -1)

    def _fill(buf, length, pw, ph):
        pw.contents.value = 2
        ph.contents.value = 2
        if buf:
            for i in range(16):
                ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))[i] = i
        return 0

    monkeypatch.setattr(ni.ctypes, "CDLL", lambda p: lib)
    ipc = ni.NemuIpc("y.dll", 1)
    ipc.connect()
    assert ipc.connect_id == 7
    img = ipc.capture()
    assert img.shape == (2, 2, 4)
    ipc.disconnect()
    assert ipc.connect_id == 0


def test_connect_failure_raises(monkeypatch):
    lib = _FakeLib()
    lib._set("nemu_connect", lambda folder, iid: 0)
    monkeypatch.setattr(ni.ctypes, "CDLL", lambda p: lib)
    ipc = ni.NemuIpc("y.dll", 1)
    with pytest.raises(ni.NemuIpcError):
        ipc.connect()