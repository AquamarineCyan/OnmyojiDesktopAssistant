"""Task 1: MuMu 安装目录五级降级探测（monkeypatch 挂载点，无需真机）。"""
import pytest

import src.utils.emulator.mumu_handle as mh


@pytest.fixture(autouse=True)
def _clean_cache():
    """每个测试前清空探测缓存：空配置探测结果会写入模块级 _detect_cache。"""
    mh.reset_detect_cache()


def test_configured_used_when_valid(tmp_path):
    root = tmp_path / "MuMuPlayer"
    cli = root / "nx_main" / "mumu-cli.exe"
    cli.parent.mkdir(parents=True)
    cli.write_text("x")
    assert mh.detect_mumu_folder(str(root)) == str(root)


def test_configured_invalid_falls_to_process_exe(monkeypatch, tmp_path):
    root = tmp_path / "MuMuPlayer"
    (root / "nx_main").mkdir(parents=True)
    (root / "nx_main" / "mumu-cli.exe").write_text("x")
    monkeypatch.setattr(mh, "_running_mumu_exes",
                        lambda: [str(root / "nx_main" / "MuMuNxMain.exe")])
    # 假配置无效时降级到进程 exe 反推
    assert mh.detect_mumu_folder("C:\\no\\such\\dir") == str(root)


def test_exe_to_root_walks_up(tmp_path):
    root = tmp_path / "MuMuPlayer"
    (root / "nx_main").mkdir(parents=True)
    (root / "nx_main" / "mumu-cli.exe").write_text("x")
    dev = root / "nx_device" / "15.0" / "shell" / "MuMuNxDevice.exe"
    assert mh._exe_to_root(str(dev)) == str(root)


def test_exe_to_root_rejects_vbox_service(tmp_path):
    svc = tmp_path / "MuMuNxVbox" / "Hypervisor" / "MuMuNxSVC.exe"
    svc.parent.mkdir(parents=True)
    svc.write_text("x")
    assert mh._exe_to_root(str(svc)) == ""


def test_uninstall_locations_filters_non_mumu(monkeypatch):
    """假 winreg 必须镜像真实 API：模块级函数 QueryInfoKey/EnumKey/QueryValueEx + PyHKEY 上下文管理。"""

    class _Key:  # 单个卸载键（支持 with + Close，等价 PyHKEY）
        def __init__(self, values):
            self._values = values

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    class _Hive:  # Uninstall 根键：枚举子键名
        def __init__(self, names):
            self._names = names

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    class _FakeWinreg:
        HKEY_LOCAL_MACHINE = object()

        def OpenKey(self, hkey, path):
            if "WOW6432Node" in str(path):
                raise OSError
            if "Uninstall" in str(path):
                return _Hive(["MuMu模拟器", "OnmyojiLauncher"])
            if path == "MuMu模拟器":
                return _Key({"DisplayName": "MuMu模拟器", "InstallLocation": "E:\\MuMuPlayer"})
            return _Key({"DisplayName": "阴阳师模拟器专版",
                         "InstallLocation": r"C:\Program Files (x86)\Netease\OnmyojiLauncher"})

        def QueryInfoKey(self, k):
            return (len(getattr(k, "_names", ())), 0, 0)

        def EnumKey(self, k, i):
            return k._names[i]

        def QueryValueEx(self, k, name):
            return k._values[name], 1

    monkeypatch.setattr(mh, "_winreg", _FakeWinreg())
    got = mh._uninstall_locations()
    assert got == ["E:\\MuMuPlayer"]  # 专版客户端 DisplayName 不含 'mumu' → 排除


def test_no_signal_returns_empty(monkeypatch):
    monkeypatch.setattr(mh, "_valid_root", lambda r: False)
    monkeypatch.setattr(mh, "_running_mumu_exes", lambda: [])
    monkeypatch.setattr(mh, "_uninstall_locations", lambda: [])
    assert mh.detect_mumu_folder("") == ""


def test_is_valid_mumu_folder(tmp_path):
    ok = tmp_path / "MuMuPlayer"
    (ok / "nx_main").mkdir(parents=True)
    (ok / "nx_main" / "mumu-cli.exe").write_text("x")
    assert mh.is_valid_mumu_folder(str(ok))
    assert not mh.is_valid_mumu_folder(str(tmp_path / "nowhere"))