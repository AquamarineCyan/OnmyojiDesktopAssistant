import json
import os
import time
import zipfile
from enum import Enum
from pathlib import Path

import httpx
from packaging.version import Version

from .application import APP_NAME, APP_PATH, VERSION, Connect
from .config import _update_download_list, config
from .decorator import run_in_thread
from .log import logger
from .mysignal import global_ms as ms
from .restart import Restart
from .toast import toast


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


class Upgrade(Connect):
    """更新升级"""

    def __init__(self):
        self.new_version: str = None
        """新版本版本号"""
        self.new_version_info: str = None
        """新版本更新内容"""
        self.browser_download_url: str = None
        """更新包下载链接"""
        self.file: str = None
        """下载文件名称"""
        self.file_size: int = None
        """下载文件大小"""
        self.zip_path: str = None
        """更新包路径"""

    def get_browser_download_url(self) -> StatusCode:
        """获取更新包地址

        返回:
            StatusCode: 状态码
        """
        _api_url = self.releases_latest_api
        logger.info(f"api_url: {_api_url}")

        try:
            response = httpx.get(_api_url, headers=self.headers, follow_redirects=True)
            logger.info(f"api.status_code: {response.status_code}")
            if response.status_code == 404:
                return StatusCode.CONNECT_ERROR
        except Exception as e:
            logger.ui_warn(f"获取更新信息失败: {e}")
            return StatusCode.CONNECT_ERROR

        response_dict = json.loads(response.text)
        _tag_name = response_dict.get("tag_name")
        if _tag_name is None or "v" not in _tag_name:
            return StatusCode.RELEASES_ERROR

        self.new_version = _tag_name[1:]
        logger.info(f"new_version:{self.new_version}")

        _assets_list = response_dict.get("assets", [])
        if len(_assets_list) == 0:
            # 新版本tag已创建但更新包尚未上传，视为无可用更新
            logger.info("新版本tag已创建，但更新包尚未上传")
            return StatusCode.LATEST

        if not compare_versions(self.new_version, VERSION):
            return StatusCode.LATEST

        _info: str = response_dict.get("body", "")
        logger.info(_info)
        _changelog_marker = "**Full Changelog**"
        if _changelog_marker in _info:
            self.new_version_info = _info[: _info.find(_changelog_marker)].rstrip("\n")
        else:
            self.new_version_info = _info

        for item in _assets_list:
            logger.info(item)
            if item.get("name") == f"{APP_NAME}-{self.new_version}.zip":
                self.browser_download_url = item.get("browser_download_url")
                if self.browser_download_url is None:
                    logger.ui_error("更新包下载链接丢失")
                    return StatusCode.ZIP_ERROR
                logger.info(f"更新包下载链接: {self.browser_download_url}")
                self.file = self.browser_download_url.split("/")[-1]
                logger.info(f"file:{self.file}")
                self.file_size = item.get("size")
                if self.file_size is None:
                    logger.ui_error("更新包大小缺失")
                    return StatusCode.ZIP_ERROR
                logger.info(f"file_size:{self.file_size}")
                return StatusCode.NEW_VERSION

        return StatusCode.ZIP_ERROR

    def _check_local_file(self, file: str, expected_size: int) -> bool:
        return bool(os.path.exists(file) and os.stat(file).st_size == expected_size)

    def _check_download_zip(self):
        if self._check_local_file(self.file, self.file_size):
            logger.ui("检测到本地存在新版本更新包")
            return True

        logger.ui("即将开始下载新版本更新包")

        # 检测各镜像站点延迟
        delay_dict = {}
        for url in self.mirror_station:
            try:
                r = httpx.get(url, headers=self.headers)
                delay_ms = round(r.elapsed.total_seconds() * 1000, 2)
                delay_dict[url] = delay_ms
                logger.ui(f"站点：{url}\n延迟: {delay_ms} 毫秒")
            except Exception as e:
                logger.ui_warn(f"访问站点 {url} 失败: {e}")
                delay_dict[url] = float("inf")
        sorted_urls = sorted(delay_dict, key=delay_dict.get)

        # 补全下载链接
        sorted_download_urls = []
        sorted_download_urls.extend(f"{url}{self.browser_download_url}" for url in sorted_urls)

        download_url_list = []
        if config.user.update_download == _update_download_list[0]:  # 镜像站
            download_url_list.extend(sorted_download_urls)
            download_url_list.append(self.browser_download_url)
        else:
            download_url_list.append(self.browser_download_url)
            download_url_list.extend(sorted_download_urls)
        logger.info(f"download_url_list:{download_url_list}")

        _result = False
        for download_url in download_url_list:
            logger.ui(f"下载链接:\n{download_url}")
            if self.download_upgrade_zip(download_url):
                _result = True
                break
        return _result

    @run_in_thread
    def ui_update_handle(self):
        if self._check_download_zip() and self._check_local_file(self.file, self.file_size):
            ms.main.qmessagbox_update.emit("question", "更新重启")
        else:
            logger.ui_error("更新失败")
        ms.upgrade_new_version.close_ui.emit()

    @run_in_thread
    def ui_download_handle(self):
        if not self._check_download_zip():
            logger.ui_error("下载失败")
        ms.upgrade_new_version.close_ui.emit()

    def download_upgrade_zip(self, download_url: str) -> bool:
        """下载更新包"""
        try:
            with httpx.stream("GET", download_url, headers=self.headers, follow_redirects=True) as r:
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
                    for chunk in r.iter_bytes(chunk_size=1024):
                        if chunk:
                            f.write(chunk)

                _msg = "更新包下载完成"
                logger.ui(_msg)
                toast(_msg)
                return True

        except httpx.ConnectTimeout:
            logger.ui_warn("超时，尝试更换源")
            return False

        except Exception as e:
            logger.ui_warn(f"访问下载链接失败{e}")
            return False

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
                ms.upgrade_new_version.show_ui.emit()
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

    @run_in_thread
    def restart(self):
        """解压更新包并重启应用程序"""
        logger.info("开始解压更新包")
        if not self._unzip_handle():
            return

        # 使用脚本重启
        logger.info("开始重启应用程序")
        _restart = Restart()
        logger.info("编写更新重启脚本")
        _restart.write_upgrage_restart_bat(self.zip_files_path.name)
        logger.info("重启应用程序")
        _restart.app_restart(is_upgrade=True)


upgrade = Upgrade()


def hum_convert(value):
    """转换文件大小"""
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    value = int(value)
    size = 1024.0
    for unit in units:
        if (value / size) < 1:
            return "%.2f%s" % (value, unit)
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
        ms.upgrade_new_version.progress_text_update.emit(display_text)

        progress = 0
        if total_size > 0:
            progress = min(100, int(100 * (curr / total_size)))
        ms.upgrade_new_version.progressBar_update.emit(progress)

        # 更新上一次记录
        last_time = current_time
        last_size = curr

        # 每隔500ms更新一次进度条
        time.sleep(0.5)
        if curr >= total_size:
            break
