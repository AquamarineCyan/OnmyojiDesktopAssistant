#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新升级
"""

import requests
import httpx
import json
from pathlib import Path

from mysignal import global_ms as ms
from package.log import Log

fpath = Path.cwd()
"""文件路径"""
from main import version as version_location

"""版本号"""


class Upgrade:
    def __init__(self):
        self.version_github: str = ""
        self.browser_download_url: str = ""
        self.new_version_info: str = ""

    def return_version_github(self) -> str:
        return self.version_github

    def return_browser_download_url(self) -> str:
        return self.browser_download_url

    def return_new_version_info(self) -> str:
        return self.new_version_info

    def get_browser_download_url(self) -> str:
        """
        获取更新地址

        :return: 更新地址
        """
        api_url = "https://api.github.com/repos/AquamarineCyan/Onmyoji_Python/releases/latest"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
        try:
            result = httpx.get(api_url, headers=headers)
            if result.status_code == 200:
                Log().log_write(result)
                # print(json.loads(result.text))
                # print(type(json.loads(result.text)))
                data_dict = json.loads(result.text)
                data = json.dumps(json.loads(result.text), indent=4, ensure_ascii=False)
                # print(type(data))
                with open("api_github.json", mode="w") as f:
                    f.write(data)

                Log().log_write("******")
                Log().log_write(data_dict["tag_name"])
                if "v" in data_dict["tag_name"]:
                    self.version_github = data_dict["tag_name"][1:]
                    print(self.version_github)
                    if self.version_github > version_location:
                        Log().log_write("*****")
                        Log().log_write(data_dict["body"])
                        self.new_version_info = data_dict["body"]
                        Log().log_write(data_dict["assets"])
                        Log().log_write(type(data_dict["assets"]))
                        Log().log_write(data_dict["assets"][0])
                        Log().log_write(type(data_dict["assets"][0]))
                        self.browser_download_url = data_dict["assets"][0]["browser_download_url"]
                        Log().log_write(self.browser_download_url)
                        Log().log_write(type(self.browser_download_url))
                        ms.text_print_update.emit(f"有新版本{self.version_github}")
                        return "has new version"
                    else:
                        ms.text_print_update.emit("暂无更新")
                        return "the version is the latest"
        except:
            ms.text_print_update.emit("获取更新地址失败")
            return "cant connect"

    def download_zip(self):
        """
        下载更新压缩包
        """
        # browser_download_url = "https://github.com/AquamarineCyan/Onmyoji_Python/releases/download/v1.6.5/Onmyoji_Python-1.6.5.zip"
        ms.text_print_update.emit("准备下载压缩包")
        ms.text_print_update.emit(self.browser_download_url)
        # zip_flag: bool = None
        zip_name = './' + self.browser_download_url.split('/')[-1]
        if fpath.joinpath(self.browser_download_url.split('/')[-1]) in fpath.iterdir():
            ms.text_print_update.emit("存在最新版本压缩包")
        else:
            ms.text_print_update.emit("未存在最新版本压缩包，即将开始下载")
            try:
                response = requests.get(self.browser_download_url, stream=True)
                Log().log_write(response.status_code)
                # zip_name = './' + browser_download_url.split('/')[-1]
                bytes_total = response.headers['Content-length']
                ms.text_print_update.emit(f"bytes_total = {bytes_total}")
                with open(zip_name, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)

                    ms.text_print_update.emit("download successfully")
            except:
                ms.text_print_update.emit("访问下载链接失败")

    def upgrade_auto(self):
        ms.text_print_update.emit(f"当前版本：{version_location}")
        if self.get_browser_download_url() == "has new version":
            self.download_zip()
            ms.text_print_update.emit(f"有新版本：{self.return_version_github()}")
            ms.text_print_update.emit(self.return_new_version_info())
