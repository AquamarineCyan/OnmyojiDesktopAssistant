"""Task 2: 枚举 + cli 解析 + 句柄树判定（monkeypatch 假 win32/子进程，无需真机）。"""
import src.utils.emulator.mumu_handle as mh


class _FakeGui:
    """假 win32gui：桌面窗口表 + 类名/标题表 + 父子关系。"""

    def __init__(self, tops, cls, titles, parents):
        self.tops = tops          # hwnd -> exe 归属由 _exe_of 决定
        self.cls = cls
        self.titles = titles
        self.parents = parents    # hwnd -> parent hwnd (0=顶层)

    def EnumWindows(self, cb, _):
        for h in sorted(self.tops):
            cb(h, None)
        return True

    def IsWindow(self, h):
        return h in self.tops

    def GetClassName(self, h):
        return self.cls.get(h, "")

    def GetWindowText(self, h):
        return self.titles.get(h, "")

    def GetParent(self, h):
        return self.parents.get(h, 0)

    def EnumChildWindows(self, h, cb, lparam=None):  # lparam 透传，对齐真实 win32gui API
        for c, p in self.parents.items():
            if p == h:
                cb(c, lparam)
        return True


def _mk(monkeypatch, tops, cls, titles, parents):
    fake = _FakeGui(tops, cls, titles, parents)
    monkeypatch.setattr(mh, "_gui", fake)
    monkeypatch.setattr(mh, "is_window", lambda h: h in tops)
    monkeypatch.setattr(mh, "_exe_of", lambda pid: "MuMuNxDevice.exe")
    return fake


def _qt_tree():
    """本机实测树：根 Qt5156QWindowIcon → Qt5156QWindowIcon(MuMuNxDevice) → nemuwin(nemudisplay)"""
    tops = {100: "", 200: "", 300: "NxUpdaterMessageWndMuMuPlayer", 400: "", 500: "IME"}
    cls = {100: "Qt5156QWindowIcon", 200: "Qt5156QWindowToolSaveBits",
           300: "Static", 400: "NVOpenGLPbuffer", 500: "IME"}
    titles = {100: "MuMu安卓设备-1", 200: "MuMuNxDevice", 300: "x", 400: "__wglDummyWindowFodder", 500: "Default IME"}
    parents = {110: 100, 111: 110, 200: 0, 300: 0, 400: 0, 500: 0}
    cls[110] = "Qt5156QWindowIcon"; cls[111] = "nemuwin"
    titles[110] = "MuMuNxDevice"; titles[111] = "nemudisplay"
    return tops, cls, titles, parents


def test_enum_excludes_helper_windows(monkeypatch):
    tops, cls, titles, parents = _qt_tree()
    _mk(monkeypatch, tops, cls, titles, parents)
    got = mh.enum_mumu_by_process()
    assert got == [100]  # 200/300/400/500 全部排除


def test_build_handle_qt_tree(monkeypatch):
    tops, cls, titles, parents = _qt_tree()
    _mk(monkeypatch, tops, cls, titles, parents)
    h = mh.build_handle(100, wait_tries=1)
    assert h.root_hwnd == 100
    assert h.shot_hwnd == 111 and h.control_hwnds == [100, 111]
    assert h.client_w > 0


def test_build_handle_legacy_tree(monkeypatch):
    """OnmyojiAuto 旧树：根 → MuMuPlayer 首子。"""
    tops = {100: ""}
    cls = {100: "root", 110: "MuMuPlayer"}
    titles = {100: "MuMu模拟器12", 110: ""}
    parents = {110: 100}
    _mk(monkeypatch, tops, cls, titles, parents)
    h = mh.build_handle(100, wait_tries=1)
    assert h.shot_hwnd == 110


def test_build_handle_rejects_pc_window(monkeypatch):
    tops = {100: ""}  # 无子窗口的普通窗口（如 onmyoji.exe）
    _mk(monkeypatch, tops, {}, {"100": "阴阳师-MuMu模拟器专版"}, {})
    try:
        mh.build_handle(100, wait_tries=1)
    except ValueError:
        return
    raise AssertionError("expected ValueError for non-MuMu tree")


def test_query_cli_windows_parses_started_only(monkeypatch):
    payload = {
        "0": {"name": "MuMu安卓设备", "is_android_started": False, "is_process_started": False, "main_wnd": "000000A0"},
        "1": {"name": "MuMu安卓设备-1", "is_android_started": True, "is_process_started": True,
              "main_wnd": "00830C5E", "render_wnd": "000E0CC6"},
    }
    monkeypatch.setattr(mh, "_mumu_cli_json", lambda f: _fake_cli(payload))
    monkeypatch.setattr(mh, "is_window", lambda h: h == 0x830C5E)  # 隔离真实桌面，无需真机
    rows = mh.query_cli_windows("E:\\MuMuPlayer")
    assert rows == [(0x830C5E, 1, "MuMu安卓设备-1")]
    assert mh._render_wnd_from_cli(0x830C5E, "E:\\MuMuPlayer") == 0xE0CC6


def _fake_cli(payload):
    out = []
    for key, v in payload.items():
        v = dict(v)
        v["index"] = int(key)
        out.append(v)
    return out


def test_discover_orders_by_instance(monkeypatch):
    def _cli(folder):
        return [
            {"index": 1, "main_wnd": "00000002", "name": "MuMu安卓设备-1", "is_process_started": True},
            {"index": 0, "main_wnd": "00000001", "name": "MuMu安卓设备", "is_process_started": True},
        ]

    monkeypatch.setattr(mh, "_mumu_cli_json", _cli)
    monkeypatch.setattr(mh, "is_window", lambda h: h in (1, 2))  # 隔离真实桌面，无需真机
    monkeypatch.setattr(mh, "enum_mumu_by_process", lambda: [])  # 兜底路径也不触真实桌面
    got = mh.discover_clients("E:\\MuMuPlayer")
    assert got == [(0, 1, "MuMu安卓设备"), (1, 2, "MuMu安卓设备-1")]  # 实例1 在前


def test_resolve_auto_prefers_cli(monkeypatch):
    def _cli(folder):
        return [
            {"index": 1, "main_wnd": "00000002", "name": "MuMu安卓设备-1", "is_process_started": True},
            {"index": 0, "main_wnd": "00000001", "name": "MuMu安卓设备", "is_process_started": True},
        ]

    monkeypatch.setattr(mh, "_mumu_cli_json", _cli)
    monkeypatch.setattr(mh, "is_window", lambda h: h in (1, 2))  # 隔离真实桌面，无需真机
    monkeypatch.setattr(mh, "enum_mumu_by_process", lambda: [])  # 兜底路径也不触真实桌面
    assert mh.resolve_auto(0, "E:\\MuMuPlayer") == (1, 0)  # 按实例序，非相遇序
    assert mh.resolve_auto(1, "E:\\MuMuPlayer") == (2, 1)


def test_resolve_auto_process_fallback(monkeypatch):
    monkeypatch.setattr(mh, "_mumu_cli_json", lambda f: [])
    monkeypatch.setattr(mh, "enum_mumu_by_process", lambda: [200, 100])

    def _build(spec, mumu_folder="", wait_tries=10):
        if int(spec) == 200:
            return mh.MumuHandle(root_hwnd=200, root_title="MuMu安卓设备-2", shot_hwnd=200,
                                 control_hwnds=[200, 200], scale_rate=1.0, client_w=100, client_h=100)
        return mh.MumuHandle(root_hwnd=100, root_title="MuMu安卓设备", shot_hwnd=100,
                             control_hwnds=[100, 100], scale_rate=1.0, client_w=100, client_h=100)

    monkeypatch.setattr(mh, "build_handle", _build)
    assert mh.resolve_auto(0) == (100, 0)  # 按 hwnd 升序，标题后缀号
    assert mh.resolve_auto(1) == (200, 2)


def _counted_cli(calls, rows):
    def _cli(folder):
        calls.append(folder)
        return rows
    return _cli


def test_cli_json_cached_returns_cached_rows_within_ttl(monkeypatch):
    """Imp #2: TTL 内第二次调用命中缓存，不再起 mumu-cli 子进程。"""
    calls = []
    rows = [{"index": 0, "main_wnd": "00000001", "name": "MuMu安卓设备", "is_process_started": True}]
    monkeypatch.setattr(mh, "_mumu_cli_json", _counted_cli(calls, rows))
    a = mh._mumu_cli_json_cached("E:\\MuMuPlayer")
    b = mh._mumu_cli_json_cached("E:\\MuMuPlayer")
    assert a is b
    assert len(calls) == 1


def test_cli_json_cached_expires_after_ttl(monkeypatch):
    """Imp #2: TTL 过期后重新调用底层函数。"""
    calls = []
    rows = [{"index": 0, "main_wnd": "00000001", "name": "MuMu安卓设备", "is_process_started": True}]
    monkeypatch.setattr(mh, "_mumu_cli_json", _counted_cli(calls, rows))
    now = [1000.0]
    monkeypatch.setattr(mh.time, "monotonic", lambda: now[0])
    mh._mumu_cli_json_cached("E:\\MuMuPlayer")
    mh._mumu_cli_json_cached("E:\\MuMuPlayer")
    assert len(calls) == 1
    now[0] += 5.0  # 超过 1s TTL
    mh._mumu_cli_json_cached("E:\\MuMuPlayer")
    assert len(calls) == 2


def test_cli_json_cached_recompute_when_function_changed(monkeypatch):
    """Imp #2: 底层函数对象变化（测试 monkeypatch / 热替换）时缓存自动失效。"""
    calls = []
    rows = [{"index": 0, "main_wnd": "00000001", "name": "MuMu安卓设备", "is_process_started": True}]
    monkeypatch.setattr(mh, "_mumu_cli_json", _counted_cli(calls, rows))
    mh._mumu_cli_json_cached("E:\\MuMuPlayer")
    monkeypatch.setattr(mh, "_mumu_cli_json", _counted_cli(calls, []))  # 换一个函数对象
    assert mh._mumu_cli_json_cached("E:\\MuMuPlayer") == []
    assert len(calls) == 2


def test_mumu_root_from_dll():
    """C2: 由 external_renderer_ipc.dll 路径反推安装根（覆盖 nx_main / nx_device 两种布局）。"""
    assert mh.mumu_root_from_dll(
        r"D:\Apps\MuMuPlayer\nx_main\sdk\external_renderer_ipc.dll"
    ) == r"D:\Apps\MuMuPlayer"
    assert mh.mumu_root_from_dll(
        r"C:\Program Files\MuMuPlayer\nx_device\15.0\shell\sdk\x.dll"
    ) == r"C:\Program Files\MuMuPlayer"
    assert mh.mumu_root_from_dll(r"C:\somewhere\else\x.dll") == ""