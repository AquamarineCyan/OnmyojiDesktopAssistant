"""更新包处理逻辑的单元测试（不涉及真实下载）。

覆盖：
- GitHub 响应类解析与默认值
- SHA-256 规范化、文件摘要
- 本地包复用、解压、解压前校验
- `restart` 中的校验兜底与确认流程
- 下载线路分派（下载函数本身打桩）
"""

import hashlib
import zipfile
from types import SimpleNamespace

import pytest

from src.utils import update as update_module
from src.utils.config import UpdateDownload, config
from src.utils.message import MessageBoxPayload
from src.utils.update import (
    GitHubAssetResponse,
    GitHubReleaseResponse,
    StatusCode,
    Update,
    _file_sha256,
    _zip_file_name,
    normalize_sha256,
)

_DIGEST = "a" * 64


@pytest.fixture(autouse=True)
def no_config_save(monkeypatch):
    """避免测试触发配置写盘"""
    monkeypatch.setattr(config, "_save", lambda *args, **kwargs: None)


class _FakeHTTPResponse:
    def __init__(self, payload, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class _FakeSignal:
    def __init__(self):
        self.payloads = []

    def emit(self, payload):
        self.payloads.append(payload)


def _fake_signal_manager() -> SimpleNamespace:
    return SimpleNamespace(main=SimpleNamespace(message_box_requested=_FakeSignal()))


class _FakeRestart:
    def __init__(self):
        self.bat_name = None
        self.update_restarted = False

    def write_update_restart_bat(self, name: str):
        self.bat_name = name

    def app_restart(self, is_update: bool = False):
        self.update_restarted = is_update


def _release(tag_name: str = "v9.9.9", assets: list[dict] | None = None, **kwargs) -> dict:
    if assets is None:
        name = _zip_file_name(tag_name)
        assets = [
            {
                "name": name,
                "size": 321,
                "browser_download_url": f"https://example.com/{name}",
                "digest": f"sha256:{_DIGEST}",
            }
        ]
    return {"tag_name": tag_name, "body": "更新内容", "assets": assets, **kwargs}


def _make_manager(tmp_path, content: bytes = b"zip-bytes") -> Update:
    manager = Update()
    manager.file = str(tmp_path / "a.zip")
    (tmp_path / "a.zip").write_bytes(content)
    manager.file_size = len(content)
    manager.browser_download_url = "https://example.com/a.zip"
    manager.download_source = UpdateDownload.GITHUB
    return manager


class TestNormalizeSha256:
    def test_plain_digest_is_kept(self):
        assert normalize_sha256(_DIGEST) == _DIGEST

    def test_prefix_and_case_are_normalized(self):
        assert normalize_sha256(f"  SHA256: {'A' * 64}  ") == _DIGEST

    def test_other_algorithm_is_rejected(self):
        assert normalize_sha256(f"sha512:{_DIGEST}") == ""

    def test_invalid_length_is_rejected(self):
        assert normalize_sha256("abc") == ""

    @pytest.mark.parametrize("value", ["", None])
    def test_empty_value_returns_empty(self, value):
        assert normalize_sha256(value) == ""


class TestFileSha256:
    def test_matches_hashlib(self, tmp_path):
        file = tmp_path / "a.bin"
        file.write_bytes(b"abc")

        assert _file_sha256(str(file)) == hashlib.sha256(b"abc").hexdigest()


class TestGitHubAssetResponse:
    def test_full_fields(self):
        asset = GitHubAssetResponse.from_dict(
            {
                "name": "a.zip",
                "size": 321,
                "browser_download_url": "https://example.com/a.zip",
                "digest": f"sha256:{_DIGEST}",
            }
        )

        assert asset.name == "a.zip"
        assert asset.size == 321
        assert asset.browser_download_url == "https://example.com/a.zip"
        assert asset.digest == f"sha256:{_DIGEST}"

    def test_missing_fields_fall_back_to_defaults(self):
        asset = GitHubAssetResponse.from_dict({})

        assert asset.name == ""
        assert asset.size == 0
        assert asset.browser_download_url is None
        assert asset.digest == ""

    def test_empty_download_url_becomes_none(self):
        assert GitHubAssetResponse.from_dict({"browser_download_url": ""}).browser_download_url is None

    def test_non_dict_payload_returns_defaults(self):
        assert GitHubAssetResponse.from_dict(["bad"]) == GitHubAssetResponse()


class TestGitHubReleaseResponse:
    def test_full_fields(self):
        release = GitHubReleaseResponse.from_dict(_release())

        assert release.tag_name == "v9.9.9"
        assert release.body == "更新内容"
        assert release.draft is False
        assert release.prerelease is False
        assert len(release.assets) == 1
        assert release.assets[0].size == 321

    def test_missing_fields_fall_back_to_defaults(self):
        release = GitHubReleaseResponse.from_dict({})

        assert release.tag_name == ""
        assert release.body == ""
        assert release.draft is False
        assert release.prerelease is False
        assert release.assets == []

    def test_non_dict_assets_are_skipped(self):
        release = GitHubReleaseResponse.from_dict({"assets": ["bad", {"name": "a.zip"}]})

        assert [asset.name for asset in release.assets] == ["a.zip"]

    def test_non_dict_payload_returns_defaults(self):
        assert GitHubReleaseResponse.from_dict(None) == GitHubReleaseResponse()


class TestCheckLocalFile:
    def test_matching_size_is_reused(self, tmp_path):
        manager = _make_manager(tmp_path, b"abc")

        assert manager._check_local_file(manager.file, 3) is True
        assert manager._check_local_file(manager.file, 4) is False

    def test_missing_file_is_not_reused(self, tmp_path):
        manager = Update()

        assert manager._check_local_file(str(tmp_path / "missing.zip"), 0) is False

    def test_stat_error_is_not_reused(self, monkeypatch):
        manager = Update()
        monkeypatch.setattr(update_module.os.path, "exists", lambda path: True)

        def _raise(path):
            raise OSError("file locked")

        monkeypatch.setattr(update_module.os, "stat", _raise)

        assert manager._check_local_file("a.zip", 1) is False


class TestVerifyArchiveSha256:
    def test_matching_sha256_passes(self, tmp_path):
        manager = _make_manager(tmp_path, b"abc")
        manager.sha256 = hashlib.sha256(b"abc").hexdigest()

        assert manager.verify_archive_sha256() is True

    def test_mismatched_sha256_fails_and_reports(self, monkeypatch, tmp_path):
        errors, ui_errors = [], []
        monkeypatch.setattr(update_module.logger, "error", errors.append)
        monkeypatch.setattr(update_module.logger, "ui_error", ui_errors.append)
        manager = _make_manager(tmp_path, b"abc")
        manager.sha256 = "0" * 64

        assert manager.verify_archive_sha256() is False
        assert len(errors) == 1
        assert ui_errors == ["更新包 SHA-256 校验失败"]

    def test_missing_sha256_skips_check(self, tmp_path):
        manager = _make_manager(tmp_path, b"abc")
        manager.sha256 = ""

        assert manager.verify_archive_sha256() is True

    def test_missing_file_skips_check(self, tmp_path):
        manager = Update()
        manager.file = str(tmp_path / "missing.zip")
        manager.sha256 = "0" * 64

        assert manager.verify_archive_sha256() is True

    def test_unreadable_file_skips_check(self, monkeypatch, tmp_path):
        warnings = []
        monkeypatch.setattr(update_module.logger, "ui_warn", warnings.append)

        def _raise(path):
            raise OSError("file locked")

        monkeypatch.setattr(update_module, "_file_sha256", _raise)
        manager = _make_manager(tmp_path, b"abc")
        manager.sha256 = "0" * 64

        assert manager.verify_archive_sha256() is True
        assert len(warnings) == 1


class TestUnzipHandle:
    def test_extracts_files_and_removes_package(self, monkeypatch, tmp_path):
        zip_path = tmp_path / "a.zip"
        with zipfile.ZipFile(zip_path, "w") as archive:
            archive.writestr("hello.txt", "hi")

        monkeypatch.setattr(update_module, "APP_PATH", tmp_path)
        manager = Update()
        manager.file = str(zip_path)

        assert manager._unzip_handle() is True
        assert (tmp_path / "zip_files" / "hello.txt").read_text(encoding="utf-8") == "hi"
        assert not zip_path.exists()

    def test_invalid_zip_is_rejected(self, monkeypatch, tmp_path):
        zip_path = tmp_path / "a.zip"
        zip_path.write_bytes(b"not a zip")

        monkeypatch.setattr(update_module, "APP_PATH", tmp_path)
        manager = Update()
        manager.file = str(zip_path)

        assert manager._unzip_handle() is False
        assert zip_path.exists()


class TestCheckDownloadZipDispatch:
    def test_local_package_is_reused_without_download(self, monkeypatch, tmp_path):
        manager = _make_manager(tmp_path, b"abc")
        monkeypatch.setattr(config.user, "update_download", UpdateDownload.GITHUB)
        monkeypatch.setattr(manager, "download_update_zip", lambda url: pytest.fail("不应下载"))
        monkeypatch.setattr(manager, "_download_mirrorchyan", lambda: pytest.fail("不应下载"))
        monkeypatch.setattr(manager, "_download_by_mirror_stations", lambda: pytest.fail("不应下载"))

        assert manager._check_download_zip() is True

    def test_github_route_downloads_from_github_url(self, monkeypatch, tmp_path):
        manager = _make_manager(tmp_path)
        manager.file = str(tmp_path / "missing.zip")
        monkeypatch.setattr(config.user, "update_download", UpdateDownload.GITHUB)
        calls = []
        monkeypatch.setattr(manager, "download_update_zip", lambda url: calls.append(url) or True)

        assert manager._check_download_zip() is True
        assert calls == ["https://example.com/a.zip"]

    def test_mirrorchyan_route_delegates(self, monkeypatch, tmp_path):
        manager = _make_manager(tmp_path)
        manager.file = str(tmp_path / "missing.zip")
        monkeypatch.setattr(config.user, "update_download", UpdateDownload.MIRRORCHYAN)
        monkeypatch.setattr(manager, "_download_mirrorchyan", lambda: True)

        assert manager._check_download_zip() is True

    def test_mirror_station_route_uses_stations(self, monkeypatch, tmp_path):
        manager = _make_manager(tmp_path)
        manager.file = str(tmp_path / "missing.zip")
        monkeypatch.setattr(config.user, "update_download", UpdateDownload.MIRROR)
        monkeypatch.setattr(manager, "_download_by_mirror_stations", lambda: True)

        assert manager._check_download_zip() is True

    def test_unknown_route_fails(self, monkeypatch, tmp_path):
        manager = _make_manager(tmp_path)
        manager.file = str(tmp_path / "missing.zip")
        monkeypatch.setattr(config.user, "update_download", "unknown")
        monkeypatch.setattr(update_module.logger, "ui_error", lambda *args: None)

        assert manager._check_download_zip() is False


class TestGitHubUpdateCheck:
    @pytest.fixture
    def manager(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config.user, "update_download", UpdateDownload.GITHUB)
        manager = Update()
        monkeypatch.setattr(manager, "_write_update_record", lambda record: None)
        return manager

    def test_new_version_fills_package_info(self, manager, monkeypatch):
        monkeypatch.setattr(
            manager, "_fetch_releases", lambda per_page=10: ([GitHubReleaseResponse.from_dict(_release())], None)
        )

        assert manager.get_browser_download_url() is StatusCode.NEW_VERSION
        assert manager.new_version == "9.9.9"
        assert manager.new_version_info == "更新内容"
        assert manager.file == _zip_file_name("9.9.9")
        assert manager.file_size == 321
        assert manager.sha256 == _DIGEST
        assert manager.download_source is UpdateDownload.GITHUB
        assert manager.version_history == [{"version": "9.9.9", "body": "更新内容"}]

    def test_missing_digest_leaves_sha256_empty(self, manager, monkeypatch):
        asset = {
            "name": _zip_file_name("9.9.9"),
            "size": 321,
            "browser_download_url": f"https://example.com/{_zip_file_name('9.9.9')}",
        }
        monkeypatch.setattr(
            manager,
            "_fetch_releases",
            lambda per_page=10: ([GitHubReleaseResponse.from_dict(_release(assets=[asset]))], None),
        )

        assert manager.get_browser_download_url() is StatusCode.NEW_VERSION
        assert manager.sha256 == ""

    def test_older_release_is_latest(self, manager, monkeypatch):
        monkeypatch.setattr(
            manager,
            "_fetch_releases",
            lambda per_page=10: ([GitHubReleaseResponse.from_dict(_release("v0.0.1"))], None),
        )

        assert manager.get_browser_download_url() is StatusCode.LATEST

    def test_release_without_assets_is_latest(self, manager, monkeypatch):
        monkeypatch.setattr(
            manager,
            "_fetch_releases",
            lambda per_page=10: ([GitHubReleaseResponse.from_dict(_release(assets=[]))], None),
        )

        assert manager.get_browser_download_url() is StatusCode.LATEST

    def test_missing_package_asset_returns_zip_error(self, manager, monkeypatch):
        release = _release(assets=[{"name": "other.zip", "size": 1, "browser_download_url": "https://example.com/x"}])
        monkeypatch.setattr(
            manager,
            "_fetch_releases",
            lambda per_page=10: ([GitHubReleaseResponse.from_dict(release)], None),
        )

        assert manager.get_browser_download_url() is StatusCode.ZIP_ERROR


class TestFetchReleases:
    def test_filters_draft_prerelease_and_non_dict(self, monkeypatch):
        payload = [
            {"tag_name": "v9.9.9", "draft": True},
            {"tag_name": "v9.9.8", "prerelease": True},
            {"tag_name": "v9.9.7"},
            "bad",
        ]
        monkeypatch.setattr(update_module.httpx, "get", lambda *args, **kwargs: _FakeHTTPResponse(payload))

        releases, status = Update()._fetch_releases()

        assert status is None
        assert [release.tag_name for release in releases] == ["v9.9.7"]

    def test_not_found_returns_connect_error(self, monkeypatch):
        monkeypatch.setattr(update_module.httpx, "get", lambda *args, **kwargs: _FakeHTTPResponse([], 404))

        releases, status = Update()._fetch_releases()

        assert releases is None
        assert status is StatusCode.CONNECT_ERROR

    def test_server_error_returns_releases_error(self, monkeypatch):
        monkeypatch.setattr(update_module.httpx, "get", lambda *args, **kwargs: _FakeHTTPResponse([], 500))

        releases, status = Update()._fetch_releases()

        assert releases is None
        assert status is StatusCode.RELEASES_ERROR

    def test_non_list_payload_returns_releases_error(self, monkeypatch):
        monkeypatch.setattr(update_module.httpx, "get", lambda *args, **kwargs: _FakeHTTPResponse({"bad": 1}))

        releases, status = Update()._fetch_releases()

        assert releases is None
        assert status is StatusCode.RELEASES_ERROR

    def test_request_exception_returns_connect_error(self, monkeypatch):
        def _raise(*args, **kwargs):
            raise RuntimeError("network down")

        monkeypatch.setattr(update_module.httpx, "get", _raise)
        monkeypatch.setattr(update_module.logger, "ui_warn", lambda *args: None)

        releases, status = Update()._fetch_releases()

        assert releases is None
        assert status is StatusCode.CONNECT_ERROR


class TestRestartVerification:
    def _prepare(self, tmp_path, sha256: str) -> Update:
        manager = _make_manager(tmp_path, b"abc")
        manager.sha256 = sha256
        manager.zip_files_path = tmp_path / "zip_files"
        return manager

    def test_bad_sha256_asks_for_confirmation_without_unzip(self, monkeypatch, tmp_path):
        signal_manager = _fake_signal_manager()
        monkeypatch.setattr(update_module, "signal_manager", signal_manager)
        manager = self._prepare(tmp_path, "0" * 64)
        unzip_calls = []
        monkeypatch.setattr(manager, "_unzip_handle", lambda: unzip_calls.append(True) or True)

        Update.restart.__wrapped__(manager)

        assert unzip_calls == []
        payloads = signal_manager.main.message_box_requested.payloads
        assert len(payloads) == 1
        assert payloads[0].level is MessageBoxPayload.Level.QUESTION
        assert payloads[0].action is MessageBoxPayload.Action.EXTRACT_CONFIRM

    def test_valid_sha256_proceeds_to_unzip_and_restart(self, monkeypatch, tmp_path):
        monkeypatch.setattr(update_module, "signal_manager", _fake_signal_manager())
        created = []

        def _restart_factory():
            instance = _FakeRestart()
            created.append(instance)
            return instance

        monkeypatch.setattr(update_module, "Restart", _restart_factory)
        manager = self._prepare(tmp_path, hashlib.sha256(b"abc").hexdigest())
        monkeypatch.setattr(manager, "_unzip_handle", lambda: True)

        Update.restart.__wrapped__(manager)

        assert len(created) == 1
        assert created[0].bat_name == "zip_files"
        assert created[0].update_restarted is True

    def test_size_mismatch_asks_for_confirmation_even_if_sha_valid(self, monkeypatch, tmp_path):
        signal_manager = _fake_signal_manager()
        monkeypatch.setattr(update_module, "signal_manager", signal_manager)
        manager = self._prepare(tmp_path, hashlib.sha256(b"abc").hexdigest())
        manager.size_mismatch = True
        unzip_calls = []
        monkeypatch.setattr(manager, "_unzip_handle", lambda: unzip_calls.append(True) or True)

        Update.restart.__wrapped__(manager)

        assert unzip_calls == []
        payloads = signal_manager.main.message_box_requested.payloads
        assert len(payloads) == 1
        assert payloads[0].level is MessageBoxPayload.Level.QUESTION
        assert payloads[0].action is MessageBoxPayload.Action.EXTRACT_CONFIRM

    def test_force_skips_sha256_verification(self, monkeypatch, tmp_path):
        monkeypatch.setattr(update_module, "signal_manager", _fake_signal_manager())
        monkeypatch.setattr(update_module, "Restart", _FakeRestart)
        manager = self._prepare(tmp_path, "0" * 64)
        monkeypatch.setattr(manager, "verify_archive_sha256", lambda: pytest.fail("force 不应校验"))
        monkeypatch.setattr(manager, "_unzip_handle", lambda: True)

        Update.restart.__wrapped__(manager, force=True)

    def test_preverified_sha_skips_second_check(self, monkeypatch, tmp_path):
        """本地包已校验通过时，重启阶段不再重复计算 SHA"""
        monkeypatch.setattr(update_module, "Restart", _FakeRestart)
        manager = self._prepare(tmp_path, "0" * 64)
        manager.sha_verified = True
        manager.size_mismatch = False
        monkeypatch.setattr(manager, "verify_archive_sha256", lambda: pytest.fail("不应重复校验"))
        monkeypatch.setattr(manager, "_unzip_handle", lambda: True)

        Update.restart.__wrapped__(manager)

    def test_unzip_failure_emits_error_and_skips_restart(self, monkeypatch, tmp_path):
        signal_manager = _fake_signal_manager()
        monkeypatch.setattr(update_module, "signal_manager", signal_manager)
        monkeypatch.setattr(update_module, "Restart", lambda: pytest.fail("解压失败不应启动重启"))
        manager = self._prepare(tmp_path, hashlib.sha256(b"abc").hexdigest())
        monkeypatch.setattr(manager, "_unzip_handle", lambda: False)

        Update.restart.__wrapped__(manager)

        payloads = signal_manager.main.message_box_requested.payloads
        assert len(payloads) == 1
        assert payloads[0].level is MessageBoxPayload.Level.ERROR
        assert "解压" in payloads[0].content
