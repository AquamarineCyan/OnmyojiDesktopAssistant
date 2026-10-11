"""更新链路的安全闸门：SHA-256 校验、落盘原子性、脚本健壮性。

这些用例对应一条真实的提权 RCE 链：更新包经第三方镜像站分发 →
解压 → 以管理员权限覆盖安装目录 → 执行，全程没有任何完整性校验。
"""
import hashlib
import re
import zipfile
from pathlib import Path

import pytest


@pytest.fixture
def update_manager(tmp_path, monkeypatch):
    """构造一个 file 指向临时目录的 Update 实例，避免碰真实安装目录"""
    from src.utils import update as update_module

    mgr = update_module.Update()
    mgr.file = str(tmp_path / "pkg.zip")
    return mgr


def _write(path: Path, data: bytes) -> str:
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def test_sha256_accepts_matching_file(update_manager, tmp_path):
    f = tmp_path / "pkg.zip"
    digest = _write(f, b"hello world")

    assert update_manager._verify_sha256(str(f), digest) is True


def test_sha256_rejects_tampered_file(update_manager, tmp_path):
    f = tmp_path / "pkg.zip"
    digest = _write(f, b"hello world")
    f.write_bytes(b"hello worle")  # 篡改一个字节

    assert update_manager._verify_sha256(str(f), digest) is False


def test_sha256_rejects_empty_expectation(update_manager, tmp_path):
    """远端没给校验和时必须判失败，不能因为「无法比对」就放行"""
    f = tmp_path / "pkg.zip"
    _write(f, b"hello world")

    assert update_manager._verify_sha256(str(f), "") is False


def test_sha256_rejects_wrong_length_digest(update_manager, tmp_path):
    f = tmp_path / "pkg.zip"
    _write(f, b"hello world")

    assert update_manager._verify_sha256(str(f), "deadbeef") is False


def test_normalize_sha256_variants():
    from src.utils.update import normalize_sha256

    raw = "a" * 64
    assert normalize_sha256(raw) == raw
    assert normalize_sha256(raw.upper()) == raw
    assert normalize_sha256(f"sha256:{raw}") == raw
    # 非 sha256 算法应被拒绝
    assert normalize_sha256(f"md5:{'a' * 32}") == ""
    # 长度不对应被拒绝
    assert normalize_sha256("abc") == ""
    assert normalize_sha256("") == ""


def test_verify_downloaded_zip_requires_both_size_and_hash(update_manager, tmp_path):
    f = tmp_path / "pkg.zip"
    payload = b"payload" * 100
    digest = _write(f, payload)

    update_manager.file_size = len(payload)
    update_manager.sha256 = digest
    assert update_manager._verify_downloaded_zip() is True

    # 体积对但哈希错 → 放行一个被篡改的包，必须拒绝
    update_manager.sha256 = "b" * 64
    assert update_manager._verify_downloaded_zip() is False

    # 哈希对但体积不符（截断）→ 也必须拒绝
    update_manager.sha256 = digest
    update_manager.file_size = len(payload) - 1
    assert update_manager._verify_downloaded_zip() is False


def test_mirrorchyan_info_does_not_self_certify_size(update_manager, tmp_path, monkeypatch):
    """回归：曾经用 os.stat 回填 file_size，把体积校验变成恒真比较"""
    from src.utils import update as update_module

    payload = b"x" * 50
    digest = _write(tmp_path / "pkg.zip", payload)

    info = update_module.UpdateInfo(
        source="MirrorChyan",
        url="https://example.invalid/pkg.zip",
        file_name="pkg.zip",
        version="9.9.9",
        file_size=999_999,  # 远端声明与实际不符
        sha256=digest,
    )
    monkeypatch.setattr(update_module, "check_for_update", lambda cdk: info)
    monkeypatch.setattr(update_module.Update, "download_update_zip", lambda self, url: True)
    monkeypatch.setattr(update_module.config.user, "mirrorchyan_cdk", "test-cdk", raising=False)

    assert update_manager._download_mirrorchyan() is True
    # 声明值必须原样保留，不能被本地实测值覆盖
    assert update_manager.file_size == 999_999
    assert update_manager._verify_downloaded_zip() is False


def test_restart_bat_uses_absolute_path_and_quoted_start(tmp_path):
    """restart.bat 在提权进程中执行：路径必须是绝对路径，start 必须带引号"""
    from src.utils import restart as restart_module

    mgr = restart_module.Restart()
    assert Path(mgr.bat_path).is_absolute()

    mgr.bat_path = str(tmp_path / "restart.bat")
    mgr.write_update_restart_bat()

    text = (tmp_path / "restart.bat").read_text(encoding="ascii")
    # start 的第一个带引号参数会被当成窗口标题，必须显式给空串
    assert 'start "" "%program_name%"' in text
    # xcopy 失败必须能被发现，否则会「覆盖失败却删掉更新包并报成功」
    assert "if errorlevel 1 goto :fail" in text
    # 等待循环要有上限
    assert re.search(r"if !_tries! gtr \d+", text)


def test_restart_bat_is_pure_ascii(tmp_path):
    """脚本用固定编码写入，中文内容在西文 locale 上会直接写失败"""
    from src.utils import restart as restart_module

    mgr = restart_module.Restart()
    mgr.bat_path = str(tmp_path / "restart.bat")
    mgr.write_restart_bat()
    mgr.write_update_restart_bat()

    text = (tmp_path / "restart.bat").read_text(encoding="ascii")
    assert all(ord(c) < 128 for c in text)


def test_unzip_skips_utime_failure_and_keeps_going(tmp_path, monkeypatch):
    """单条文件的 os.utime 失败不应中断整包解压"""
    from src.utils import update as update_module

    mgr = update_module.Update()
    payload = tmp_path / "pkg.zip"
    with zipfile.ZipFile(payload, "w") as zf:
        zf.writestr("a.txt", "a")
        zf.writestr("b.txt", "b")

    mgr.file = str(payload)
    monkeypatch.setattr(update_module, "APP_PATH", tmp_path)

    def boom(*args, **kwargs):
        raise OSError("nope")

    monkeypatch.setattr(update_module.os, "utime", boom)
    assert mgr._unzip_handle() is True
    # zip_files_path 由 APP_PATH 推导，见 _unzip_handle 内部
    assert (tmp_path / "zip_files" / "a.txt").is_file()
    assert (tmp_path / "zip_files" / "b.txt").is_file()


def test_announcement_rejects_malformed_entries():
    """公告与更新包同源，不能当作可信输入"""
    from src.utils.announcement import _validate

    good = {"id": 3, "content": "hello", "title": "t"}
    result = _validate(
        [
            good,
            {"content": "缺 id"},  # 排序时 KeyError
            {"id": "4", "content": "id 是字符串"},  # 比较时 TypeError
            {"id": True, "content": "bool"},  # bool 是 int 的子类
            {"id": 99999999999999, "content": "id 越界"},
            {"id": 5, "content": ""},
            "不是对象",
        ]
    )

    assert result is not None
    assert [a["id"] for a in result] == [3]


def test_announcement_validate_rejects_non_list():
    from src.utils.announcement import _validate

    assert _validate({"id": 1}) is None
    assert _validate("字符串") is None


def test_mark_as_read_ignores_out_of_range_id():
    """远端 id 可写进用户配置，超大值会永久压制后续所有公告"""
    from src.utils import announcement as ann

    recorded = []
    original = ann.config.update
    ann.config.update = lambda k, v: recorded.append((k, v))
    try:
        ann.mark_as_read(99999999999999)
        ann.mark_as_read("abc")
        ann.mark_as_read(True)
        assert recorded == []
    finally:
        ann.config.update = original


def test_open_safe_link_rejects_non_http_schemes():
    from PySide6.QtCore import QUrl

    from src.ui.ui_utils import is_safe_link

    assert is_safe_link(QUrl("https://example.com/a")) is True
    assert is_safe_link(QUrl("http://example.com/a")) is True
    # 这些会把系统拉去执行本地程序或访问网络共享
    for bad in ("file:///C:/Windows/System32/calc.exe", "\\\\host\\share\\p.exe", "ms-settings:", "javascript:alert(1)"):
        assert is_safe_link(QUrl(bad)) is False, bad
