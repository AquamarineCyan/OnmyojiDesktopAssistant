#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# update.py
"""更新日志"""

from utils.mysignal import global_ms as ms


def update_record() -> None:
    """更新日志"""
    update = {
        "1.7.1":
        """优化 任务完成的表现形式
优化 系统通知保留至通知栏
添加 镜像下载源
添加 对部分素材的路径检查
适配 神罚副本""",
        "1.7.0":
        """该版本为1.7测试版
资源文件夹由 `pic` 更新为 `resource` ，尝试兼容旧资源文件夹
新增 配置文件及设置
优化 悬赏封印处理方式并添加设置项"""
    }

    for key, value in update.items():
        s: str = f"{str(key)}\n{str(value)}\n"
        ms.ui_update_record_textBrowser_update.emit(s)
