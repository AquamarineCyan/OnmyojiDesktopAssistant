import json
import os
import time
import zipfile
from enum import Enum
from pathlib import Path

import httpx

from .application import APP_EXE_NAME, APP_NAME, APP_PATH, VERSION, Connect
from .config import _update_download_list, config
from .decorator import log_function_call, run_in_thread
from .log import logger
from .mysignal import global_ms as ms
from .restart import Restart
from .toast import toast


class StatusCode(Enum):
    LATEST = 1
    NEW_VERSION = 2
    CONNECT_ERROR = 3
    RELEASES_ERROR = 4
    ASSETS_ERROR = 5
    ZIP_ERROR = 6


class Upgrade(Connect):
    """更新升级"""

    def __init__(self) -> None:
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

    def compare_versions(self, new_version, current_version):
        # 将版本号分割成部分并转换为整数
        v1_parts = list(map(int, new_version.split(".")))
        v2_parts = list(map(int, current_version.split(".")))

        # 比较每个部分
        for v1, v2 in zip(v1_parts, v2_parts):
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1

        # 如果部分相同，比较长度
        if len(v1_parts) < len(v2_parts):
            return -1  #
        elif len(v1_parts) > len(v2_parts):
            return 1

        return 0  # 两个版本号相等

    def get_browser_download_url(self) -> StatusCode:
        """获取更新包地址

        返回:
            StatusCode: 状态码
        """
        _api_url = self.github_api
        logger.info(f"api_url: {_api_url}")

        try:
            response = httpx.get(_api_url, headers=self.headers)
            logger.info(f"api.status_code: {response.status_code}")
            if response.status_code != 200:
                return StatusCode.CONNECT_ERROR
        except Exception as e:
            logger.ui_warn(f"获取更新信息失败: {e}")
            return StatusCode.CONNECT_ERROR

        response_dict = json.loads(response.text)
        if "v" not in response_dict["tag_name"]:
            # 由Releases决定，一般不可能
            return StatusCode.RELEASES_ERROR

        self.new_version = response_dict["tag_name"][1:]
        logger.info(f"new_version:{self.new_version}")
        if self.compare_versions(self.new_version, VERSION) < 0:
            return StatusCode.LATEST

        _info: str = response_dict["body"]
        logger.info(_info)
        self.new_version_info = _info[: _info.find("**Full Changelog**")].rstrip("\n")
        if len(response_dict["assets"]) == 0:
            return StatusCode.ASSETS_ERROR

        for item in response_dict["assets"]:
            logger.info(item)
            if item.get("name") == f"{APP_NAME}-{self.new_version}.zip":
                self.browser_download_url = item["browser_download_url"]
                logger.info(f"browser_download_url:{self.browser_download_url}")
                self.file = self.browser_download_url.split("/")[-1]
                logger.info(f"file:{self.file}")
                self.file_size = item["size"]
                logger.info(f"file_size:{self.file_size}")
                return StatusCode.NEW_VERSION

        return StatusCode.ZIP_ERROR

    def get_mirror_station_url(self) -> str:
        return f"{self.mirror_station}{self.browser_download_url}"

    def _check_local_file(self, file: str, size: int) -> bool:
        if os.path.exists(file) and os.stat(file).st_size == size:
            return True
        return False

    def _check_download_zip(self):
        if self._check_local_file(self.file, self.file_size):
            logger.ui("检测到本地存在新版本更新包")
            return True

        logger.ui("即将开始下载新版本更新包")
        _download_url_default_list = [
            self.browser_download_url,
            self.get_mirror_station_url(),
        ]

        if config.user.update_download == _update_download_list[0]:  # mirror
            _download_url_user_list = list_change_first(_download_url_default_list, 1)
        else:
            _download_url_user_list = _download_url_default_list
        logger.info(f"_download_url_user_list:{_download_url_default_list}")

        _result = False
        for download_url in _download_url_user_list:
            logger.ui(f"下载链接:\n{download_url}")
            if self.download_upgrade_zip(download_url):
                _result = True
                break
        return _result

    @run_in_thread
    def ui_update_func(self):
        if self._check_download_zip() and self._check_local_file(self.file, self.file_size):
            ms.main.qmessagbox_update.emit("question", "更新重启")
        else:
            logger.ui_error("更新失败")
        ms.upgrade_new_version.close_ui.emit()

    @run_in_thread
    def ui_download_func(self):
        self._check_download_zip()
        ms.upgrade_new_version.close_ui.emit()

    def download_upgrade_zip(self, download_url: str) -> bool:
        """下载更新包"""
        try:
            with httpx.stream(
                "GET", download_url, headers=self.headers, follow_redirects=True
            ) as r:
                logger.info(f"status_code: {r.status_code}")
                if r.status_code != 200:
                    logger.ui_error(f"下载链接异常，url: {download_url}")
                    return False

                _bytes_total = int(r.headers["Content-length"])
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

    @log_function_call
    @run_in_thread
    def check_latest(self) -> None:
        """检查更新"""
        if config.user.update == "关闭":
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
            case StatusCode.ASSETS_ERROR:
                logger.ui_warn("更新包尚未发布，稍后重试")
            case StatusCode.ZIP_ERROR:
                logger.ui_warn("更新包异常")
            case _:
                logger.ui_warn("UPDATE ERROR")

    @log_function_call
    def _unzip_func(self) -> bool:
        self.zip_path = self.file
        logger.info(f"更新包路径: {self.zip_path}")
        self.zip_files_path: Path = APP_PATH / "zip_files"
        logger.info(f"解压路径: {self.zip_files_path}")
        if not zipfile.is_zipfile(self.zip_path):
            logger.ui_warn("更新包异常")
            return False

        try:
            _result = False
            logger.ui("开始解压...")
            with zipfile.ZipFile(self.zip_path, "r") as f_zip:
                f_zip.extractall(self.zip_files_path)
                # 保留提取文件修改日期
                for info in f_zip.infolist():
                    info.filename = info.filename.encode("cp437").decode(
                        "gbk"
                    )  # 解决中文文件名乱码问题
                    f_zip.extract(info, self.zip_files_path)
                    timestamp = time.mktime(info.date_time + (0, 0, -1))
                    os.utime(
                        os.path.join(self.zip_files_path.__str__(), info.filename),
                        (timestamp, timestamp),
                    )

            logger.ui("解压结束")
            Path(self.zip_path).unlink()
            logger.ui("删除更新包")
            _result = True

        except zipfile.BadZipFile:
            logger.ui_error("文件异常，请检查文件是否损坏")

        except Exception as e:
            logger.ui_error(f"解压失败：{e}")

        return _result

    def _move_files_recursive(self, source_folder: Path, target_folder: Path) -> None:
        """递归移动文件"""
        for item_path in source_folder.iterdir():
            target_path = target_folder / item_path.name
            if item_path.is_file() and item_path.name != APP_EXE_NAME:  # 排除exe
                item_path.replace(target_path)
                self.move_n += 1
            elif item_path.is_dir():
                target_path.mkdir(exist_ok=True)
                self._move_files_recursive(item_path, target_path)

    @log_function_call
    @run_in_thread
    def restart(self) -> None:
        """解压更新包并重启应用程序"""
        if not self._unzip_func():
            return
        # self.move_n: int = 0
        # self._move_files_recursive(self.zip_files_path, APP_PATH)
        # logger.info(f"finish moving {self.move_n} files.")
        _restart = Restart()
        _restart.write_upgrage_restart_bat(self.zip_path)
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
def download_zip_percentage_update(file, max: int):
    """
    下载进度条

    xxMB/xxMB
    """
    while True:
        curr = Path(file).stat().st_size if Path(file).exists() else 0
        ms.upgrade_new_version.text_insert.emit(
            f"{hum_convert(curr)}/{hum_convert(max)}"
        )
        ms.upgrade_new_version.progressBar_update.emit(int(100 * (curr / max)))
        time.sleep(0.1)
        if curr >= max:
            break


def list_change_first(_list: list = None, _index: int = None):
    """提取元素置于列表首位"""
    _value = _list[_index]
    copy_list = _list.copy()
    copy_list.remove(_value)
    return [_value, *copy_list]
