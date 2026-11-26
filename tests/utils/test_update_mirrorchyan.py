"""Mirror酱 线路检查更新与 CDK 剩余天数（无 GUI 依赖）。

回归背景：
- 下载站点为 Mirror酱 时，检查更新只请求 Mirror酱 `/latest`，不再调用 GitHub Releases；
- 未填写 CDK 直接返回错误提示，不发起请求；
- 检查结果回填到 update_manager，下载阶段复用，避免重复请求接口。
"""

import hashlib
import threading
import time
from types import SimpleNamespace

import pytest

from src.utils import update as update_module
from src.utils.config import UpdateDownload, config
from src.utils.message import MessageBoxPayload
from src.utils.update import (
    MirrorChyanError,
    MirrorChyanLatestResponse,
    StatusCode,
    Update,
    UpdateInfo,
    get_cdk_remaining_days,
    update_manager,
)


@pytest.fixture(autouse=True)
def mirrorchyan_route(monkeypatch):
    """默认走 Mirror酱 线路，并禁止写盘。"""
    monkeypatch.setattr(config.user, "update_download", UpdateDownload.MIRRORCHYAN)
    monkeypatch.setattr(config, "_save", lambda *args, **kwargs: None)


@pytest.fixture(autouse=True)
def reset_latest_cache():
    """隔离模块级 `/latest` 缓存，避免测试之间互相影响。"""
    update_module._mirrorchyan_latest_cache = None
    update_module._mirrorchyan_latest_inflight.clear()
    yield
    update_module._mirrorchyan_latest_cache = None
    update_module._mirrorchyan_latest_inflight.clear()


def _new_info() -> UpdateInfo:
    return UpdateInfo(
        source="MirrorChyan",
        url="https://example.com/a.zip",
        file_name="a.zip",
        version="9.9.9",
        file_size=123,
        release_note="更新内容",
    )


@pytest.fixture
def no_github(monkeypatch):
    def _fail(*args, **kwargs):
        pytest.fail("Mirror酱线路不应调用 GitHub Releases")

    monkeypatch.setattr(update_manager, "_fetch_releases", _fail)


@pytest.fixture
def no_write_record(monkeypatch):
    written = []
    monkeypatch.setattr(update_manager, "_write_update_record", written.append)
    return written


def test_missing_cdk_returns_error_without_request(monkeypatch):
    monkeypatch.setattr(config.user, "mirrorchyan_cdk", "")
    monkeypatch.setattr(
        update_module, "check_for_update", lambda *args, **kwargs: pytest.fail("未填写 CDK 不应请求接口")
    )

    status = update_manager.get_browser_download_url()

    assert status is StatusCode.MIRRORCHYAN_ERROR
    assert "未填写 Mirror酱 CDK" in update_manager.error_message


def test_latest_returns_latest(monkeypatch, no_github):
    monkeypatch.setattr(config.user, "mirrorchyan_cdk", "dummy")
    monkeypatch.setattr(update_module, "check_for_update", lambda cdk, timeout=10, *, force=False: None)

    assert update_manager.get_browser_download_url() is StatusCode.LATEST


def test_new_version_backfills_manager(monkeypatch, no_github, no_write_record):
    monkeypatch.setattr(config.user, "mirrorchyan_cdk", "dummy")
    monkeypatch.setattr(update_module, "check_for_update", lambda cdk, timeout=10, *, force=False: _new_info())

    status = update_manager.get_browser_download_url()

    assert status is StatusCode.NEW_VERSION
    assert update_manager.new_version == "9.9.9"
    assert update_manager.new_version_info == "更新内容"
    assert update_manager.browser_download_url == "https://example.com/a.zip"
    assert update_manager.file == "a.zip"
    assert update_manager.file_size == 123
    assert update_manager.version_history == [{"version": "9.9.9", "body": "更新内容"}]
    assert update_manager.download_source is UpdateDownload.MIRRORCHYAN
    # 不覆盖 update_info.json 的 GitHub 多版本记录
    assert no_write_record == []


def test_cdk_error_exposes_friendly_message(monkeypatch, no_github):
    monkeypatch.setattr(config.user, "mirrorchyan_cdk", "expired")

    def _raise(cdk, timeout=10, *, force=False):
        err = MirrorChyanError("Mirror酱 API (code=7001): Mirror酱 CDK 已过期")
        err.code = 7001
        err.msg = "Mirror酱 CDK 已过期"
        raise err

    monkeypatch.setattr(update_module, "check_for_update", _raise)

    status = update_manager.get_browser_download_url()

    assert status is StatusCode.MIRRORCHYAN_ERROR
    assert update_manager.error_message == "Mirror酱 CDK 已过期"


def test_network_error_returns_connect_error(monkeypatch, no_github):
    monkeypatch.setattr(config.user, "mirrorchyan_cdk", "dummy")

    def _raise(cdk, timeout=10, *, force=False):
        raise MirrorChyanError("Mirror酱 请求失败: timeout")

    monkeypatch.setattr(update_module, "check_for_update", _raise)

    assert update_manager.get_browser_download_url() is StatusCode.CONNECT_ERROR


def test_download_reuses_checked_url(monkeypatch, tmp_path):
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(b"x")
    manager = Update()
    manager.file = str(local_zip)
    manager.file_size = 123
    manager.browser_download_url = "https://example.com/a.zip"
    manager.download_source = UpdateDownload.MIRRORCHYAN

    calls = []
    monkeypatch.setattr(manager, "download_update_zip", lambda url: calls.append(url) or True)
    monkeypatch.setattr(update_module, "check_for_update", lambda *args, **kwargs: pytest.fail("应复用检查更新结果"))
    monkeypatch.setattr(config.user, "mirrorchyan_cdk", "dummy")

    assert manager._download_mirrorchyan() is True
    assert calls == ["https://example.com/a.zip"]
    assert manager.file_size == 123


def test_download_ignores_url_from_other_source(monkeypatch, tmp_path):
    """检查走 GitHub、弹窗切到 Mirror酱 时，必须重新走 Mirror酱接口"""
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(b"x")
    manager = Update()
    manager.file = str(local_zip)
    manager.file_size = 123
    manager.browser_download_url = "https://github.com/a.zip"
    manager.download_source = UpdateDownload.GITHUB

    calls = []
    monkeypatch.setattr(manager, "download_update_zip", lambda url: calls.append(url) or True)
    monkeypatch.setattr(config.user, "mirrorchyan_cdk", "dummy")
    monkeypatch.setattr(
        update_module,
        "check_for_update",
        lambda cdk, timeout=10, *, force=False: UpdateInfo(
            source="MirrorChyan",
            url="https://mirror.example/a.zip",
            file_name=str(local_zip),
            version="9.9.9",
            file_size=123,
        ),
    )

    assert manager._download_mirrorchyan() is True
    assert calls == ["https://mirror.example/a.zip"]
    assert manager.browser_download_url == "https://mirror.example/a.zip"
    assert manager.download_source is UpdateDownload.MIRRORCHYAN


def test_download_retries_after_expired_url(monkeypatch, tmp_path):
    """复用地址下载失败后应重新获取一次地址"""
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(b"x")
    manager = Update()
    manager.file = str(local_zip)
    manager.file_size = 123
    manager.browser_download_url = "https://example.com/expired.zip"
    manager.download_source = UpdateDownload.MIRRORCHYAN

    calls = []
    force_calls = []

    def _download(url: str) -> bool:
        calls.append(url)
        return url != "https://example.com/expired.zip"

    def _check(cdk, timeout=10, *, force=False):
        force_calls.append(force)
        return UpdateInfo(
            source="MirrorChyan",
            url="https://example.com/fresh.zip",
            file_name=str(local_zip),
            version="9.9.9",
            file_size=123,
        )

    monkeypatch.setattr(manager, "download_update_zip", _download)
    monkeypatch.setattr(config.user, "mirrorchyan_cdk", "dummy")
    monkeypatch.setattr(update_module, "check_for_update", _check)

    assert manager._download_mirrorchyan() is True
    assert calls == ["https://example.com/expired.zip", "https://example.com/fresh.zip"]
    assert force_calls == [True]


def test_mirror_station_route_falls_back_to_direct_download(monkeypatch):
    """弹窗切到镜像站但地址来自 Mirror酱 时，直接下载而不是拼接非法地址"""
    manager = Update()
    manager.file = "a.zip"
    manager.file_size = 123
    manager.browser_download_url = "https://mirror.example/a.zip"
    manager.download_source = UpdateDownload.MIRRORCHYAN
    monkeypatch.setattr(config.user, "update_download", UpdateDownload.MIRROR)

    calls = []
    monkeypatch.setattr(manager, "_check_local_file", lambda *args: False)
    monkeypatch.setattr(manager, "download_update_zip", lambda url: calls.append(url) or True)
    monkeypatch.setattr(manager, "_download_by_mirror_stations", lambda: pytest.fail("不应使用镜像站拼接"))

    assert manager._check_download_zip() is True
    assert calls == ["https://mirror.example/a.zip"]


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload


def test_latest_response_optional_fields_default():
    latest = MirrorChyanLatestResponse.from_dict({"code": 0, "data": {"version_name": "v9.9.9"}})

    assert latest.code == 0
    assert latest.msg == ""
    assert latest.data.version_name == "v9.9.9"
    assert latest.data.url is None
    assert latest.data.filesize == 0
    assert latest.data.sha256 == ""
    assert latest.data.release_note == ""
    assert latest.data.cdk_expired_time == 0


def test_latest_response_full_fields():
    latest = MirrorChyanLatestResponse.from_dict(
        {
            "code": 0,
            "data": {
                "version_name": "9.9.9",
                "url": "https://example.com/a.zip",
                "filesize": 123,
                "sha256": "abcdef",
                "release_note": "更新内容",
                "cdk_expired_time": 1800000000,
            },
        }
    )

    assert latest.data.url == "https://example.com/a.zip"
    assert latest.data.filesize == 123
    assert latest.data.sha256 == "abcdef"
    assert latest.data.release_note == "更新内容"
    assert latest.data.cdk_expired_time == 1800000000


def test_latest_response_null_data_is_tolerated():
    latest = MirrorChyanLatestResponse.from_dict({"code": 0, "data": None})

    assert latest.data.version_name == ""
    assert latest.data.url is None


def test_request_latest_logs_raw_response(monkeypatch):
    logs = []
    monkeypatch.setattr(update_module.logger, "info", logs.append)
    monkeypatch.setattr(
        update_module.httpx,
        "get",
        lambda *args, **kwargs: _FakeResponse({"code": 0, "data": {"version_name": "1.0.0"}}),
    )

    update_module._request_mirrorchyan_latest("dummy")

    assert any("原始响应" in line and "version_name" in line for line in logs)


def test_latest_response_tolerates_invalid_field_types():
    latest = MirrorChyanLatestResponse.from_dict(
        {
            "code": "abc",
            "msg": 123,
            "data": {
                "version_name": 1,
                "filesize": "not-a-number",
                "cdk_expired_time": "not-a-number",
            },
        }
    )

    assert latest.code == 0
    assert latest.msg == "123"
    assert latest.data.version_name == "1"
    assert latest.data.filesize == 0
    assert latest.data.cdk_expired_time == 0


def test_request_latest_rejects_non_dict_payload(monkeypatch):
    monkeypatch.setattr(update_module.logger, "info", lambda *args: None)
    monkeypatch.setattr(update_module.httpx, "get", lambda *args, **kwargs: _FakeResponse(["bad"]))

    with pytest.raises(MirrorChyanError, match="格式异常"):
        update_module._request_mirrorchyan_latest("dummy")


def test_cdk_remaining_days_rounds_up(monkeypatch):
    expired = int(time.time()) + 3 * 86400
    monkeypatch.setattr(
        update_module.httpx,
        "get",
        lambda *args, **kwargs: _FakeResponse({"code": 0, "data": {"cdk_expired_time": expired}}),
    )

    assert get_cdk_remaining_days("dummy") == 3


def test_cdk_remaining_days_expired_is_negative(monkeypatch):
    expired = int(time.time()) - 2 * 86400
    monkeypatch.setattr(
        update_module.httpx,
        "get",
        lambda *args, **kwargs: _FakeResponse({"code": 0, "data": {"cdk_expired_time": expired}}),
    )

    assert get_cdk_remaining_days("dummy") <= 0


def test_cdk_remaining_days_without_expiry(monkeypatch):
    monkeypatch.setattr(
        update_module.httpx,
        "get",
        lambda *args, **kwargs: _FakeResponse({"code": 0, "data": {}}),
    )

    assert get_cdk_remaining_days("dummy") is None


def test_cdk_remaining_days_empty_cdk_skips_request(monkeypatch):
    monkeypatch.setattr(update_module.httpx, "get", lambda *args, **kwargs: pytest.fail("空 CDK 不应请求"))

    assert get_cdk_remaining_days("") is None


def test_cdk_remaining_days_raises_with_code_and_msg(monkeypatch):
    monkeypatch.setattr(
        update_module.httpx,
        "get",
        lambda *args, **kwargs: _FakeResponse({"code": 7002, "msg": "invalid cdk"}),
    )

    with pytest.raises(MirrorChyanError) as excinfo:
        get_cdk_remaining_days("dummy")

    assert excinfo.value.code == 7002
    assert excinfo.value.msg == "Mirror酱 CDK 错误"


def _latest_payload(**data) -> dict:
    return {"code": 0, "msg": "success", "data": data}


def test_latest_request_cached_within_ttl(monkeypatch):
    """TTL 内连续调用只发一次请求"""
    calls = []

    def _get(*args, **kwargs):
        calls.append(1)
        return _FakeResponse(_latest_payload(version_name="v9.9.9"))

    monkeypatch.setattr(update_module.httpx, "get", _get)

    first = update_module._request_mirrorchyan_latest("dummy")
    second = update_module._request_mirrorchyan_latest("dummy")

    assert first == second
    assert len(calls) == 1


def test_latest_request_force_bypasses_cache(monkeypatch):
    """force=True 时必须绕过缓存"""
    calls = []

    def _get(*args, **kwargs):
        calls.append(1)
        return _FakeResponse(_latest_payload(version_name="v9.9.9"))

    monkeypatch.setattr(update_module.httpx, "get", _get)

    update_module._request_mirrorchyan_latest("dummy")
    update_module._request_mirrorchyan_latest("dummy", force=True)

    assert len(calls) == 2


def test_latest_request_concurrent_single_flight(monkeypatch):
    """并发调用共享同一次请求"""
    calls = []
    entered = threading.Event()
    release = threading.Event()
    barrier = threading.Barrier(2)

    def _get(*args, **kwargs):
        calls.append(1)
        entered.set()
        assert release.wait(2)
        return _FakeResponse(_latest_payload(version_name="v9.9.9"))

    monkeypatch.setattr(update_module.httpx, "get", _get)

    results = []
    errors = []

    def _worker():
        try:
            barrier.wait(timeout=2)
            results.append(update_module._request_mirrorchyan_latest("dummy"))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=_worker) for _ in range(2)]
    for thread in threads:
        thread.start()

    assert entered.wait(2)
    release.set()

    for thread in threads:
        thread.join(2)

    assert not errors
    assert len(results) == 2
    assert len(calls) == 1


def test_latest_request_failure_not_cached(monkeypatch):
    """失败结果不进入缓存，下一次调用会重试"""
    calls = []

    def _get(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("boom")
        return _FakeResponse(_latest_payload(version_name="v9.9.9"))

    monkeypatch.setattr(update_module.httpx, "get", _get)

    with pytest.raises(MirrorChyanError, match="请求失败"):
        update_module._request_mirrorchyan_latest("dummy")

    assert update_module._request_mirrorchyan_latest("dummy")["code"] == 0
    assert len(calls) == 2


def test_latest_request_cache_is_per_cdk(monkeypatch):
    """不同 CDK 不共享缓存"""
    calls = []

    def _get(api, **kwargs):
        calls.append(api)
        cdk = "a" if "cdk=cdk-a" in api else "b"
        return _FakeResponse(_latest_payload(version_name=f"v9.9.{cdk}"))

    monkeypatch.setattr(update_module.httpx, "get", _get)

    first = update_module._request_mirrorchyan_latest("cdk-a")
    second = update_module._request_mirrorchyan_latest("cdk-b")

    assert first != second
    assert len(calls) == 2


def test_cdk_days_and_update_check_share_latest_request(monkeypatch):
    """启动时 CDK 天数与更新检查复用同一次 /latest 请求"""
    calls = []
    expired = int(time.time()) + 3 * 86400

    def _get(*args, **kwargs):
        calls.append(1)
        return _FakeResponse(
            _latest_payload(
                version_name="v9.9.9",
                url="https://example.com/a.zip",
                filesize=123,
                sha256="a" * 64,
                cdk_expired_time=expired,
            )
        )

    monkeypatch.setattr(update_module.httpx, "get", _get)

    assert get_cdk_remaining_days("dummy") == 3
    info = update_module.check_for_update("dummy")

    assert info is not None
    assert info.version == "9.9.9"
    assert len(calls) == 1


def test_manual_check_forces_refresh(monkeypatch):
    """手动检查强制刷新，自动检查仍允许使用缓存"""
    forces = []

    def _check(cdk, timeout=10, *, force=False):
        forces.append(force)

    monkeypatch.setattr(update_module, "check_for_update", _check)
    monkeypatch.setattr(config.user, "mirrorchyan_cdk", "dummy")

    assert update_manager.get_browser_download_url() is StatusCode.LATEST
    assert update_manager.get_browser_download_url(force=True) is StatusCode.LATEST
    assert forces == [False, True]


def _wait_until(predicate, timeout: float = 2.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return False


def test_check_latest_deduplicates_concurrent_checks(monkeypatch):
    """已有检查进行中时，重复检查直接跳过"""
    monkeypatch.setattr(config.user, "auto_update", True)
    manager = Update()
    started = threading.Event()
    release = threading.Event()
    duplicate_seen = threading.Event()
    forces = []

    original_info = update_module.logger.info

    def _info(msg, *args, **kwargs):
        if isinstance(msg, str) and "已有更新检查进行中" in msg:
            duplicate_seen.set()
        original_info(msg, *args, **kwargs)

    def _slow_get(*, force=False):
        forces.append(force)
        started.set()
        assert release.wait(2)
        return StatusCode.LATEST

    monkeypatch.setattr(update_module.logger, "info", _info)
    monkeypatch.setattr(manager, "get_browser_download_url", _slow_get)

    try:
        manager.check_latest()
        assert started.wait(2)

        manager.check_latest()
        assert duplicate_seen.wait(2)
    finally:
        release.set()

    assert _wait_until(lambda: not manager._checking)
    assert forces == [False]


def test_check_latest_releases_guard_after_completion(monkeypatch):
    """一次检查结束后，允许再次检查"""
    monkeypatch.setattr(config.user, "auto_update", True)
    manager = Update()
    calls = []

    def _get(*, force=False):
        calls.append(force)
        return StatusCode.LATEST

    monkeypatch.setattr(manager, "get_browser_download_url", _get)

    manager.check_latest()
    assert _wait_until(lambda: len(calls) == 1 and not manager._checking)

    manager.check_latest()
    assert _wait_until(lambda: len(calls) == 2 and not manager._checking)

    assert calls == [False, False]


def test_verify_downloaded_package_keeps_size_mismatch_for_restart(tmp_path):
    """大小不一致时保留文件，等待 restart 阶段弹窗确认"""
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(b"x")
    manager = Update()
    manager.file = str(local_zip)
    manager.file_size = 123
    manager.sha256 = ""

    assert manager._verify_downloaded_package(verify_sha=False) is True
    assert manager.size_mismatch is True
    assert local_zip.exists()


def test_verify_downloaded_package_size_mismatch_with_bad_sha_deletes(tmp_path):
    """仅下载流程中大小不一致且 SHA 失败时删除文件"""
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(b"x")
    manager = Update()
    manager.file = str(local_zip)
    manager.file_size = 123
    manager.sha256 = "0" * 64

    assert manager._verify_downloaded_package() is False
    assert manager.size_mismatch is True
    assert not local_zip.exists()


def test_verify_downloaded_package_accepts_size_match(tmp_path):
    """大小一致且未提供 SHA 时允许通过"""
    data = b"x" * 10
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(data)
    manager = Update()
    manager.file = str(local_zip)
    manager.file_size = len(data)
    manager.sha256 = ""

    assert manager._verify_downloaded_package() is True
    assert local_zip.exists()


def test_verify_downloaded_package_rejects_sha_mismatch(tmp_path):
    """SHA 不一致时删除文件"""
    data = b"x" * 10
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(data)
    manager = Update()
    manager.file = str(local_zip)
    manager.file_size = len(data)
    manager.sha256 = "0" * 64

    assert manager._verify_downloaded_package() is False
    assert not local_zip.exists()


def test_verify_downloaded_package_can_skip_sha(tmp_path):
    """更新重启流程可跳过预校验，交由 restart 保留继续解压确认"""
    data = b"x" * 10
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(data)
    manager = Update()
    manager.file = str(local_zip)
    manager.file_size = len(data)
    manager.sha256 = "0" * 64

    assert manager._verify_downloaded_package(verify_sha=False) is True
    assert local_zip.exists()


def test_download_update_zip_rejects_truncated_file(monkeypatch, tmp_path):
    """实际写入大小与 Content-Length 不一致时删除文件"""
    local_zip = tmp_path / "a.zip"
    manager = Update()
    manager.file = str(local_zip)

    class _Stream:
        def __init__(self):
            self.status_code = 200
            self.headers = {"content-length": "10"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def iter_bytes(self, chunk_size=65536):
            yield b"abc"

    monkeypatch.setattr(update_module.httpx, "stream", lambda *args, **kwargs: _Stream())
    monkeypatch.setattr(update_module, "download_zip_percentage_update", lambda *args, **kwargs: None)

    assert manager.download_update_zip("https://example.com/a.zip") is False
    assert not local_zip.exists()


class _FakeSignal:
    def __init__(self):
        self.payloads = []

    def emit(self, payload):
        self.payloads.append(payload)


def _fake_signal_manager():
    return SimpleNamespace(main=SimpleNamespace(message_box_requested=_FakeSignal()))


def test_local_package_sha_valid_reuses_without_download(tmp_path):
    """下载前本地包 SHA 校验通过时直接复用"""
    data = b"abc"
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(data)
    manager = Update()
    manager.file = str(local_zip)
    manager.file_size = 123
    manager.sha256 = hashlib.sha256(data).hexdigest()

    assert manager._check_local_package_before_download() is True
    assert manager.sha_verified is True
    assert manager.size_mismatch is False
    assert local_zip.exists()


def test_local_package_sha_invalid_emits_extract_confirm(monkeypatch, tmp_path):
    """下载前本地包 SHA 校验失败时提示继续解压，并保留文件"""
    signal_manager = _fake_signal_manager()
    monkeypatch.setattr(update_module, "signal_manager", signal_manager)
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(b"abc")
    manager = Update()
    manager.file = str(local_zip)
    manager.file_size = 3
    manager.sha256 = "0" * 64

    assert manager._check_local_package_before_download() is False
    assert manager.sha_verified is False
    assert local_zip.exists()

    payloads = signal_manager.main.message_box_requested.payloads
    assert len(payloads) == 1
    assert payloads[0].level is MessageBoxPayload.Level.QUESTION
    assert payloads[0].action is MessageBoxPayload.Action.EXTRACT_CONFIRM


def test_local_package_without_sha_defers_to_original_flow(tmp_path):
    """没有 SHA 时交回原有检测/下载流程"""
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(b"abc")
    manager = Update()
    manager.file = str(local_zip)
    manager.sha256 = ""

    assert manager._check_local_package_before_download() is None


def test_reset_verification_state_keeps_file(tmp_path):
    """取消解压时只清除校验状态，不删除文件"""
    local_zip = tmp_path / "a.zip"
    local_zip.write_bytes(b"abc")
    manager = Update()
    manager.file = str(local_zip)
    manager.sha_verified = True
    manager.size_mismatch = True

    manager.reset_verification_state()

    assert local_zip.exists()
    assert manager.sha_verified is False
    assert manager.size_mismatch is False
