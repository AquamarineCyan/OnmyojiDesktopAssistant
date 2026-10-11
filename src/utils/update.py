import hashlib
import hmac
import json
import os
import threading
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime
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

_HASH_CHUNK_SIZE: int = 1 << 20
"""计算 SHA-256 的分块大小（1MB），避免一次性读入整个更新包"""

_PROGRESS_MAX_LIFETIME: float = 600.0
"""下载进度线程的最长存活时间（秒），兜底防止调用方漏传 stop_event"""


class StatusCode(Enum):
    LATEST = 1
    NEW_VERSION = 2
    CONNECT_ERROR = 3
    RELEASES_ERROR = 4
    ZIP_ERROR = 5


def compare_versions(new_version: str, current_version: str) -> bool:
    try:
        return Version(new_version) > Version(current_version)
    except Exception:
        logger.ui_warn(f"版本号格式异常: {new_version} vs {current_version}")
        return False


class MirrorChyanError(RuntimeError):
    """MirrorChyan 版本检测异常基类"""


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


def _parse_error(resp_status: int, data: dict) -> MirrorChyanError:
    """将响应转化为带提示的异常"""
    code = data.get("code", resp_status)
    msg = data.get("msg", "unknown error")
    if code in _CDK_ERROR_MESSAGES:
        msg = _CDK_ERROR_MESSAGES[code]
    return MirrorChyanError(f"Mirror酱 API (code={code}): {msg}")


def _strip_v(version: str) -> str:
    """去除版本号前缀 v"""
    return version[1:] if version.startswith("v") else version


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
    return datetime.fromtimestamp(expired_time).strftime("%Y-%m-%d")


def _check_mirrorchyan(cdk: str, current_version: str, timeout: int = 10) -> UpdateInfo | None:
    """通过 Mirror酱 分发站检查更新。

    Returns:
        有新版本返回 UpdateInfo；已是最新返回 None。
    Raises:
        MirrorChyanError: 检测失败。
    """
    api = _latest_api(cdk)
    logger.debug(f"Mirror酱 API: {_mask_cdk(api, cdk)}")
    try:
        resp = httpx.get(api, timeout=timeout)
        data = resp.json()
    except Exception as e:
        raise MirrorChyanError(f"Mirror酱 请求失败: {e}") from e

    if resp.status_code != 200 or data.get("code") != 0:
        raise _parse_error(resp.status_code, data)

    _data = data.get("data") or {}

    # 格式化打印有效期
    cdk_expired_time = int(_data.get("cdk_expired_time") or 0)
    if cdk_expired_time:
        logger.ui(f"Mirror酱 CDK 有效期至 {_format_expire(cdk_expired_time)}")

    version_name = _strip_v(str(_data.get("version_name", "")))
    if not version_name or not compare_versions(version_name, current_version):
        logger.info(f"Mirror酱 已是最新版本: {current_version}")
        return None

    # 有新版本时才返回 url 字段（最新版本时 API 不返回）
    url = _data.get("url") or ""
    if not url:
        raise MirrorChyanError("Mirror酱 未返回下载链接")

    return UpdateInfo(
        source="MirrorChyan",
        url=url,
        file_name=_zip_file_name(version_name),
        version=version_name,
        file_size=int(_data.get("filesize") or 0),
        sha256=normalize_sha256(str(_data.get("sha256") or "")),
        release_note=str(_data.get("release_note") or ""),
    )


def check_for_update(cdk: str, timeout: int = 10) -> UpdateInfo | None:
    """Mirror酱 独立线路：检查更新。

    Args:
        cdk: Mirror酱 CDK 密钥（必须，用于配额分发）。
        timeout: 单次请求超时。

    Returns:
        UpdateInfo 若有新版本；None 若已最新或无需更新。

    Raises:
        MirrorChyanError: 检测失败（CDK 无效、接口异常等）。
    """
    if not cdk:
        raise MirrorChyanError("未填写 Mirror酱 CDK")
    logger.info(f"Mirror酱 检查更新: current={VERSION}")
    return _check_mirrorchyan(cdk, VERSION, timeout)


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
        self.file: str = None
        """下载文件名称"""
        self.file_size: int = None
        """下载文件大小"""
        self.sha256: str = ""
        """下载文件的 SHA-256 期望值，空串表示远端未提供（将拒绝安装）"""
        self.zip_path: str = None
        """更新包路径"""

    def _fetch_releases(self, per_page: int = 10) -> tuple[list | None, StatusCode | None]:
        """拉取并过滤 GitHub 正式发布列表（去除草稿与预发布）。

        返回:
            (发布列表, None) 成功，列表可能为空，由调用方决策；
            (None, StatusCode) 失败时的状态码。
        """
        _api_url = f"{Connect.releases_api}?per_page={per_page}"
        logger.info(f"api_url: {_api_url}")
        try:
            response = httpx.get(
                _api_url,
                headers=Connect.headers,
                follow_redirects=True,
                timeout=Connect.API_TIMEOUT,
            )
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
        return [item for item in data if not item.get("draft") and not item.get("prerelease")], None

    @staticmethod
    def _build_version_history(releases: list) -> list[dict]:
        """从发布列表构建版本历史（新版本在前，仅保留 v 前缀 tag 并去除前缀）"""
        history = []
        for item in releases:
            tag = item.get("tag_name")
            if not tag or not tag.startswith("v"):
                continue
            history.append({"version": _strip_v(tag), "body": item.get("body", "")})
        return history

    def get_browser_download_url(self) -> StatusCode:
        """获取更新包地址

        Returns:
            StatusCode: 状态码
        """
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
        _tag_name = _latest.get("tag_name")
        if not _tag_name or not _tag_name.startswith("v"):
            return StatusCode.RELEASES_ERROR

        self.new_version = _strip_v(_tag_name)  # 去除“v”前缀
        logger.info(f"new_version:{self.new_version}")

        _assets_list = _latest.get("assets", [])
        if len(_assets_list) == 0:
            # 新版本tag已创建但更新包尚未上传，视为无可用更新
            logger.info("新版本tag已创建，但更新包尚未上传")
            return StatusCode.LATEST

        if not compare_versions(self.new_version, VERSION):
            return StatusCode.LATEST

        _info: str = _latest.get("body", "")
        logger.info(_info)
        self.new_version_info = _info

        _expected_file_name = _zip_file_name(self.new_version)
        _checksum_asset = None
        for item in _assets_list:
            name = item.get("name")
            if name == f"{_expected_file_name}.sha256":
                _checksum_asset = item
                continue
            if name == _expected_file_name:
                self.browser_download_url = item.get("browser_download_url")
                if self.browser_download_url is None:
                    logger.ui_error("更新包下载链接丢失")
                    return StatusCode.ZIP_ERROR
                logger.info(f"更新包下载链接: {self.browser_download_url}")
                self.file = _expected_file_name
                self.file_size = item.get("size")
                if self.file_size is None:
                    logger.ui_error("更新包大小缺失")
                    return StatusCode.ZIP_ERROR
                logger.info(f"file_size:{self.file_size}")

        if self.browser_download_url is None:
            return StatusCode.ZIP_ERROR

        # SHA-256 期望值来自 release 的 sidecar 资产（release.yml 产出）。
        # 没有它就不能给更新包背书：更新包会被解压后以管理员权限覆盖安装目录
        # 并执行，全程没有签名可依赖，哈希是唯一的完整性闸门。
        if _checksum_asset is None:
            logger.ui_error("该版本缺少 SHA-256 校验文件，拒绝安装")
            return StatusCode.ZIP_ERROR
        self.sha256 = self._fetch_release_checksum(_checksum_asset)
        if not self.sha256:
            logger.ui_error("SHA-256 校验文件无效，拒绝安装")
            return StatusCode.ZIP_ERROR

        return StatusCode.NEW_VERSION

    @staticmethod
    def _fetch_release_checksum(asset: dict) -> str:
        """下载并解析 release 的 `.sha256` sidecar 资产"""
        url = asset.get("browser_download_url")
        if not url:
            return ""
        try:
            resp = httpx.get(url, headers=Connect.headers, follow_redirects=True, timeout=Connect.API_TIMEOUT)
            if resp.status_code != 200:
                logger.ui_error(f"获取校验文件失败: HTTP {resp.status_code}")
                return ""
        except Exception as e:
            logger.ui_error(f"获取校验文件失败: {e}")
            return ""

        # sidecar 形如 "<64位小写hex>  OnmyojiDesktopAssistant-x.y.z.zip"
        return normalize_sha256(resp.text.strip().split()[0] if resp.text.strip() else "")

    def _check_local_file(self, file: str, expected_size: int) -> bool:
        return bool(os.path.exists(file) and os.stat(file).st_size == expected_size)

    @staticmethod
    def _verify_sha256(file: str, expected_sha256: str) -> bool:
        """校验文件 SHA-256

        更新包最终会被 `restart.bat` 以管理员权限覆盖进安装目录并执行，
        整条链路上没有任何签名或哈希校验，一旦镜像站/CDN 被投毒即是
        管理员权限任意代码执行。因此这里是唯一的完整性闸门：
        **期望值为空同样判失败**，不能因为「远端没给校验和」就放行。
        """
        if not expected_sha256:
            logger.ui_error("更新包缺少 SHA-256 校验值，拒绝安装")
            return False

        digest = hashlib.sha256()
        try:
            with open(file, "rb") as f:
                for block in iter(lambda: f.read(_HASH_CHUNK_SIZE), b""):
                    digest.update(block)
        except OSError as e:
            logger.ui_error(f"更新包读取失败: {e}")
            return False

        actual = digest.hexdigest()
        if not hmac.compare_digest(actual, expected_sha256):
            logger.ui_error("更新包 SHA-256 校验失败，文件可能已被篡改")
            logger.error(f"expected={expected_sha256}, actual={actual}")
            return False
        return True

    def _verify_downloaded_zip(self) -> bool:
        """下载完成后的统一校验：体积 + SHA-256"""
        if not self._check_local_file(self.file, self.file_size):
            logger.ui_error("更新包大小与预期不符")
            return False
        return self._verify_sha256(self.file, self.sha256)

    def _check_download_zip(self):
        if self._check_local_file(self.file, self.file_size):
            logger.ui("检测到已下载的新版本更新包")
            return True

        logger.ui("即将开始下载新版本更新包")

        match config.user.update_download:
            case UpdateDownload.GITHUB:
                return self.download_update_zip(self.browser_download_url)

            case UpdateDownload.MIRRORCHYAN:
                return self._download_mirrorchyan()

            case UpdateDownload.MIRROR:
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
                r = httpx.get(url, headers=Connect.headers, timeout=Connect.API_TIMEOUT)
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

    def _download_mirrorchyan(self) -> bool:
        """通过 Mirror酱 分发站下载更新包"""
        cdk = config.user.mirrorchyan_cdk
        if not cdk:
            logger.ui_error("未填写 Mirror酱 CDK，请前往设置页填写")
            return False

        try:
            info = check_for_update(cdk)
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
        logger.info(f"下载链接:\n{info.url}")
        if not self.download_update_zip(info.url):
            logger.ui_error(f"Mirror酱 下载失败: {info.url}")
            self._remove_partial_file()
            return False

        # 注意：不要用 os.stat 回填 file_size —— 那会让后续的体积校验退化成
        # 「文件大小 == 文件大小」的恒真比较，任何截断/替换/投毒都能通过。
        # 体积只用于快速失败，真正的闸门是 _verify_sha256。
        return True

    @run_in_thread
    def ui_update_handle(self):
        # 体积 + SHA-256 双校验通过才允许进入「解压 → 覆盖安装目录 → 管理员重启」
        if self._check_download_zip() and self._verify_downloaded_zip():
            signal_manager.main.message_box_requested.emit(
                MessageBoxPayload.question(MessageBoxPayload.Action.UPDATE_RESTART)
            )
        else:
            logger.ui_error("更新包校验失败，已中止更新")
            self._remove_partial_file()
        signal_manager.update_new_version.close_ui.emit()

    @run_in_thread
    def ui_download_handle(self):
        if not self._check_download_zip():
            logger.ui_error("下载失败")
        signal_manager.update_new_version.close_ui.emit()

    def _remove_partial_file(self) -> None:
        """清理下载失败留下的半截文件

        半截文件留在安装目录会被下一次 `_check_download_zip` 当成候选，
        让用户反复「下载失败却提示已存在」。
        """
        if not self.file:
            return
        try:
            Path(self.file).unlink(missing_ok=True)
        except OSError as e:
            logger.error(f"清理未完成文件失败: {e}")

    def download_update_zip(self, download_url: str) -> bool:
        """下载更新包

        先写 `*.part` 再原子替换：直接写最终路径时，中断会在安装目录留下
        半截 zip，而它会被下一次 `_check_download_zip` 当成「已下载的新版本」，
        随后以管理员权限解压执行。
        """
        logger.info(f"下载链接: {download_url}")
        tmp_path = f"{self.file}.part"
        progress_stop = threading.Event()
        progress_thread = None
        try:
            # 必须带 timeout：缺省下 GitHub/镜像站无响应会让守护线程永久挂起
            with httpx.stream(
                "GET",
                download_url,
                headers=Connect.headers,
                follow_redirects=True,
                timeout=Connect.DOWNLOAD_TIMEOUT,
            ) as r:
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

                progress_stop.clear()
                progress_thread = threading.Thread(
                    target=download_zip_percentage_update,
                    args=(self.file, _bytes_total),
                    kwargs={"stop_event": progress_stop},
                    daemon=True,
                )
                progress_thread.start()

                downloaded = 0
                with open(tmp_path, "wb") as f:
                    for chunk in r.iter_bytes(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                # 复核实际字节数：content-length 只说明服务端「打算」发多少
                if downloaded != _bytes_total:
                    logger.ui_error(f"更新包不完整（{downloaded}/{_bytes_total} 字节）")
                    return False

            os.replace(tmp_path, self.file)

            _msg = "更新包下载完成"
            logger.ui(_msg)
            toast(_msg)
            return True

        except httpx.TimeoutException:
            logger.ui_warn("超时，尝试更换源")
            return False

        except Exception as e:
            logger.ui_warn(f"访问下载链接失败{e}")
            return False

        finally:
            # 进度线程只在「下载完成」时才会自己退出；下载失败/中断时
            # 必须由这里显式通知，否则它会每 0.5s 轮询一次永久存活
            progress_stop.set()
            if progress_thread is not None and progress_thread.is_alive():
                progress_thread.join(timeout=2)
            Path(tmp_path).unlink(missing_ok=True)

    @run_in_thread
    def check_latest(self):
        """检查更新"""
        logger.info("检查更新")
        if not config.user.auto_update:
            logger.info("跳过更新")
            return

        STATUS = self.get_browser_download_url()
        match STATUS:
            case StatusCode.LATEST:
                logger.info("暂无更新")
            case StatusCode.NEW_VERSION:
                logger.ui(f"新版本{self.new_version}")
                signal_manager.update_new_version.show_ui.emit()
                toast("检测到新版本", f"{self.new_version}\n{self.new_version_info}")
            case StatusCode.CONNECT_ERROR:
                logger.ui_warn("访问更新地址失败")
            case StatusCode.RELEASES_ERROR:
                logger.ui_warn("获取发布信息失败")
            case StatusCode.ZIP_ERROR:
                logger.ui_warn("更新包异常")
            case _:
                logger.ui_warn("UPDATE ERROR")

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
                    # 只有非 UTF-8 标志位的条目才需要 cp437→gbk 转码。
                    # 原先无条件转码，遇到 Compress-Archive 产出的 UTF-8
                    # 文件名会抛 UnicodeError，进而让整个解压半途中断。
                    if not info.flag_bits & 0x800:
                        try:
                            info.filename = info.filename.encode("cp437").decode("gbk")
                        except (UnicodeEncodeError, UnicodeDecodeError):
                            pass  # 保留原始文件名，不要因为编码问题中断整包解压

                    # 用 extract 的返回值拿实际落盘路径：info.filename 是未净化的
                    # 原始条目名，os.path.join 后可能落到 zip_files 之外
                    extracted = f_zip.extract(info, self.zip_files_path)
                    _file_count += 1

                    # 修复文件时间：单条失败不应中断整包解压
                    try:
                        timestamp = time.mktime(info.date_time + (0, 0, -1))
                        os.utime(extracted, (timestamp, timestamp))
                    except (OSError, OverflowError, ValueError) as e:
                        logger.warning(f"修复文件时间失败: {extracted} ({e})")

            logger.ui(f"解压完成，共解压 {_file_count} 个文件")
            Path(self.zip_path).unlink()
            logger.ui("删除更新包")
            return True

        except zipfile.BadZipFile:
            logger.ui_error("文件异常，请检查文件是否损坏")

        except Exception as e:
            logger.ui_error(f"解压失败：{e}")

        return False

    @run_in_thread
    def restart(self):
        """解压更新包并重启应用程序"""
        # 二次校验：重启会以管理员权限覆盖安装目录并执行解压产物，
        # 这里是覆盖前的最后一道闸门，不允许「下载时校验过」被默认成立
        if not self._verify_downloaded_zip():
            logger.error("更新包校验失败，拒绝覆盖安装目录")
            signal_manager.main.message_box_requested.emit(
                MessageBoxPayload.error("更新包完整性校验失败，已中止更新")
            )
            self._remove_partial_file()
            return

        logger.info("开始解压更新包")

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
def download_zip_percentage_update(file, total_size: int, stop_event: threading.Event = None):
    """
    下载进度显示

    xxMB/xxMB (速度: xx MB/s)

    Args:
        stop_event: 取消信号。下载失败/中断时文件永远达不到 total_size，
            没有它这个线程会每 0.5s 永久轮询并持续向 GUI 发信号。
            另外加一个兜底超时，避免调用方忘记传。
    """
    last_time = time.time()
    last_size = 0
    speed = 0.0
    deadline = time.time() + _PROGRESS_MAX_LIFETIME

    while True:
        if stop_event is not None and stop_event.wait(timeout=0.5):
            return
        if time.time() > deadline:
            logger.warning("下载进度线程超时退出")
            return

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

        if curr >= total_size:
            return

        # 更新上一次记录
        last_time = current_time
        last_size = curr
