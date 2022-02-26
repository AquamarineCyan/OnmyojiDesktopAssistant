#!/usr/bin/env python3
# update.py

"""
更新日志
主界面功能-1
"""


def UpdateRecord():
    update = {
        1.5: '''新增 百鬼夜行功能
优化 普通召唤的判定逻辑''',
        1.4: '''新增 个人结界功能
优化 图片素材存储''',
        1.3: '''新增 寮突破功能
优化 函数调用
优化 御魂组队情况''',
        1.2: '''新增 组队御魂功能''',
        1.1: '''新增 普通召唤功能'''
    }
    for key, value in update.items():
        print(key)
        print(value)
    print('\n')
