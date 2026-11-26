import hashlib
import json
import math
import os
import threading
import time
import zipfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

import httpx
from packaging.version import Version

from .application import APP_NAME, APP_PATH, UPDATE_INFO_FILE, USER_DATA_DIR_PATH, VERSION, Connect
from .config import UpdateDownload, config
from .decorator import run_in_thread
from .log import logger
from .message import MessageBoxPayload
from .restart import Restart
from .signals import signal_manager
from .toast import toast


class StatusCode(Enum):
    LATEST = 1
    NEW_VERSION = 2
    CONNECT_ERROR = 3
    RELEASES_ERROR = 4
    ZIP_ERROR = 5
    MIRRORCHYAN_ERROR = 6


def compare_versions(new_version: str, current_version: str) -> bool:
    try:
        return Version(new_version) > Version(current_version)
    except Exception:
        logger.ui_warn(f"版本号格式异常: {new_version} vs {current_version}")
        return False


class MirrorChyanError(RuntimeError):
    """MirrorChyan 版本检测异常基类"""

    code: int | None = None
    """接口错误码，网络异常时为 None"""
    msg: str = ""
    """面向用户的错误提示"""


# CDK 错误码 → 提示文本
_CDK_ERROR_MESSAGES = {
    7001: "Mirror酱 CDK 已过期",
    7002: "Mirror酱 CDK 错误",
    7003: "Mirror酱 CDK 今日下载次数已达上限",
    7004: "Mirror酱 CDK 类型和待下载的资源不匹配",
    7005: "Mirror酱 CDK 已被封禁",
}


@dataclass
class UpdateInfo:
    """标准化的更新信息"""

    source: str  # "MirrorChyan"
    url: str  # 下载链接
    file_name: str  # 文件名
    version: str  # 远程版本号（不带 v）
    file_size: int = 0  # 文件大小
    sha256: str = ""  # 下载文件 SHA-256
    release_note: str = ""  # 更新日志（Markdown）


@dataclass
class MirrorChyanLatestResponse:
    """Mirror酱 `/latest` 接口响应

    文档: https://github.com/MirrorChyan/docs
    """

    @dataclass
    class Data:
        """`data` 字段：仅 `version_name` 一定会返回，其余字段均可能缺失

        - `url`：仅在有可用更新且 CDK 有效时返回；
        - `filesize` / `sha256` / `release_note`：随更新包返回，可能为空；
        - `cdk_expired_time`：未使用 CDK 或接口未返回时缺省。
        """

        version_name: str = ""
        """最新版本号，可能带 v 前缀"""
        url: str | None = None
        """更新包下载链接（可选）"""
        filesize: int = 0
        """更新包大小（字节，可选）"""
        sha256: str = ""
        """更新包 SHA-256（可选）"""
        release_note: str = ""
        """更新日志 Markdown（可选）"""
        cdk_expired_time: int = 0
        """CDK 到期时间戳（可选，0 表示未返回）"""

    code: int = 0
    """接口状态码，0 表示成功"""
    msg: str = ""
    """接口提示信息，成功时通常为空"""
    data: "MirrorChyanLatestResponse.Data" = field(default_factory=lambda: MirrorChyanLatestResponse.Data())
    """接口数据"""

    @classmethod
    def from_dict(cls, payload: dict) -> "MirrorChyanLatestResponse":
        """从接口 JSON 构建响应对象，字段缺失或类型异常时回退默认值"""
        if not isinstance(payload, dict):
            return cls()
        raw_data = payload.get("data")
        if not isinstance(raw_data, dict):
            raw_data = {}

        return cls(
            code=_as_int(payload.get("code")),
            msg=_as_str(payload.get("msg")),
            data=cls.Data(
                version_name=_as_str(raw_data.get("version_name")),
                url=_as_str(raw_data.get("url")) or None,
                filesize=_as_int(raw_data.get("filesize")),
                sha256=_as_str(raw_data.get("sha256")),
                release_note=_as_str(raw_data.get("release_note")),
                cdk_expired_time=_as_int(raw_data.get("cdk_expired_time")),
            ),
        )


@dataclass
class GitHubAssetResponse:
    """GitHub Release 资产（仅保留下载所需字段）

    文档: https://docs.github.com/en/rest/releases/assets
    """

    name: str = ""
    """资产文件名"""
    size: int = 0
    """资产大小（字节），缺失时为 0"""
    browser_download_url: str | None = None
    """资产下载链接，缺失时为 None"""
    digest: str = ""
    """资产摘要（形如 `sha256:...`），缺失时为空串"""

    @classmethod
    def from_dict(cls, payload: dict) -> "GitHubAssetResponse":
        """从接口 JSON 构建资产对象，字段缺失或类型异常时回退默认值"""
        if not isinstance(payload, dict):
            return cls()

        return cls(
            name=_as_str(payload.get("name")),
            size=_as_int(payload.get("size")),
            browser_download_url=_as_str(payload.get("browser_download_url")) or None,
            digest=_as_str(payload.get("digest")),
        )


@dataclass
class GitHubReleaseResponse:
    """GitHub `/releases` 接口的单条发布记录（仅保留更新检查所需字段）

    文档: https://docs.github.com/en/rest/releases/releases
    """

    tag_name: str = ""
    """发布标签，通常带 v 前缀"""
    body: str = ""
    """发布说明 Markdown，可能为空"""
    draft: bool = False
    """是否草稿，缺失时视为正式发布"""
    prerelease: bool = False
    """是否预发布，缺失时视为正式发布"""
    assets: list[GitHubAssetResponse] = field(default_factory=list)
    """发布资产列表，缺失时为空列表"""

    @classmethod
    def from_dict(cls, payload: dict) -> "GitHubReleaseResponse":
        """从接口 JSON 构建发布对象，字段缺失或类型异常时回退默认值"""
        if not isinstance(payload, dict):
            return cls()
        raw_assets = payload.get("assets")
        if not isinstance(raw_assets, list):
            raw_assets = []

        assets: list[GitHubAssetResponse] = []
        for asset in raw_assets:
            if isinstance(asset, dict):
                assets.append(GitHubAssetResponse.from_dict(asset))

        return cls(
            tag_name=_as_str(payload.get("tag_name")),
            body=_as_str(payload.get("body")),
            draft=bool(payload.get("draft")),
            prerelease=bool(payload.get("prerelease")),
            assets=assets,
        )


def _as_int(value) -> int:
    """尽力将接口字段转为整数，非法值回退 0"""
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _as_str(value) -> str:
    """尽力将接口字段转为字符串，缺失时回退空串"""
    return "" if value is None else str(value)


def normalize_sha256(value: str) -> str:
    """将分发站返回的摘要规范化为纯 SHA-256 十六进制字符串"""
    if not value:
        return ""
    normalized = value.strip().lower()
    if ":" in normalized:
        algorithm, digest = normalized.split(":", 1)
        if algorithm != "sha256":
            return ""
        normalized = digest.strip()
    return normalized if len(normalized) == 64 else ""


def _file_sha256(file: str) -> str:
    """计算文件的 SHA-256 十六进制摘要"""
    hasher = hashlib.sha256()
    with open(file, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)  # 1MB
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def _parse_error(resp_status: int, data: dict) -> MirrorChyanError:
    """将响应转化为带提示的异常"""
    code = data.get("code", resp_status)
    msg = data.get("msg", "unknown error")
    if code in _CDK_ERROR_MESSAGES:
        msg = _CDK_ERROR_MESSAGES[code]
    err = MirrorChyanError(f"Mirror酱 API (code={code}): {msg}")
    err.code = code
    err.msg = msg
    return err


def _strip_v(version: str) -> str:
    """去除版本号前缀 v"""
    return version.removeprefix("v")


def _zip_file_name(version: str) -> str:
    """更新包文件名模板（与 GitHub release 资产命名一致）"""
    return f"{APP_NAME}-{_strip_v(version)}.zip"


def _latest_api(cdk: str) -> str:
    """构造查询最新版本接口地址"""
    return (
        f"{Connect.MirrorChyan.api}/{Connect.MirrorChyan.resource}/latest"
        f"?cdk={cdk}&user_agent={Connect.MirrorChyan.user_agent}&os=win&arch=x64&channel=stable"
    )


def _mask_cdk(api: str, cdk: str) -> str:
    """日志中隐藏 CDK 明文"""
    return api.replace(cdk, "***") if cdk else api


def _format_expire(expired_time: int) -> str:
    return datetime.fromtimestamp(expired_time, tz=UTC).astimezone().strftime("%Y-%m-%d")


_MIRRORCHYAN_LATEST_TTL = 120.0
"""Mirror酱 `/latest` 响应缓存有效期（秒）"""

_mirrorchyan_latest_lock = threading.Lock()
_mirrorchyan_latest_cache: tuple[str, float, dict] | None = None
"""缓存项：(CDK, 获取时的 monotonic 时间, 原始响应)"""

_mirrorchyan_latest_inflight: dict[str, threading.Event] = {}
"""正在进行的请求，用于合并同一 CDK 的并发调用"""


def _mirrorchyan_latest_cache_valid(cdk: str, now: float) -> bool:
    """判断 `/latest` 缓存是否仍然有效"""
    cache = _mirrorchyan_latest_cache
    return bool(cache and cache[0] == cdk and now - cache[1] < _MIRRORCHYAN_LATEST_TTL)


def _do_request_mirrorchyan_latest(cdk: str, timeout: int = 10) -> dict:
    """实际请求 Mirror酱 `/latest`，并把原始响应写入日志"""
    api = _latest_api(cdk)
    logger.debug(f"Mirror酱 API: {_mask_cdk(api, cdk)}")
    try:
        resp = httpx.get(api, timeout=timeout)
        data = resp.json()
    except Exception as e:
        raise MirrorChyanError(f"Mirror酱 请求失败: {e}") from e

    logger.info(f"Mirror酱 原始响应({resp.status_code}): {json.dumps(data, ensure_ascii=False)}")

    if not isinstance(data, dict):
        raise MirrorChyanError("Mirror酱 接口返回格式异常")
    if resp.status_code != 200 or data.get("code") != 0:
        raise _parse_error(resp.status_code, data)

    return data


def _request_mirrorchyan_latest(cdk: str, timeout: int = 10, *, force: bool = False) -> dict:
    """请求 Mirror酱 `/latest`，同一 CDK 的并发调用共享结果

    Args:
        cdk: Mirror酱 CDK。
        timeout: 单次请求超时。
        force: 为 `True` 时绕过缓存；若已有请求在进行，仍等待并复用该请求。

    Returns:
        接口原始 JSON。

    Raises:
        MirrorChyanError: 请求失败或接口返回错误码。
    """
    global _mirrorchyan_latest_cache

    now = time.monotonic()
    with _mirrorchyan_latest_lock:
        if not force and _mirrorchyan_latest_cache_valid(cdk, now):
            logger.debug("Mirror酱 /latest 命中缓存")
            return _mirrorchyan_latest_cache[2]

        event = _mirrorchyan_latest_inflight.get(cdk)
        if event is None:
            event = threading.Event()
            _mirrorchyan_latest_inflight[cdk] = event
            owner = True
        else:
            owner = False

    if not owner:
        if not event.wait(timeout + 1):
            raise MirrorChyanError("Mirror酱 请求等待超时")
        with _mirrorchyan_latest_lock:
            if _mirrorchyan_latest_cache_valid(cdk, time.monotonic()):
                return _mirrorchyan_latest_cache[2]
        # 上一次请求失败，重试一次
        return _request_mirrorchyan_latest(cdk, timeout, force=True)

    try:
        data = _do_request_mirrorchyan_latest(cdk, timeout)
        with _mirrorchyan_latest_lock:
            _mirrorchyan_latest_cache = (cdk, time.monotonic(), data)
        return data
    finally:
        with _mirrorchyan_latest_lock:
            _mirrorchyan_latest_inflight.pop(cdk, None)
        event.set()


def _check_mirrorchyan(cdk: str, current_version: str, timeout: int = 10, *, force: bool = False) -> UpdateInfo | None:
    """通过 Mirror酱 分发站检查更新。

    Args:
        cdk: Mirror酱 CDK。
        current_version: 当前版本号。
        timeout: 单次请求超时。
        force: 为 `True` 时绕过 `/latest` 缓存，强制获取最新结果。

    Returns:
        有新版本返回 UpdateInfo；已是最新返回 None。
    Raises:
        MirrorChyanError: 检测失败。
    """
    latest = MirrorChyanLatestResponse.from_dict(_request_mirrorchyan_latest(cdk, timeout, force=force))

    # 格式化打印有效期
    if latest.data.cdk_expired_time:
        logger.info(f"Mirror酱 CDK 有效期至 {_format_expire(latest.data.cdk_expired_time)}")

    version_name = _strip_v(latest.data.version_name)
    if not version_name or not compare_versions(version_name, current_version):
        logger.info(f"Mirror酱 已是最新版本: {current_version}")
        return None

    # 有新版本时才返回 url 字段（最新版本时 API 不返回）
    if not latest.data.url:
        raise MirrorChyanError("Mirror酱 未返回下载链接")

    return UpdateInfo(
        source="MirrorChyan",
        url=latest.data.url,
        file_name=_zip_file_name(version_name),
        version=version_name,
        file_size=latest.data.filesize,
        sha256=normalize_sha256(latest.data.sha256),
        release_note=latest.data.release_note,
    )


def get_cdk_remaining_days(cdk: str, timeout: int = 10) -> int | None:
    """查询 Mirror酱 CDK 剩余天数。

    Args:
        cdk: Mirror酱 CDK 密钥。
        timeout: 单次请求超时。

    Returns:
        剩余天数（向上取整，已过期为负数）；接口未返回有效期时返回 None。

    Raises:
        MirrorChyanError: 检测失败（CDK 无效、接口异常等）。
    """
    if not cdk:
        return None

    latest = MirrorChyanLatestResponse.from_dict(_request_mirrorchyan_latest(cdk, timeout))
    if not latest.data.cdk_expired_time:
        return None

    return math.ceil((latest.data.cdk_expired_time - time.time()) / 86400)


def check_for_update(cdk: str, timeout: int = 10, *, force: bool = False) -> UpdateInfo | None:
    """Mirror酱 独立线路：检查更新。

    Args:
        cdk: Mirror酱 CDK 密钥（必须，用于配额分发）。
        timeout: 单次请求超时。
        force: 为 `True` 时绕过 `/latest` 缓存，强制获取最新结果。

    Returns:
        UpdateInfo 若有新版本；None 若已最新或无需更新。

    Raises:
        MirrorChyanError: 检测失败（CDK 无效、接口异常等）。
    """
    if not cdk:
        raise MirrorChyanError("未填写 Mirror酱 CDK")
    logger.info(f"Mirror酱 检查更新: current={VERSION}")
    return _check_mirrorchyan(cdk, VERSION, timeout, force=force)


class Update:
    """更新升级"""

    def __init__(self):
        self.new_version: str = None
        """新版本版本号"""
        self.new_version_info: str = None
        """新版本更新内容"""
        self.version_history: list[dict] = []
        """版本历史（新版本在前），用于展示多版本更新内容"""
        self.browser_download_url: str = None
        """更新包下载链接"""
        self.download_source: UpdateDownload | None = None
        """当前下载链接的来源线路，避免弹窗内切换线路后误用"""
        self.file: str = None
        """下载文件名称"""
        self.file_size: int = None
        """下载文件大小"""
        self.sha256: str = ""
        """更新包 SHA-256（空串表示接口未提供，跳过校验）"""
        self.sha_verified: bool = False
        """当前更新包是否已经通过 SHA-256 校验"""
        self.size_mismatch: bool = False
        """下载包实际大小与服务端声明大小是否不一致"""
        self.zip_path: str = None
        """更新包路径"""
        self.error_message: str = None
        """镜像线路检查失败时的用户提示"""
        self._check_lock = threading.Lock()
        """保护检查运行状态"""
        self._checking = False
        """是否已有更新检查在进行"""

    def _fetch_releases(self, per_page: int = 10) -> tuple[list[GitHubReleaseResponse] | None, StatusCode | None]:
        """拉取并过滤 GitHub 正式发布列表（去除草稿与预发布）。

        返回:
            (发布列表, None) 成功，列表可能为空，由调用方决策；
            (None, StatusCode) 失败时的状态码。
        """
        _api_url = f"{Connect.releases_api}?per_page={per_page}"
        logger.info(f"api_url: {_api_url}")
        try:
            response = httpx.get(_api_url, headers=Connect.headers, follow_redirects=True)
            logger.info(f"api.status_code: {response.status_code}")
            if response.status_code == 404:
                return None, StatusCode.CONNECT_ERROR
            if response.status_code != 200:
                return None, StatusCode.RELEASES_ERROR
            data = response.json()
        except Exception as e:
            logger.ui_warn(f"获取更新信息失败: {e}")
            return None, StatusCode.CONNECT_ERROR
        if not isinstance(data, list):
            return None, StatusCode.RELEASES_ERROR
        releases: list[GitHubReleaseResponse] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            release = GitHubReleaseResponse.from_dict(item)
            if release.draft or release.prerelease:
                continue
            releases.append(release)
        return releases, None

    @staticmethod
    def _build_version_history(releases: list[GitHubReleaseResponse]) -> list[dict]:
        """从发布列表构建版本历史（新版本在前，仅保留 v 前缀 tag 并去除前缀）"""
        history = []
        for item in releases:
            if not item.tag_name or not item.tag_name.startswith("v"):
                continue
            history.append({"version": _strip_v(item.tag_name), "body": item.body})
        return history

    def get_browser_download_url(self, *, force: bool = False) -> StatusCode:
        """获取更新包地址

        Args:
            force: 为 `True` 时跳过镜像线路的 `/latest` 缓存。

        Returns:
            StatusCode: 状态码
        """
        if config.user.update_download == UpdateDownload.MIRRORCHYAN:
            return self._get_mirrorchyan_download_url(force=force)

        response_list, status = self._fetch_releases()
        if status is not None:
            return status
        if not response_list:
            return StatusCode.RELEASES_ERROR

        # 构建版本历史
        self.version_history = self._build_version_history(response_list)
        # 检查更新成功后同步本地更新记录缓存
        self._write_update_record(self.version_history)
        logger.info(f"version_history: {[item['version'] for item in self.version_history]}")

        _latest = response_list[0]
        if not _latest.tag_name or not _latest.tag_name.startswith("v"):
            return StatusCode.RELEASES_ERROR

        self.new_version = _strip_v(_latest.tag_name)  # 去除“v”前缀
        logger.info(f"new_version:{self.new_version}")

        _assets_list = _latest.assets
        if len(_assets_list) == 0:
            # 新版本tag已创建但更新包尚未上传，视为无可用更新
            logger.info("新版本tag已创建，但更新包尚未上传")
            return StatusCode.LATEST

        if not compare_versions(self.new_version, VERSION):
            return StatusCode.LATEST

        _info: str = _latest.body
        logger.info(_info)
        self.new_version_info = _info

        for item in _assets_list:
            logger.info(item)
            if item.name == _zip_file_name(self.new_version):
                self.browser_download_url = item.browser_download_url
                if self.browser_download_url is None:
                    logger.ui_error("更新包下载链接丢失")
                    return StatusCode.ZIP_ERROR
                logger.info(f"更新包下载链接: {self.browser_download_url}")
                self.download_source = UpdateDownload.GITHUB
                self.file = self.browser_download_url.split("/")[-1]
                logger.info(f"file:{self.file}")
                self.file_size = item.size
                if not self.file_size:
                    logger.ui_error("更新包大小缺失")
                    return StatusCode.ZIP_ERROR
                logger.info(f"file_size:{self.file_size}")
                self.sha256 = normalize_sha256(item.digest)
                self.sha_verified = False
                self.size_mismatch = False
                if not self.sha256:
                    logger.warning("GitHub 未返回更新包 SHA-256，将跳过校验")
                return StatusCode.NEW_VERSION

        return StatusCode.ZIP_ERROR

    def _get_mirrorchyan_download_url(self, *, force: bool = False) -> StatusCode:
        """Mirror酱 线路：仅通过 Mirror酱接口检查更新

        Args:
            force: 为 `True` 时跳过 `/latest` 缓存。

        Returns:
            StatusCode: 状态码
        """
        cdk = config.user.mirrorchyan_cdk
        if not cdk:
            self.error_message = "未填写 Mirror酱 CDK，请前往设置页填写"
            return StatusCode.MIRRORCHYAN_ERROR

        try:
            info = check_for_update(cdk, force=force)
        except MirrorChyanError as e:
            self.error_message = e.msg or str(e)
            return StatusCode.MIRRORCHYAN_ERROR if e.code is not None else StatusCode.CONNECT_ERROR

        if info is None:
            logger.info(f"Mirror酱 已是最新版本: {VERSION}")
            return StatusCode.LATEST

        # 回填版本信息，供更新弹窗与下载复用，避免重复请求接口
        self.new_version = info.version
        self.new_version_info = info.release_note
        # 仅更新内存中的历史，不覆盖 update_info.json 的 GitHub 多版本记录
        self.version_history = [{"version": info.version, "body": info.release_note}]
        self.browser_download_url = info.url
        self.download_source = UpdateDownload.MIRRORCHYAN
        self.file = info.file_name
        self.file_size = info.file_size
        self.sha256 = info.sha256
        self.sha_verified = False
        self.size_mismatch = False
        return StatusCode.NEW_VERSION

    def _check_local_file(self, file: str, expected_size: int) -> bool:
        """校验本地更新包大小是否与服务端一致"""
        try:
            return bool(os.path.exists(file) and os.stat(file).st_size == expected_size)
        except OSError:
            return False

    def _check_download_zip(self):
        if self._check_local_file(self.file, self.file_size):
            logger.ui("检测到本地存在新版本更新包")
            return True

        logger.ui("即将开始下载新版本更新包")

        match config.user.update_download:
            case UpdateDownload.GITHUB:
                return self.download_update_zip(self.browser_download_url)

            case UpdateDownload.MIRRORCHYAN:
                return self._download_mirrorchyan()

            case UpdateDownload.MIRROR:
                if self.download_source != UpdateDownload.GITHUB:
                    # 镜像站需要 GitHub 资源路径，来自 Mirror酱 的完整地址无法拼接
                    logger.ui_warn("当前更新包来自 Mirror酱，无法使用镜像站加速，改为直接下载")
                    return self.download_update_zip(self.browser_download_url)
                return self._download_by_mirror_stations()

            case _:
                logger.ui_error("未知下载线路，请前往设置页检查")
                return False

    def _download_by_mirror_stations(self) -> bool:
        """通过镜像站下载更新包"""
        # 检测各镜像站点延迟
        delay_dict = {}
        for url in Connect.mirror_station:
            try:
                r = httpx.get(url, headers=Connect.headers)
                delay_ms = round(r.elapsed.total_seconds() * 1000, 2)
                delay_dict[url] = delay_ms
                logger.ui(f"站点：{url}\n延迟: {delay_ms} 毫秒")
            except Exception as e:
                logger.ui_warn(f"访问站点 {url} 失败: {e}")
                delay_dict[url] = float("inf")
        sorted_urls = sorted(delay_dict, key=delay_dict.get)

        # 补全下载链接
        for url in sorted_urls:
            download_url = f"{url}{self.browser_download_url}"
            logger.ui(f"下载链接:\n{download_url}")
            if self.download_update_zip(download_url):
                return True

        logger.ui_warn("镜像站下载失败")
        return False

    def _check_local_package_before_download(self) -> bool | None:
        """下载前检查本地更新包

        Returns:
            True: 本地包 SHA-256 校验通过，可直接复用；
            False: 本地包校验失败，已发出继续解压确认；
            None: 无本地包或无法校验，继续原有检测/下载流程。
        """
        if not self.file or not os.path.exists(self.file) or not self.sha256:
            return None

        if self.verify_archive_sha256():
            self.sha_verified = True
            self.size_mismatch = False
            logger.ui("本地更新包校验通过，直接使用")
            return True

        signal_manager.main.message_box_requested.emit(
            MessageBoxPayload.question(MessageBoxPayload.Action.EXTRACT_CONFIRM)
        )
        return False

    def reset_verification_state(self) -> None:
        """清除本地包校验状态，不删除文件"""
        self.sha_verified = False
        self.size_mismatch = False

    def _download_mirrorchyan(self) -> bool:
        """通过 Mirror酱 分发站下载更新包"""
        cdk = config.user.mirrorchyan_cdk
        if not cdk:
            logger.ui_error("未填写 Mirror酱 CDK，请前往设置页填写")
            return False

        # 仅复用 Mirror酱 检查时返回的地址；其他线路的地址可能不是 Mirror酱 的更新包
        download_url = self.browser_download_url if self.download_source == UpdateDownload.MIRRORCHYAN else None
        if download_url:
            logger.info(f"下载链接:\n{download_url}")
            if self.download_update_zip(download_url):
                return True
            # 签发的下载地址有时效，失败后重新获取一次
            logger.ui_warn("Mirror酱 下载地址可能已过期，重新获取")

        try:
            info = check_for_update(cdk, force=True)
        except Exception as e:
            logger.ui_error(f"Mirror酱 获取更新失败: {e}")
            return False

        if info is None:
            logger.ui_error("Mirror酱 暂未检测到新版本更新包")
            return False

        # 更新包以 Mirror酱 返回的文件信息为准
        self.file = info.file_name
        self.file_size = info.file_size
        self.sha256 = info.sha256
        self.browser_download_url = info.url
        self.download_source = UpdateDownload.MIRRORCHYAN
        self.sha_verified = False
        self.size_mismatch = False

        logger.info(f"下载链接:\n{info.url}")
        if not self.download_update_zip(info.url):
            logger.ui_error(f"Mirror酱 下载失败: {info.url}")
            return False

        return True

    @run_in_thread
    def ui_update_handle(self):
        local_status = self._check_local_package_before_download()
        if local_status is False:
            signal_manager.update_new_version.close_ui.emit()
            return
        if local_status is True:
            signal_manager.main.message_box_requested.emit(
                MessageBoxPayload.question(MessageBoxPayload.Action.UPDATE_RESTART)
            )
            signal_manager.update_new_version.close_ui.emit()
            return

        if self._check_download_zip() and self._verify_downloaded_package(verify_sha=False):
            signal_manager.main.message_box_requested.emit(
                MessageBoxPayload.question(MessageBoxPayload.Action.UPDATE_RESTART)
            )
        else:
            logger.ui_error("更新失败")
        signal_manager.update_new_version.close_ui.emit()

    @run_in_thread
    def ui_download_handle(self):
        if not self._check_download_zip() or not self._verify_downloaded_package():
            logger.ui_error("下载失败")
        signal_manager.update_new_version.close_ui.emit()

    def verify_archive_sha256(self) -> bool:
        """解压前校验更新包 SHA-256

        下载流程会先校验一次大小；「仅下载」还会提前校验摘要。
        更新重启流程保留此校验作为解压前兜底，失败时可让用户确认继续。

        Returns:
            True: 校验通过，或无法校验（未提供摘要、文件不存在）；
            False: 摘要不一致。
        """
        if not self.sha256 or not self.file or not os.path.exists(self.file):
            return True
        logger.ui("正在校验更新包 SHA-256...")
        try:
            _actual = _file_sha256(self.file)
        except OSError as e:
            logger.ui_warn(f"无法读取更新包，跳过 SHA-256 校验: {e}")
            return True
        if _actual == self.sha256:
            logger.info("更新包 SHA-256 校验通过")
            return True
        logger.error(f"更新包 SHA-256 校验失败（期望 {self.sha256}，实际 {_actual}）")
        logger.ui_error("更新包 SHA-256 校验失败")
        return False

    def _remove_invalid_package(self) -> None:
        """删除校验失败的更新包，避免下次误用"""
        if not self.file:
            return
        try:
            os.remove(self.file)
        except OSError as e:
            logger.ui_warn(f"删除异常更新包失败: {e}")

    def _verify_downloaded_package(self, *, verify_sha: bool = True) -> bool:
        """下载完成后校验更新包大小与 SHA-256

        大小不一致时保留文件并记录 `size_mismatch`，交由 `restart` 弹窗确认是否继续；
        `verify_sha=True` 时校验 SHA-256，失败则删除文件。

        Args:
            verify_sha: 是否同时校验 SHA-256。更新重启流程可跳过，
                交由 `restart` 在解压前校验并保留「继续解压」确认。
        """
        if not self.file or not os.path.exists(self.file):
            logger.ui_error("更新包不存在")
            return False

        try:
            actual_size = os.stat(self.file).st_size
        except OSError as e:
            logger.ui_error(f"读取更新包失败: {e}")
            return False

        self.size_mismatch = bool(self.file_size and actual_size != self.file_size)
        if self.size_mismatch:
            logger.ui_warn(f"更新包大小不一致（期望 {self.file_size}，实际 {actual_size}），保留文件继续校验")

        if verify_sha and not self.verify_archive_sha256():
            self._remove_invalid_package()
            return False

        if verify_sha:
            self.sha_verified = True

        return True

    def download_update_zip(self, download_url: str) -> bool:
        """下载更新包"""
        logger.info(f"下载链接: {download_url}")
        self.sha_verified = False
        self.size_mismatch = False
        try:
            with httpx.stream("GET", download_url, headers=Connect.headers, follow_redirects=True) as r:
                logger.info(f"status_code: {r.status_code}")
                if r.status_code != 200:
                    logger.ui_error(f"下载链接异常，url: {download_url}")
                    return False

                _content_length = r.headers.get("content-length")
                if _content_length is None:
                    logger.ui_error("无法获取更新包大小")
                    return False
                _bytes_total = int(_content_length)
                logger.ui(f"更新包大小:{hum_convert(_bytes_total)}")
                download_zip_percentage_update(self.file, _bytes_total)
                with open(self.file, "wb") as f:
                    f.writelines(r.iter_bytes(chunk_size=65536))

                actual_size = os.stat(self.file).st_size
                if actual_size != _bytes_total:
                    logger.ui_error(f"更新包下载不完整（期望 {_bytes_total}，实际 {actual_size}）")
                    self._remove_invalid_package()
                    return False

                _msg = "更新包下载完成"
                logger.ui(_msg)
                toast(_msg)
                return True

        except httpx.ConnectTimeout:
            logger.ui_warn("超时，尝试更换源")
            self._remove_invalid_package()
            return False

        except Exception as e:
            logger.ui_warn(f"访问下载链接失败{e}")
            self._remove_invalid_package()
            return False

    @run_in_thread
    def check_latest(self, manual: bool = False):
        """检查更新

        Args:
            manual: 是否为手动检查。手动检查不受自动更新开关限制，并明确提示结果。
        """
        with self._check_lock:
            if self._checking:
                logger.info(f"已有更新检查进行中，跳过本次{'手动' if manual else '自动'}检查")
                if manual:
                    signal_manager.main.info_bar_requested.emit("检查更新", "正在检查更新，请稍候", "info", 5)
                return
            self._checking = True

        try:
            logger.info("手动检查更新" if manual else "检查更新")
            if not manual and not config.user.auto_update:
                logger.info("跳过更新")
                return

            STATUS = self.get_browser_download_url(force=manual)
            info_bar: tuple[str, str, str, int] | None = None
            match STATUS:
                case StatusCode.LATEST:
                    info_bar = ("检查更新", "当前已是最新版本", "success", 5)
                case StatusCode.NEW_VERSION:
                    logger.ui(f"新版本{self.new_version}")
                    signal_manager.update_new_version.show_ui.emit()
                    toast("检测到新版本", f"{self.new_version}\n{self.new_version_info}")
                case StatusCode.CONNECT_ERROR:
                    info_bar = ("检查更新失败", "访问更新地址失败", "warning", 5)
                case StatusCode.RELEASES_ERROR:
                    info_bar = ("检查更新失败", "获取发布信息失败", "warning", 5)
                case StatusCode.ZIP_ERROR:
                    info_bar = ("检查更新失败", "更新包异常", "warning", 5)
                case StatusCode.MIRRORCHYAN_ERROR:
                    info_bar = (
                        "检查更新失败",
                        self.error_message or "Mirror酱 检查更新失败",
                        "warning",
                        5,
                    )
                case _:
                    info_bar = ("检查更新失败", "未知错误", "warning", 5)

            if info_bar:
                if info_bar[2] == "success":
                    logger.info(info_bar[1])
                else:
                    logger.ui_warn(info_bar[1])
                if manual:
                    signal_manager.main.info_bar_requested.emit(*info_bar)
        finally:
            with self._check_lock:
                self._checking = False
            signal_manager.main.update_check_finished.emit()

    def _unzip_handle(self) -> bool:
        """解压更新包"""
        logger.info("解压更新包")
        self.zip_path = self.file
        logger.info(f"更新包路径: {self.zip_path}")
        self.zip_files_path: Path = APP_PATH / "zip_files"
        logger.info(f"解压路径: {self.zip_files_path}")
        if not zipfile.is_zipfile(self.zip_path):
            logger.ui_error("更新包异常")
            return False

        try:
            logger.ui("开始解压...")
            self.zip_files_path.mkdir(parents=True, exist_ok=True)
            _file_count = 0
            with zipfile.ZipFile(self.zip_path, "r") as f_zip:
                for info in f_zip.infolist():
                    info.filename = info.filename.encode("cp437").decode("gbk")  # 解决中文文件名乱码问题
                    f_zip.extract(info, self.zip_files_path)
                    timestamp = time.mktime(info.date_time + (0, 0, -1))
                    # 保留文件修改日期
                    os.utime(
                        os.path.join(str(self.zip_files_path), info.filename),
                        (timestamp, timestamp),
                    )
                    _file_count += 1

            logger.ui(f"解压结束，共解压 {_file_count} 个文件")
            Path(self.zip_path).unlink()
            logger.ui("删除更新包")
            return True

        except zipfile.BadZipFile:
            logger.ui_error("文件异常，请检查文件是否损坏")

        except Exception as e:
            logger.ui_error(f"解压失败：{e}")

        return False

    @run_in_thread(name="update_manager_restart")
    def restart(self, force: bool = False):
        """解压更新包并重启应用程序

        Args:
            force: 跳过 SHA-256 校验直接解压，仅在用户确认继续解压时使用。
        """
        logger.info("开始解压更新包")

        if not force:
            if not self.sha_verified and not self.verify_archive_sha256():
                # 校验失败不直接解压，交由界面确认后以 force=True 重新调用
                signal_manager.main.message_box_requested.emit(
                    MessageBoxPayload.question(MessageBoxPayload.Action.EXTRACT_CONFIRM)
                )
                return
            if self.size_mismatch:
                # 大小不一致同样交由界面确认是否继续解压
                signal_manager.main.message_box_requested.emit(
                    MessageBoxPayload.question(MessageBoxPayload.Action.EXTRACT_CONFIRM)
                )
                return

        if not self._unzip_handle():
            logger.error("解压更新包失败，终止更新重启")
            signal_manager.main.message_box_requested.emit(
                MessageBoxPayload.error("解压更新包失败，请检查更新包是否损坏后重试")
            )
            return

        try:
            # 使用脚本重启
            logger.info("开始重启应用程序")
            _restart = Restart()
            logger.info("编写更新重启脚本")
            _restart.write_update_restart_bat(self.zip_files_path.name)
            logger.info("重启应用程序")
            _restart.app_restart(is_update=True)
        except Exception as e:
            logger.error(f"更新重启失败: {e}", exc_info=True)
            signal_manager.main.message_box_requested.emit(MessageBoxPayload.error(f"更新重启失败: {e}"))

    @staticmethod
    def _json_read(file_path: str):
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _json_write(file_path: str, data: dict):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _write_update_record(self, record: list[dict]):
        """将版本历史写入本地更新记录缓存"""
        if not USER_DATA_DIR_PATH.exists():
            USER_DATA_DIR_PATH.mkdir(parents=True)
        self._json_write(UPDATE_INFO_FILE, record)

    def get_local_update_record(self) -> list[dict]:
        """获取本地更新记录（缓存由检查更新时写入，不存在时返回空列表）"""
        if not UPDATE_INFO_FILE.exists():
            return []
        return self._json_read(UPDATE_INFO_FILE)


update_manager = Update()


def hum_convert(value):
    """转换文件大小"""
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    value = int(value)
    size = 1024.0
    for unit in units:
        if (value / size) < 1:
            return f"{value:.2f}{unit}"
        value = value / size


@run_in_thread
def download_zip_percentage_update(file, total_size: int):
    """
    下载进度条

    xxMB/xxMB (速度: xx MB/s)
    """
    last_time = time.time()
    last_size = 0
    speed = 0.0

    while True:
        curr = Path(file).stat().st_size if Path(file).exists() else 0
        current_time = time.time()

        # 计算下载速度
        time_diff = current_time - last_time
        if time_diff > 0:  # 只有在时间差大于0时才计算速度
            size_diff = curr - last_size
            speed = size_diff / time_diff / (1024 * 1024)  # 转换为MB/s

        # 更新显示文本：大小 + 速度
        display_text = f"{hum_convert(curr)}/{hum_convert(total_size)} (速度: {speed:.2f} MB/s)"
        signal_manager.update_new_version.progress_text_changed.emit(display_text)

        progress = 0
        if total_size > 0:
            progress = min(100, int(100 * (curr / total_size)))
        signal_manager.update_new_version.progress_bar_changed.emit(progress)

        # 更新上一次记录
        last_time = current_time
        last_size = curr

        # 每隔500ms更新一次进度条
        time.sleep(0.5)
        if curr >= total_size:
            break
