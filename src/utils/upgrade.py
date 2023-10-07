#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# upgrade.py
"""更新升级"""

import json
import os
import time
import zipfile
from pathlib import Path

import httpx

from .application import APP_EXE_NAME, APP_NAME, APP_PATH, VERSION
from .config import config
from .decorator import log_function_call, run_in_thread
from .function import app_restart, write_upgrage_restart_bat
from .log import logger
from .mysignal import global_ms as ms
from .toast import toast


class Upgrade:
    """更新升级"""

    def __init__(self) -> None:
        self.headers: dict = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70"
        }
        self.version_github: str = ""
        self.browser_download_url: str = ""
        self.new_version_info: str = ""
        self.zip_path: str = None
        """更新包路径"""

    def _get_browser_download_url(self) -> str:
        """获取更新地址

        Returns:
            str: 更新地址
        """
        api_url = "https://api.github.com/repos/AquamarineCyan/Onmyoji_Python/releases/latest"
        try:
            result = httpx.get(api_url, headers=self.headers)
            logger.info(f"api_url.status_code:{result.status_code}")
            if result.status_code == 200:
                data_dict = json.loads(result.text)
                if "v" in data_dict["tag_name"]:
                    self.version_github = data_dict["tag_name"][1:]
                    logger.info(f"version_github:{self.version_github}")
                    if self.version_github > VERSION:
                        _info: str = data_dict["body"]
                        self.new_version_info = (_info[:_info.find("**Full Changelog**")].rstrip("\n"))
                        for item in data_dict["assets"]:
                            if item["name"] == f"Onmyoji_Python-{self.version_github}.zip":
                                logger.info(item["name"])
                                self.browser_download_url = item["browser_download_url"]
                                logger.info(f"browser_download_url:{self.browser_download_url}")
                        return "NEW VERSION"
                    else:
                        return "LATEST"
        except Exception:
            return "CONNECT ERROR"

    def _get_ghproxy_url(self) -> str:
        return f"https://ghproxy.com/{self.browser_download_url}"

    def _check_download_zip(self):
        logger.info(f"browser_download_url:{self.browser_download_url}")
        self.zip_path = self.browser_download_url.split("/")[-1]
        logger.info(f"zip_name:{self.zip_path}")
        if APP_PATH.joinpath(self.browser_download_url.split("/")[-1]) in APP_PATH.iterdir():
            logger.ui("存在新版本更新包")
            toast("存在新版本更新包", "请关闭程序后手动解压覆盖")
        else:
            logger.ui("未存在新版本更新包，即将开始下载")
            _download_url_default_list = [self.browser_download_url, self._get_ghproxy_url()]
            # 使用用户配置的优先级
            if config.config_user.get("下载线路") == "ghproxy":
                _download_url_user_list = list_change_first(_download_url_default_list, _download_url_default_list[1])
            else:
                # 默认顺序
                _download_url_user_list = _download_url_default_list
            for download_url in _download_url_user_list:
                logger.ui(f"下载链接:\n{download_url}")
                if self._download_zip(download_url):
                    break

    def _download_zip(self, download_url: str) -> bool:
        """下载更新包"""
        try:
            with httpx.stream("GET", download_url, headers=self.headers, follow_redirects=True) as r:
                logger.info(f"status_code: {r.status_code}")
                print(r.headers)
                if r.status_code != 200:
                    return False
                _bytes_total = int(r.headers["Content-length"])
                logger.ui(f"更新包大小:{hum_convert(_bytes_total)}")
                download_zip_percentage_update(self.zip_path, _bytes_total)
                with open(self.zip_path, "wb") as f:
                    for chunk in r.iter_bytes(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                logger.ui("更新包下载完成，请关闭程序后手动解压覆盖")
                toast("更新包下载完成", "请关闭程序后手动解压覆盖")
                return True
        except httpx.ConnectTimeout:
            logger.ui("超时，尝试更换源", "warn")
            return False
        except Exception:
            logger.ui("访问下载链接失败", "warn")
            return False

    @log_function_call
    @run_in_thread
    def check_latest(self) -> None:
        """检查更新"""
        if config.config_user.get("更新模式") == "关闭":
            logger.info("skip for upgrade")
            return

        STATUS = self._get_browser_download_url()
        match STATUS:
            case "NEW VERSION":
                logger.ui(f"新版本{self.version_github}")
                toast("检测到新版本", f"{self.version_github}\n{self.new_version_info}")
                logger.ui(self.new_version_info)
                self._check_download_zip()
                for item_path in APP_PATH.iterdir():
                    if APP_NAME in item_path.name.__str__() and item_path.suffix == ".zip":
                        self.zip_path = item_path
                        break
                if self.zip_path and Path(self.zip_path).exists():
                    ms.qmessagbox_update.emit("question", "更新重启")
            case "LATEST":
                logger.info("暂无更新")
            case "CONNECT ERROR":
                logger.ui("访问更新地址失败", "warn")
            case _:
                logger.ui("UPDATE ERROR", "warn")

    def _unzip_func(self) -> None:
        logger.info("start unzip")
        # 解压路径
        self.zip_files_path: Path = APP_PATH / "zip_files"
        # 压缩包文件
        logger.ui("开始解压...")

        with zipfile.ZipFile(self.zip_path, "r") as f_zip:
            f_zip.extractall(self.zip_files_path)
            # 保留提取文件修改日期
            for info in f_zip.infolist():
                info.filename = info.filename.encode("cp437").decode("gbk")  # 解决中文文件名乱码问题
                f_zip.extract(info, self.zip_files_path)
                timestamp = time.mktime(info.date_time + (0, 0, -1))
                os.utime(os.path.join(self.zip_files_path.__str__(), info.filename), (timestamp, timestamp))

        logger.ui("解压结束")
        Path(self.zip_path).unlink()
        logger.ui("删除更新包")

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

    def restart(self) -> None:
        """解压更新包并重启应用程序"""
        self._unzip_func()
        self.move_n: int = 0
        self._move_files_recursive(self.zip_files_path, APP_PATH)
        logger.info(f"finish moving {self.move_n} files.")
        write_upgrage_restart_bat(self.zip_path)
        app_restart(is_upgrade=True)


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
        ms.text_print_insert_update.emit(f"{hum_convert(curr)}/{hum_convert(max)}")
        time.sleep(0.05)
        if (curr >= max):
            break


def list_change_first(_list: list = None, _value: str = None):
    """提取元素置于列表首位"""
    if _value in _list:
        copy_list = _list.copy()
        copy_list.remove(_value)
        return [_value, *copy_list]
