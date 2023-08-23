#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# update.py
"""更新日志"""

from .mysignal import global_ms as ms


def update_record():
    """更新日志"""
    update = {
        "1.7.7":
        """优化 优化日志记录速度
优化 道馆突破适配怀旧&简约主题
优化 适配活动「真火切磋」""",
        "1.7.6":
        """新增 开始/停止功能
优化 添加自动打包环境
优化 优化日志操作
优化 优化悬赏封印识别速度
优化 统一截图保存路径
优化 适配新版召唤界面
优化 适配活动「守缘合战」
修复 修复更新完新版本，重复识别更新包的问题
修复 修复业原火重复识别结束界面的问题
修复 修复个人突破无法刷新的问题
修复 修复悬赏封印卡住主任务的问题""",
        "1.7.5":
        """新增 单人探索测试功能
新增 契灵-探查测试功能
优化 日志保存的时间精度
优化 添加程序复用属性
优化 优化配置文件
优化 调整 `app` 属性
优化 修改项目结构
优化 简化组队御魂副本的场景提示
优化 调整调试信息的时间显示
优化 完善异常提醒
优化 移除主界面信息显示的行数限制
优化 优化契灵结契流程
优化 调整设置项-`更新模式`和`下载路线`
优化 适配活动「森间试炼」
修复 活动卡顿引起的判定异常问题
修复 修复单人御魂副本非正常结束的问题
修复 修复单人探索副本无法运行的问题
修复 修复单人探索副本结束后无法正确识别宝箱和妖气的问题
修复 修复结界突破识别异常的问题""",
        "1.7.4":
        """新增 手动重启按钮
优化 组队/单人御魂副本任务
优化 修改工具类函数的导入形式
优化 更新下载显示
优化 御魂副本支持素材复用
优化 组队永生之海副本，支持新版结算
优化 结果判断逻辑，防止手快提前进入结算逻辑
优化 重启函数
优化 适配活动「宴场维和」
修复 关闭悬赏可能导致进程卡住问题
修复 设置-更新模式未生效的问题
修复 组队御魂中场景判定问题
修复 业原火无法挑战的问题
""",
        "1.7.3":
        """新增 更新自动重启
新增 御魂副本测试项，使用新方法识别
新增 悬赏封印关闭选项，降低程序运行功耗（需重启）
新增 单人御魂副本测试功能
优化 默认启用镜像源下载
优化 完善资源检查
优化 测试用log文件夹测试完成后自动删除
优化 更新「妖塔燃战」限时活动资源
优化 设置界面
修复 镜像源启用失败的问题
修复 匹配更新包空路径的问题
修复 资源检测线程问题""",
        "1.7.2":
        """添加 对中文路径的提示
优化 配置文件的读取优先级
修复 潜存在的路径转义问题
修复 神罚素材不全问题
新增 日志自动清理（30天）
修复 日志文件概率乱码的问题
优化 游戏窗口检测
添加 更新记录
修复 utf-8异常乱码问题
添加 对组队御魂副本时司机可能出现的bug提示
新增 御魂掉落统计beta"""
    }

    for key, value in update.items():
        s: str = f"{str(key)}\n{str(value)}\n"
        ms.ui_update_record_textBrowser_update.emit(s)
