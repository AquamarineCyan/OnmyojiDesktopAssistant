#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# gui.py

import sys
import time
from contextlib import suppress
from pathlib import Path
from threading import Thread

from PySide6.QtGui import QIcon, QPixmap, QTextCursor
from PySide6.QtWidgets import QMainWindow, QMessageBox, QWidget

from ..package import *
from ..ui.mainui import Ui_MainWindow
from ..ui.updateui import Ui_Form as Ui_Update_Record
from .application import APP_NAME, APP_PATH, RESOURCE_DIR_PATH, VERSION
from .config import config, is_Chinese_Path
from .decorator import log_function_call, run_in_thread
from .event import event_thread, event_xuanshang_enable
from .function import FightResource, app_restart, remove_restart_bat_file
from .log import log_clean_up, logger
from .mysignal import global_ms as ms
from .update import update_record
from .upgrade import upgrade
from .window import window


class MainWindow(QMainWindow):
    _list_function = [  # 功能列表
        "1.御魂副本",
        "2.永生之海副本",
        "3.业原火副本",
        "4.御灵副本",
        "5.个人突破",
        "6.寮突破",
        "7.道馆突破",
        "8.普通召唤",
        "9.百鬼夜行",
        "10.限时活动",
        "11.组队日轮副本",
        "12.单人探索",
        "13.契灵",
    ]
    _choice: int  # 功能

    def __init__(self):
        super().__init__()
        # 使用ui文件导入定义界面类
        self.ui = Ui_MainWindow()
        # 初始化界面
        self.setFixedSize(550, 450)  # 固定宽高
        self.ui.setupUi(self)
        # 窗口图标
        icon = QIcon()
        icon.addPixmap(QPixmap("buzhihuo.ico"))
        self.setWindowIcon(icon)
        self.setWindowTitle(f"{APP_NAME} - v{VERSION}")  # 版本号显示
        # 初始化控件
        self.ui.combo_choice.addItems(self._list_function)
        self.ui.button_start.setEnabled(False)
        self.ui.combo_choice.setEnabled(False)
        self.ui.spinB_num.setEnabled(False)
        self.ui.stackedWidget.setCurrentIndex(0)  # 索引0，空白
        self.ui.label_tips.hide()
        # 设置界面
        _setting_QComboBox_dict: dict = {
            self.ui.setting_update_comboBox: "更新模式",
            self.ui.setting_download_comboBox: "下载线路",
            self.ui.setting_xuanshangfengyin_comboBox: "悬赏封印",
        }
        for key, value in _setting_QComboBox_dict.items():
            key.addItems(config.config_default[value])
            key.setCurrentText(config.config_user.get(value))
        self.ui.label_GitHub_address.setToolTip("通过浏览器打开")

        # 自定义信号
        # 弹窗更新
        ms.qmessagbox_update.connect(self.qmessagbox_update_func)
        # 主界面信息文本更新
        ms.text_print_update.connect(self.text_print_update_func)
        # 主界面信息文本覆盖
        ms.text_print_insert_update.connect(self.text_print_insert_func)
        # 运行状态更新
        ms.is_fighting_update.connect(self.is_fighting)
        # 完成情况文本更新
        ms.text_num_update.connect(self.text_num_update_func)
        # 退出程序
        ms.sys_exit_update.connect(self.exit)

        # 事件连接
        # 环境检测按钮
        self.ui.button_game_handle.clicked.connect(self.check_game_handle)
        # 开始按钮
        self.ui.button_start.clicked.connect(self.start_stop)
        # 功能选择事件
        self.ui.combo_choice.currentIndexChanged.connect(self.choice_text)
        # restart
        self.ui.button_restart.clicked.connect(app_restart)
        # 更新记录事件
        self.ui.button_update_record.clicked.connect(self.show_update_record_window)
        # GitHub地址悬停事件
        self.ui.label_GitHub_address.mousePressEvent = self.open_GitHub_address
        self.ui.buttonGroup_driver.buttonClicked.connect(self.tips_yuhun_driver)
        self.ui.buttonGroup_mode.buttonClicked.connect(self._yuhun_mode_change)

        # 设置项
        # 更新模式
        self.ui.setting_update_comboBox.currentIndexChanged.connect(
            self.setting_update_comboBox_func
        )
        # 下载线路
        self.ui.setting_download_comboBox.currentIndexChanged.connect(
            self.setting_download_comboBox_func
        )
        # 悬赏封印
        self.ui.setting_xuanshangfengyin_comboBox.currentIndexChanged.connect(
            self.setting_xuanshangfengyin_comboBox_func
        )

        # 程序开启运行
        self.application_init()

    @log_function_call
    @run_in_thread
    def application_init(self) -> None:
        """程序初始化"""
        logger.info(f"application path: {APP_PATH}")
        logger.info(f"resource path: {RESOURCE_DIR_PATH}")
        logger.info(f"[VERSION] {VERSION}")
        if config.config_user:
            for item in config.config_user.keys():
                logger.info(f"{item} : {config.config_user[item]}")
        logger.ui("未正确使用所产生的一切后果自负，保持您的肝度与日常无较大差距，本程序目前仅兼容桌面版，\
使用过程中会使用鼠标，如遇紧急情况可将鼠标划至屏幕左上角，触发安全警告强制停止")
        if self._check_enviroment():
            logger.ui("环境完整")
            self.ui.combo_choice.setEnabled(True)
            self.ui.spinB_num.setEnabled(True)
            logger.ui("移动游戏窗口后，点击下方“游戏检测”即可")
            logger.ui("请选择功能以加载内容，请确保锁定阵容")
        else:
            logger.ui("环境损坏", "error")

        logger.ui("初始化完成")
        logger.ui("主要战斗场景UI为「怀旧主题」，持续兼容部分新场景中，可在游戏内图鉴中设置")
        log_clean_up()
        remove_restart_bat_file()
        upgrade.check_latest()
        # 悬赏封印
        if config.config_user.get("悬赏封印") == "关闭":
            event_xuanshang_enable.clear()
        else:
            xuanshangfengyin.xuanshangfengyin.run()

    def qmessagbox_update_func(self, level: str, msg: str) -> None:
        match level:
            case "ERROR":
                QMessageBox.critical(self, level, msg)
            case "question":
                match msg:
                    case "强制缩放":
                        logger.error("游戏窗口大小不匹配")
                        choice = QMessageBox.question(
                            self,
                            "窗口大小不匹配",
                            "是否强制缩放，如不缩放，请自行靠近1136*640或者替换pic文件夹中对应素材"
                        )
                        if choice == QMessageBox.Yes:
                            logger.info("用户接受强制缩放")
                            window.force_zoom()
                        elif choice == QMessageBox.No:
                            logger.info("用户拒绝强制缩放")
                    case "更新重启":
                        logger.info("提示：更新重启")
                        if QMessageBox.question(
                            self,
                            "检测到更新包",
                            "是否更新重启，如有自己替换的素材，请在取消后手动解压更新包"
                        ) == QMessageBox.Yes:
                            logger.info("用户接受更新重启")
                            Thread(target=upgrade.restart, daemon=True).start()
                        else:
                            logger.info("用户拒绝更新重启")

    def text_print_update_func(self, msg: str, color: str) -> None:
        """输出内容至文本框

        WARN | ERROR -> 红色

        SCENE -> 绿色

        参数:
            msg(str): 文本内容
        """
        self.ui.text_print.setTextColor(color)
        self.ui.text_print.append(msg)
        # 自动换行
        self.ui.text_print.ensureCursorVisible()
        # 自动滑动到底
        self.ui.text_print.moveCursor(QTextCursor.MoveOperation.End)
        self.ui.text_print.setTextColor("black")

    def text_print_insert_func(self, msg: str):
        cursor = self.ui.text_print.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(msg)

        # 自动换行
        # self.ui.text_print.ensureCursorVisible()
        # 自动滑动到底
        # self.ui.text_print.moveCursor(QTextCursor.MoveOperation.End)
        # self.ui.text_print.setTextColor("black")

    def text_num_update_func(self, msg: str) -> None:
        """输出内容至文本框“完成情况”

        参数:
            msg (str): 文本
        """
        self.ui.text_num.setText(msg)

    @log_function_call
    def _check_enviroment(self) -> bool:
        """环境检测

        返回:
            bool: 是否完成
        """
        logger.info("环境检测中...")
        # 中文路径
        if is_Chinese_Path():
            ms.qmessagbox_update.emit("ERROR", "请在英文路径打开！")
            return False
        # 资源文件夹完整度
        if not self.is_resource_directory_complete():
            logger.ui("资源丢失", "error")
            return False
        # 游戏窗口检测
        if not self.check_game_handle():
            return False
        return True

    @log_function_call
    def is_resource_directory_complete(self) -> bool:
        """资源文件夹完整度

        返回:
            bool: 是否完整
        """
        class Package:
            def __init__(self, n: int = 0) -> None:
                self.scene_name = "tests"
                self.n: int = 0
                self.max: int = n
                self.resource_path = "tests"
                self.resource_list: list = []

        logger.info("开始检查资源")
        if not Path(RESOURCE_DIR_PATH).exists():
            return False
        P: Package
        for P in [
            FightResource(),
            baiguiyexing.BaiGuiYeXing(),
            daoguantupo.DaoGuanTuPo(),
            huodong.HuoDong(),
            jiejietupo.JieJieTuPo(),
            qiling.QiLing(),
            rilun.RiLun(),
            tansuo.TanSuo(),
            xuanshangfengyin.XuanShangFengYin(),
            yeyuanhuo.YeYuanHuo(),
            yongshengzhihai.YongShengZhiHai(),
            yuhun.YuHun(),
            yuling.YuLing(),
            zhaohuan.ZhaoHuan()
        ]:
            # 检查子文件夹
            if not Path(RESOURCE_DIR_PATH/P.resource_path).exists():
                logger.ui("资源文件夹不存在！", "error")
                ms.qmessagbox_update.emit("ERROR", "资源文件夹不存在！")
                return False
            else:
                # 检查资源文件
                for item in P.resource_list:
                    if not Path(RESOURCE_DIR_PATH/P.resource_path/f"{item}.png").exists():
                        logger.ui(f"无{P.resource_path}/{item}.png资源文件", "error")
                        ms.qmessagbox_update.emit("ERROR", f"无{P.resource_path}/{item}.png资源文件")
                        return False
        logger.info("资源完整")
        return True

    def setting_update_comboBox_func(self) -> None:
        """设置-更新模式-更改"""
        text = self.ui.setting_update_comboBox.currentText()
        logger.info(f"设置项：更新模式已更改为 {text}")
        config.config_user_changed("更新模式", text)

    def setting_download_comboBox_func(self) -> None:
        """设置-下载线路-更改"""
        text = self.ui.setting_download_comboBox.currentText()
        logger.info(f"设置项：下载线路已更改为 {text}")
        config.config_user_changed("下载线路", text)

    def setting_xuanshangfengyin_comboBox_func(self) -> None:
        """设置-悬赏封印-更改"""
        text = self.ui.setting_xuanshangfengyin_comboBox.currentText()
        if text == "关闭":
            logger.ui("成功关闭悬赏封印，重启程序后生效")
        logger.info(f"设置项：悬赏封印已更改为 {text}")
        config.config_user_changed("悬赏封印", text)

    @log_function_call
    def check_game_handle(self) -> bool:
        """游戏窗口检测

        Returns:
            bool: 检测结果
        """
        logger.info("游戏窗口检测中...")
        # 获取游戏窗口信息
        window.get_game_window_handle()
        handle_coor = window.handle_coor
        if handle_coor == (0, 0, 0, 0):
            logger.error("Game is close!")
            ms.qmessagbox_update.emit("ERROR", "请在打开游戏后点击 游戏检测！")
        elif handle_coor[0] < -9 or handle_coor[1] < 0 or handle_coor[2] < 0 or handle_coor[3] < 0:
            logger.error(f"Game is background, handle_coor:{handle_coor}")
            ms.qmessagbox_update.emit("ERROR", "请前置游戏窗口！")
        # TODO 解除窗口大小限制，待优化
        elif handle_coor[2] - handle_coor[0] != window.absolute_window_width and \
                handle_coor[3] - handle_coor[1] != window.absolute_window_height:
            ms.qmessagbox_update.emit("question", "强制缩放")
        else:
            logger.ui("游戏窗口检测成功")
            self.ui.combo_choice.setEnabled(True)
            self.ui.spinB_num.setEnabled(True)
            return True
        logger.ui("游戏窗口检测失败")
        return False

    def choice_text(self):
        """功能描述"""
        text = self.ui.combo_choice.currentText()
        self.ui.button_start.setEnabled(True)
        self.ui.spinB_num.setEnabled(True)
        self.ui.stackedWidget.setCurrentIndex(0)  # 索引0，空白
        if text == self._list_function[0]:
            # 1.御魂副本
            self._choice = 1
            logger.ui("请确保阵容稳定，已适配组队/单人 魂土、神罚副本\
                   新设备第一次接受邀请会有弹窗，需手动勾选“不再提醒”")
            self.ui.stackedWidget.setCurrentIndex(1)  # 索引1，御魂
            # 默认值
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 999)

            self.ui.button_mode_team.setEnabled(True)
            self.ui.button_mode_single.setEnabled(True)
            self.ui.button_mode_team.setChecked(True)

            self.ui.button_driver_False.setChecked(True)

            self.ui.button_passengers_2.setEnabled(True)
            self.ui.button_passengers_3.setEnabled(True)
            self.ui.button_passengers_2.setChecked(True)
        elif text == self._list_function[1]:
            # 2.组队永生之海副本
            self._choice = 2
            logger.ui("默认打手30次\n阴阳师技能自行选择，如晴明灭\n待开发：手动第一次锁定阵容")
            self.ui.stackedWidget.setCurrentIndex(1)  # 索引1，御魂
            # 默认值
            self.ui.spinB_num.setValue(30)
            self.ui.spinB_num.setRange(1, 999)
            self.ui.button_mode_team.setChecked(True)
            # TODO
            self.ui.button_mode_team.setEnabled(False)
            self.ui.button_mode_single.setEnabled(False)
            self.ui.button_driver_False.setChecked(True)
            self.ui.button_passengers_2.setChecked(True)
            self.ui.button_passengers_2.setEnabled(False)
            self.ui.button_passengers_3.setEnabled(False)
        elif text == self._list_function[2]:
            # 3.业原火副本
            self._choice = 3
            logger.ui("默认为“痴”，有“贪”“嗔”需求的，可替换resource/yeyuanhuo路径下start.png")
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 999)
        elif text == self._list_function[3]:
            # 4.御灵副本
            self._choice = 4
            logger.ui("暗神龙-周二六日\n暗白藏主-周三六日\n暗黑豹-周四六\n暗孔雀-周五六日\n绘卷期间请减少使用")
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 400)  # 桌面版上限300
        elif text == self._list_function[4]:
            # 5.个人突破
            self._choice = 5
            logger.ui("默认3胜刷新，上限30")
            # self.ui.stackedWidget.setCurrentIndex(2)  # 索引2，结界突破
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 30)
        elif text == self._list_function[5]:
            # 6.寮突破
            self._choice = 6
            now = time.strftime("%H:%M:%S")
            if now >= "21:00:00":
                logger.ui("CD无限", "warn")
                logger.ui("请尽情挑战，桌面版单账号上限100次")
                self.ui.spinB_num.setValue(100)  # 桌面版上限100
            else:
                logger.ui("CD6次", "warn")
                logger.ui("默认6次，可在每日21时后无限挑战")
                self.ui.spinB_num.setValue(6)
            self.ui.spinB_num.setRange(1, 200)
        elif text == self._list_function[6]:
            # 7.道馆突破
            self._choice = 7
            logger.ui("目前仅支持正在进行中的道馆突破，无法实现跳转道馆场景\n待开发：冷却时间、观战助威")
            self.ui.stackedWidget.setCurrentIndex(3)  # 索引3，道馆突破
            self.ui.spinB_num.setEnabled(False)
        elif text == self._list_function[7]:
            # 8.普通召唤
            self._choice = 8
            logger.ui("普通召唤，请选择十连次数")
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)
        elif text == self._list_function[8]:
            # 9.百鬼夜行
            self._choice = 9
            logger.ui("仅适用于清票，且无法指定鬼王")
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)
        elif text == self._list_function[9]:
            # 10.限时活动
            self._choice = 10
            logger.ui(
                "适用于限时活动及其他连点，请提前确保阵容完好并锁定\n\
可替换resource/huodong下的素材\n\
当前为「微光之守」"
            )
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 999)
        elif text == self._list_function[10]:
            # 11.组队日轮副本
            self._choice = 11
            logger.ui("请确保阵容稳定，仅适用于队友挂饼，不适用于极限卡速，默认打手\n待开发：手动第一次锁定阵容")
            self.ui.stackedWidget.setCurrentIndex(1)  # 索引1，御魂
            # 默认值
            self.ui.spinB_num.setValue(50)
            self.ui.spinB_num.setRange(1, 100)

            self.ui.button_mode_team.setEnabled(True)
            self.ui.button_mode_single.setEnabled(True)
            self.ui.button_mode_team.setChecked(True)

            self.ui.button_driver_False.setChecked(True)

            self.ui.button_passengers_2.setEnabled(True)
            self.ui.button_passengers_3.setEnabled(True)
            self.ui.button_passengers_2.setChecked(True)
        elif text == self._list_function[11]:
            # 12.单人探索
            self._choice = 12
            logger.ui("测试功能", "warn")
            logger.ui("提前准备好自动轮换和加成，仅单人探索")
            self.ui.spinB_num.setValue(1)
        elif text == self._list_function[12]:
            # 13.契灵
            self._choice = 13
            logger.ui(qiling.QiLing().description)
            self.ui.stackedWidget.setCurrentIndex(4)  # 索引4，契灵
            self.ui.spinB_num.setValue(1)
            self.ui.button_qiling_tancha.setChecked(True)

    def start_stop(self) -> None:
        """开始&停止按钮"""

        def start() -> None:
            """开始函数"""
            _n = self.ui.spinB_num.value()
            self.ui.text_num.clear()
            self.is_fighting(True)
            match self._choice:
                case 1:  # 御魂副本
                    _flag_drop_statistics = (
                        self.ui.button_yuhun_drop_statistics.isChecked()
                    )
                    match self.ui.buttonGroup_mode.checkedButton().text():
                        case "组队":
                            _flag_driver = (
                                self.ui.buttonGroup_driver.checkedButton().text()
                                != "否"
                            )
                            _flag_passengers = int(
                                self.ui.buttonGroup_passengers.checkedButton().text()
                            )
                            yuhun.YuHunTeam(
                                n=_n,
                                flag_driver=_flag_driver,
                                flag_passengers=_flag_passengers,
                                flag_drop_statistics=_flag_drop_statistics,
                            ).run()
                        case "单人":
                            yuhun.YuHunSingle(
                                n=_n, flag_drop_statistics=_flag_drop_statistics
                            ).run()
                case 2:  # 永生之海副本
                    _flag_drop_statistics = (
                        self.ui.button_yuhun_drop_statistics.isChecked()
                    )
                    match self.ui.buttonGroup_mode.checkedButton().text():
                        case "组队":
                            _flag_driver = (
                                self.ui.buttonGroup_driver.checkedButton().text()
                                != "否"
                            )
                            yongshengzhihai.YongShengZhiHaiTeam(
                                n=_n,
                                flag_driver=_flag_driver,
                                flag_drop_statistics=_flag_drop_statistics,
                            ).run()
                        case "单人":
                            pass
                case 3:  # 业原火
                    yeyuanhuo.YeYuanHuo(n=_n).run()
                case 4:  # 御灵
                    yuling.YuLing(n=_n).run()
                case 5:  # 个人突破
                    jiejietupo.JieJieTuPoGeRen(n=_n).run()
                case 6:  # 寮突破
                    jiejietupo.JieJieTuPoYinYangLiao(n=_n).run()
                case 7:  # 道馆突破
                    flag_guanzhan = self.ui.button_guanzhan.isChecked()
                    daoguantupo.DaoGuanTuPo(flag_guanzhan=flag_guanzhan).run()
                case 8:  # 普通召唤
                    zhaohuan.ZhaoHuan(n=_n).run()
                case 9:  # 百鬼夜行
                    baiguiyexing.BaiGuiYeXing(n=_n).run()
                case 10:  # 限时活动
                    huodong.HuoDong(n=_n).run()
                case 11:  # 组队日轮副本
                    # 是否司机（默认否）
                    # 组队人数（默认2人）
                    driver = self.ui.buttonGroup_driver.checkedButton().text()
                    _flag_driver = driver != "否"
                    _flag_passengers = int(
                        self.ui.buttonGroup_passengers.checkedButton().text()
                    )
                    rilun.RiLun(
                        n=_n,
                        flag_driver=_flag_driver,
                        flag_passengers=_flag_passengers,
                    ).run()
                case 12:  # 单人探索
                    tansuo.TanSuo(n=_n).run()
                case 13:  # 契灵
                    _flag_tancha = self.ui.button_qiling_tancha.isChecked()
                    _flag_jieqi = self.ui.button_qiling_jieqi.isChecked()
                    qiling.QiLing(
                        n=_n,
                        _flag_tancha=_flag_tancha,
                        _flag_jieqi=_flag_jieqi
                    ).run()

        def stop() -> None:
            """停止函数"""
            event_thread.set()
            logger.ui("停止中，请稍候")

        match self.ui.button_start.text():
            case "开始":
                event_thread.clear()
                start()
            case "停止":
                stop()

    def is_fighting(self, flag: bool):
        """程序是否运行中，启用/禁用其他控件"""
        if flag:
            self.ui.button_start.setText("停止")  # 进行中
        else:
            self.ui.button_start.setText("开始")
        for item in [
            self.ui.combo_choice,
            self.ui.spinB_num,
            # self.ui.button_start,
            self.ui.button_mode_team,
            self.ui.button_mode_single,
            self.ui.button_driver_False,
            self.ui.button_driver_True,
            self.ui.button_passengers_2,
            self.ui.button_passengers_3,
            self.ui.button_yuhun_drop_statistics,
        ]:
            item.setEnabled(not flag)
        return

    def _yuhun_mode_change(self):
        if self.ui.buttonGroup_mode.checkedButton().text() == "组队":
            _flag = True
        if self.ui.buttonGroup_mode.checkedButton().text() == "单人":
            _flag = False
        self.ui.button_driver_False.setEnabled(_flag)
        self.ui.button_driver_True.setEnabled(_flag)
        self.ui.button_passengers_2.setEnabled(_flag)
        self.ui.button_passengers_3.setEnabled(_flag)

    def tips_yuhun_driver(self):
        if self.ui.buttonGroup_driver.checkedButton().text() == "是":
            self.ui.label_tips.setText("司机请在组队界面等待，\n并开始程序")
            self.ui.label_tips.show()
        else:
            self.ui.label_tips.hide()

    def open_GitHub_address(self, *args) -> None:
        import webbrowser
        logger.info("open GitHub address.")
        webbrowser.open("https://github.com/AquamarineCyan/Onmyoji_Python")

    def closeEvent(self, event) -> None:
        """关闭程序事件（继承类）"""
        with suppress(Exception):
            logger.info("[EXIT]")
        event.accept()

    def show_update_record_window(self):
        self.update_record_ui = UpdateRecordWindow()
        self.update_record_ui.show()

    def exit(self, flag):
        if flag:
            sys.exit()


class UpdateRecordWindow(QWidget):
    """更新信息"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Update_Record()
        self.ui.setupUi(self)
        icon = QIcon()
        icon.addPixmap(QPixmap("buzhihuo.ico"))
        self.setWindowIcon(icon)
        # 关联事件
        ms.ui_update_record_textBrowser_update.connect(self.textBrowser_update)
        # 初始化
        update_record()

    def textBrowser_update(self, text: str):
        logger.info("[update record]", text)
        self.ui.textBrowser.append(text)
        self.ui.textBrowser.ensureCursorVisible()
        self.ui.textBrowser.moveCursor(QTextCursor.MoveOperation.Start)
