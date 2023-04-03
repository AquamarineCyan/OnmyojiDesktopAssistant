#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# upgrade.py
"""更新升级"""

import os
import time
import httpx
import json
import zipfile

from subprocess import Popen
from pathlib import Path

from .config import config
from .log import log
from .mysignal import global_ms as ms
from .toast import toast


class Upgrade:
    def __init__(self) -> None:
        self.application_path = config.application_path
        self.version_location = config.version
        self.headers: dict = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70"
        }
        self.version_github: str = ""
        self.browser_download_url: str = ""
        self.new_version_info: str = ""
        self.zip_path: str = None

    def _get_browser_download_url(self) -> str:
        """获取更新地址

        Returns:
            str: 更新地址
        """
        api_url = "https://api.github.com/repos/AquamarineCyan/Onmyoji_Python/releases/latest"
        try:
            result = httpx.get(api_url, headers=self.headers)
            log.info(f"api_url.status_code:{result.status_code}")
            if result.status_code == 200:
                data_dict = json.loads(result.text)
                log.info("tag_name:{}".format(data_dict["tag_name"]))
                if "v" in data_dict["tag_name"]:
                    self.version_github = data_dict["tag_name"][1:]
                    log.info(f"version_github:{self.version_github}")
                    if self.version_github > self.version_location:
                        self.new_version_info = data_dict["body"]
                        log.info(f"new_version_info:{self.new_version_info}")
                        for item in data_dict["assets"]:
                            if item["name"] == f"Onmyoji_Python-{self.version_github}.zip":
                                log.info(item["name"])
                                self.browser_download_url = item["browser_download_url"]
                                log.info(f"browser_download_url:{self.browser_download_url}")
                        return "NEW VERSION"
                    else:
                        return "LATEST"
        except:
            return "CONNECT ERROR"

    def _get_ghproxy_url(self) -> str:
        return f"https://ghproxy.com/{self.browser_download_url}"

    def _download_zip(self) -> bool:
        """下载更新包"""
        log.ui("准备下载更新包")
        log.ui(f"browser_download_url:{self.browser_download_url}")
        self.zip_path = self.browser_download_url.split("/")[-1]
        log.info(f"zip_name:{self.zip_path}")
        if self.application_path.joinpath(self.browser_download_url.split("/")[-1]) in self.application_path.iterdir():
            log.ui("存在新版本更新包")
            toast("存在新版本更新包", "请关闭程序后手动解压覆盖")
        else:
            log.ui("未存在新版本更新包，即将开始下载")
            try:
                for download_url in [self._get_ghproxy_url(), self.browser_download_url]:
                    log.info(download_url)
                    with httpx.stream("GET", download_url, headers=self.headers) as r:
                        log.info(f"status_code:{r.status_code}")
                        if r.status_code == 200:
                            bytes_total = r.headers["Content-length"]
                            log.ui(f"bytes_total:{bytes_total}")
                            with open(self.zip_path, "wb") as f:
                                for chunk in r.iter_bytes(chunk_size=1024):
                                    if chunk:
                                        f.write(chunk)
                            log.ui("更新包下载完成，请关闭程序后手动解压覆盖")
                            toast("更新包下载完成", "请关闭程序后手动解压覆盖")
                            return True
            except:
                log.ui("访问下载链接失败")
                return False

    def check_latest(self) -> None:
        """检查更新"""
        STATUS = self._get_browser_download_url()
        match STATUS:
            case "NEW VERSION":
                log.ui(f"新版本{self.version_github}")
                toast("检测到新版本", f"{self.version_github}\n{self.new_version_info}")
                log.ui(self.new_version_info)
                self._download_zip()
            case "LATEST":
                log.ui("暂无更新")
            case "CONNECT ERROR":
                log.ui("访问更新地址失败")
            case _:
                log.error("UPDATE ERROR", True)
        for item_path in self.application_path.iterdir():
            if "Onmyoji_Python" in item_path.name.__str__() and item_path.suffix == ".zip":
                self.zip_path = item_path
                break
        if self.zip_path and Path(self.zip_path).exists():
            ms.qmessagbox_update.emit("question", "更新重启")

    def _unzip_func(self) -> None:
        log.info("start unzip")
        # 解压路径
        self.zip_files_path: Path = self.application_path / "zip_files"
        # 压缩包文件
        log.ui("开始解压...")

        with zipfile.ZipFile(self.zip_path, "r") as f_zip:
            f_zip.extractall(self.zip_files_path)
            # 保留提取文件修改日期
            for info in f_zip.infolist():
                info.filename = info.filename.encode("cp437").decode("gbk")  # 解决中文文件名乱码问题
                f_zip.extract(info, self.zip_files_path)
                timestamp = time.mktime(info.date_time + (0, 0, -1))
                os.utime(os.path.join(self.zip_files_path.__str__(), info.filename), (timestamp, timestamp))

        log.ui("解压结束")

    def _move_files_recursive(self, source_folder: Path, target_folder: Path) -> None:
        """递归移动文件"""
        for item_path in source_folder.iterdir():
            target_path = target_folder / item_path.name
            if item_path.is_file() and item_path.name != config.exe_name:  # 排除exe
                item_path.replace(target_path)
                self.move_n += 1
            elif item_path.is_dir():
                target_path.mkdir(exist_ok=True)
                self._move_files_recursive(item_path, target_path)

    def _write_restart_bat(self) -> None:
        """编写bat脚本"""
        bat_text = f"""@echo off
@echo 当前为更新程序，等待自动完成
set "program_name={config.exe_name}"

:a
tasklist | findstr /I /C:"%program_name%" > nul
if errorlevel 1 (
    echo %program_name% is closed.
    goto :b
) else (
    echo %program_name% is still running, waiting...
    ping 123.45.67.89 -n 1 -w 1000 > nul
    goto :a
)

:b
echo Continue updating...

if not exist zip_files\{config.exe_name} exit
timeout /T 3 /NOBREAK
move /y zip_files\{config.exe_name} .
rd /s /q zip_files
del {self.zip_path}
start {config.exe_name}
"""

        with open("reload.bat", "w", encoding="ANSI") as f:
            f.write(bat_text)

    def reload(self) -> None:
        """解压更新包并重启应用程序"""
        self._unzip_func()
        self.move_n: int = 0
        self._move_files_recursive(self.zip_files_path, self.application_path)
        log.info(f"finish moving {self.move_n} files.")
        self._write_restart_bat()
        # 启动.bat文件
        Popen(["reload.bat"])
        # 关闭当前exe程序
        log.info("App Exiting...")
        ms.sys_exit_update.emit(True)


upgrade = Upgrade()
