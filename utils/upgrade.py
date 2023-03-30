#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# upgrade.py
"""更新升级"""

import httpx
import json

from .config import config
from .log import log
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

    def get_browser_download_url(self) -> str:
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
                log.info(f"tag_name:{data_dict['tag_name']}")
                if "v" in data_dict["tag_name"]:
                    self.version_github = data_dict["tag_name"][1:]
                    log.info(f"version_github:{self.version_github}")
                    if self.version_github > self.version_location:
                        self.new_version_info = data_dict["body"]
                        log.info(f"new_version_info:{self.new_version_info}")
                        # log.info(f"assets:{data_dict['assets']}")
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

    def get_ghproxy_url(self) -> str:
        return f"https://ghproxy.com/{self.browser_download_url}"

    def download_zip(self) -> bool:
        """下载更新包"""
        log.ui("准备下载更新包")
        log.ui(f"browser_download_url:{self.browser_download_url}")
        zip_name = self.browser_download_url.split('/')[-1]
        log.info(f"zip_name:{zip_name}")
        if self.application_path.joinpath(self.browser_download_url.split('/')[-1]) in self.application_path.iterdir():
            log.ui("存在新版本更新包")
            toast("存在新版本更新包", "请关闭程序后手动解压覆盖")
        else:
            log.ui("未存在新版本更新包，即将开始下载")
            try:
                for download_url in [self.get_ghproxy_url(), self.browser_download_url]:
                    log.info(download_url)
                    with httpx.stream("GET", download_url, headers=self.headers) as r:
                        log.info(f"status_code:{r.status_code}")
                        if r.status_code == 200:
                            bytes_total = r.headers["Content-length"]
                            log.ui(f"bytes_total:{bytes_total}")
                            with open(zip_name, "wb") as f:
                                for chunk in r.iter_bytes(chunk_size=1024):
                                    if chunk:
                                        f.write(chunk)
                            log.ui("更新包下载完成，请关闭程序后手动解压覆盖")
                            toast("更新包下载完成", "请关闭程序后手动解压覆盖")
                            return True
            except:
                log.ui("访问下载链接失败")
                return False

    def upgrade_auto(self):
        STATUS = self.get_browser_download_url()
        match STATUS:
            case "NEW VERSION":
                log.ui(f"新版本{self.version_github}")
                toast("检测到新版本", f"{self.version_github}\n{self.new_version_info}")
                log.ui(self.new_version_info)
                self.download_zip()
            case "LATEST":
                log.ui("暂无更新")
            case "CONNECT ERROR":
                log.ui("访问更新地址失败")
            case _:
                log.error("UPDATE ERROR", True)
