#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# gui.py

import sys
import time
from contextlib import suppress
from pathlib import Path

from PySide6.QtGui import QIcon, QPixmap, QTextCursor
from PySide6.QtWidgets import (QComboBox, QDialogButtonBox, QMainWindow,
                               QMessageBox, QPushButton, QWidget)

from ..package import *
from ..ui.mainui import Ui_MainWindow
from ..ui.update_record import Ui_Form as Ui_Update_Record
from ..ui.upgrade_new_version import Ui_Form as Ui_Upgrade_New_Version
from .application import APP_NAME, APP_PATH, RESOURCE_DIR_PATH, VERSION
from .config import config, is_Chinese_Path
from .decorator import log_function_call, run_in_thread
from .event import event_thread, event_ocr_init, event_xuanshang_enable
from .log import log_clean_up, logger
from .mysignal import global_ms as ms
from .mythread import WorkThread
from .restart import Restart
from .paddleocr import ocr
from .update import get_update_info, update_record
from .upgrade import upgrade
from .window import window


def get_global_icon():
    """窗口图标"""
    global_icon = QIcon()
    global_icon.addPixmap(QPixmap("buzhihuo.ico"))
    return global_icon


class MainWindow(QMainWindow):
    """主界面"""
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
        "14.觉醒副本",
    ]
    _choice: int  # 功能

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # 初始化界面
        self.setWindowIcon(get_global_icon())  # 设置图标
        self.setWindowTitle(f"{APP_NAME} - v{VERSION}")  # 版本号显示
        # 通过先启动GUI再初始化各控件，提高启动加载速度
        self.ui_init()

    @run_in_thread
    def ui_init(self):
        """初始化GUI"""
        # 初始化控件
        self.ui.combo_choice.addItems(self._list_function)
        self.ui.button_start.setEnabled(False)
        self.ui.combo_choice.setEnabled(False)
        self.ui.spin_times.setEnabled(False)
        self.ui.stackedWidget.setCurrentIndex(0)  # 索引0，空白
        self.ui.label_tips.hide()
        # 设置界面
        _setting_QComboBox_dict: dict = {
            self.ui.setting_update_comboBox: "update",
            self.ui.setting_update_download_comboBox: "update_download",
            self.ui.setting_xuanshangfengyin_comboBox: "xuanshangfengyin",
            self.ui.setting_window_style_comboBox: "window_style",
        }
        key: QComboBox
        for key, value in _setting_QComboBox_dict.items():
            key.addItems(config.config_default.model_dump()[value])
            key.setCurrentText(config.config_user.model_dump().get(value))
        _status = config.config_user.model_dump().get("remember_last_choice")
        logger.info(f"_status{_status}")
        if _status == -1:
            _flag_check = False
        else:
            _flag_check = True
        self.ui.setting_remember_last_choice_button.setChecked(_flag_check)
        self.ui.label_GitHub_address.setToolTip("通过浏览器打开")

        # 自定义信号
        # 弹窗更新
        ms.main.qmessagbox_update.connect(self.qmessagbox_update_func)
        # 更新文本
        ms.main.ui_text_info_update.connect(self.ui_text_info_update_func)
        # 运行状态更新
        ms.main.is_fighting_update.connect(self.is_fighting)
        # 完成次数更新
        ms.main.ui_text_completion_times_update.connect(self.ui_text_completion_times_update_func)
        # 退出程序
        ms.main.sys_exit.connect(self.exit_func)
        # 显示更新窗口
        ms.upgrade_new_version.show_ui.connect(self.show_upgrade_new_version_window)

        # 事件连接
        # 环境检测按钮
        self.ui.button_game_handle.clicked.connect(self.check_game_handle)
        # 开始按钮
        self.ui.button_start.clicked.connect(self.start_stop)
        # 功能选择事件
        self.ui.combo_choice.currentIndexChanged.connect(self.choice_description)
        # 重启
        self.ui.button_restart.clicked.connect(self.app_restart_func)
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
        self.ui.setting_update_download_comboBox.currentIndexChanged.connect(
            self.setting_update_download_comboBox_func
        )
        # 悬赏封印
        self.ui.setting_xuanshangfengyin_comboBox.currentIndexChanged.connect(
            self.setting_xuanshangfengyin_comboBox_func
        )
        # 界面风格
        self.ui.setting_window_style_comboBox.currentIndexChanged.connect(
            self.setting_window_style_comboBox_func
        )
        # 记忆上次所选功能
        self.ui.setting_remember_last_choice_button.clicked.connect(
            self.setting_remember_last_choice_func
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
        logger.info(f"config_user: {config.config_user}")
        logger.ui("未正确使用所产生的一切后果自负，保持您的肝度与日常无较大差距，本程序目前仅兼容桌面版，\
使用过程中会使用鼠标，如遇紧急情况可将鼠标划至屏幕左上角，触发安全警告强制停止")
        if self._check_enviroment():
            logger.ui("环境完整")
            self.ui.combo_choice.setEnabled(True)
            self.ui.spin_times.setEnabled(True)
            logger.ui("移动游戏窗口后，点击下方“游戏检测”即可")
            logger.ui("请选择功能以加载内容，请确保锁定阵容")
        else:
            logger.ui("环境损坏", "error")

        logger.ui("初始化完成")
        logger.ui("主要战斗场景UI为「怀旧主题」，持续兼容部分新场景中，可在游戏内图鉴中设置")
        if config.config_user.remember_last_choice > 0:
            self.ui.combo_choice.setCurrentIndex(config.config_user.remember_last_choice - 1)
        log_clean_up()
        Restart().move_screenshot()
        upgrade.check_latest()
        get_update_info()
        # 悬赏封印
        if config.config_user.xuanshangfengyin == "关闭":
            event_xuanshang_enable.clear()
        else:
            task_xuanshangfengyin.task_start()
        # 文字识别
        ocr.init()

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
                            WorkThread(func=upgrade.restart).start()
                        else:
                            logger.info("用户拒绝更新重启")

    def ui_text_info_update_func(self, msg: str, color: str) -> None:
        """输出内容至文本框

        WARN | ERROR -> 红色

        SCENE -> 绿色

        参数:
            msg(str): 文本内容
        """
        widget = self.ui.text_info
        widget.setTextColor(color)
        widget.append(msg)
        # 自动换行
        widget.ensureCursorVisible()
        # 自动滑动到底
        widget.moveCursor(QTextCursor.MoveOperation.End)
        widget.setTextColor("black")

    def ui_text_completion_times_update_func(self, msg: str) -> None:
        """输出内容至文本框`完成次数`

        参数:
            msg (str): 文本
        """
        self.ui.text_completion_times.setText(msg)

    def ui_spin_times_set_value_func(self, current: int = 1, min: int = None, max: int = None):
        widget = self.ui.spin_times
        widget.setValue(current)
        if min is not None:
            widget.setMinimum(min)
        if max is not None:
            widget.setMaximum(max)

    @log_function_call
    def _check_enviroment(self) -> bool:
        """环境检测

        返回:
            bool: 是否完成
        """
        logger.info("环境检测中...")
        # 中文路径
        if is_Chinese_Path():
            ms.main.qmessagbox_update.emit("ERROR", "请在英文路径打开！")
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
        logger.info("开始检查资源")
        if not Path(RESOURCE_DIR_PATH).exists():
            return False
        _package_resource_list = get_package_resource_list()
        for P in _package_resource_list:
            # 检查子文件夹
            if not Path(RESOURCE_DIR_PATH/P.resource_path).exists():
                logger.ui("资源文件夹不存在！", "error")
                ms.main.qmessagbox_update.emit("ERROR", "资源文件夹不存在！")
                return False
            else:
                # 检查资源文件
                for item in P.resource_list:
                    if not Path(RESOURCE_DIR_PATH/P.resource_path/f"{item}.png").exists():
                        logger.ui(f"未找到资源：{P.resource_path}/{item}.png", "error")
                        ms.main.qmessagbox_update.emit("ERROR", f"无{P.resource_path}/{item}.png资源文件")
                        return False
        logger.info("资源完整")
        return True

    def setting_update_comboBox_func(self) -> None:
        """设置-更新模式-更改"""
        text = self.ui.setting_update_comboBox.currentText()
        logger.info(f"设置项：更新模式已更改为 {text}")
        config.config_user_changed("update", text)

    def setting_update_download_comboBox_func(self) -> None:
        """设置-下载线路-更改"""
        text = self.ui.setting_update_download_comboBox.currentText()
        logger.info(f"设置项：下载线路已更改为 {text}")
        config.config_user_changed("update_download", text)

    def setting_xuanshangfengyin_comboBox_func(self) -> None:
        """设置-悬赏封印-更改"""
        text = self.ui.setting_xuanshangfengyin_comboBox.currentText()
        if text == "关闭":
            logger.ui("成功关闭悬赏封印，重启程序后生效")
        logger.info(f"设置项：悬赏封印已更改为 {text}")
        config.config_user_changed("xuanshangfengyin", text)

    def setting_window_style_comboBox_func(self) -> None:
        """设置-界面风格-更改"""
        text = self.ui.setting_window_style_comboBox.currentText()
        logger.info(f"设置项：界面风格已更改为 {text}")
        config.config_user_changed("window_style", text)

    def setting_remember_last_choice_func(self) -> None:
        """设置-记忆上次所选功能-更改"""
        flag = self.ui.setting_remember_last_choice_button.isChecked()
        if flag:
            _text = "开启"
            _status = 0
        else:
            _text = "关闭"
            _status = -1
        logger.info(f"设置项：记忆上次所选功能已更改为 {_text}")
        config.config_user_changed("remember_last_choice", _status)

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
            ms.main.qmessagbox_update.emit("ERROR", "请在打开游戏后点击 游戏检测！")
        elif handle_coor[0] < -9 or handle_coor[1] < 0 or handle_coor[2] < 0 or handle_coor[3] < 0:
            logger.error(f"Game is background, handle_coor:{handle_coor}")
            ms.main.qmessagbox_update.emit("ERROR", "请前置游戏窗口！")
        # TODO 解除窗口大小限制，待优化
        elif handle_coor[2] - handle_coor[0] != window.absolute_window_width and \
                handle_coor[3] - handle_coor[1] != window.absolute_window_height:
            ms.main.qmessagbox_update.emit("question", "强制缩放")
        else:
            logger.ui("游戏窗口检测成功")
            self.ui.combo_choice.setEnabled(True)
            self.ui.spin_times.setEnabled(True)
            return True
        logger.ui("游戏窗口检测失败")
        return False

    def choice_description(self):
        """功能描述"""
        try:
            self._choice = self._list_function.index(self.ui.combo_choice.currentText()) + 1
        except ValueError:  # for safe
            self._choice = 0
        if config.config_user.remember_last_choice != -1:
            config.config_user_changed("remember_last_choice", self._choice)
        self.ui.button_start.setEnabled(True)
        self.ui.spin_times.setEnabled(True)
        self.ui_spin_times_set_value_func(1, 1, 999)
        self.ui.stackedWidget.setCurrentIndex(0)  # 索引0，空白

        match self._choice:
            case 1:  # 御魂副本
                logger.ui(YuHun.description)
                self.ui.stackedWidget.setCurrentIndex(1)  # 索引1，御魂

                self.ui.button_mode_team.setEnabled(True)
                self.ui.button_mode_single.setEnabled(True)
                self.ui.button_mode_team.setChecked(True)

                self.ui.button_driver_False.setChecked(True)

                self.ui.button_passengers_2.setEnabled(True)
                self.ui.button_passengers_3.setEnabled(True)
                self.ui.button_passengers_2.setChecked(True)
            case 2:  # 组队永生之海副本
                logger.ui(YongShengZhiHai.description)
                self.ui.stackedWidget.setCurrentIndex(1)  # 索引1，御魂
                self.ui_spin_times_set_value_func(30)
                self.ui.button_mode_team.setChecked(True)
                # TODO
                self.ui.button_mode_team.setEnabled(False)
                self.ui.button_mode_single.setEnabled(False)
                self.ui.button_driver_False.setChecked(True)
                self.ui.button_passengers_2.setChecked(True)
                self.ui.button_passengers_2.setEnabled(False)
                self.ui.button_passengers_3.setEnabled(False)
            case 3:  # 业原火副本
                logger.ui(YeYuanHuo.description)
            case 4:  # 御灵副本
                logger.ui(YuLing.description)
                self.ui_spin_times_set_value_func(1, 1, 400)  # 桌面版上限300
            case 5:  # 个人突破
                logger.ui(JieJieTuPoGeRen.description)
                # self.ui.stackedWidget.setCurrentIndex(2)  # 索引2，结界突破
                self.ui_spin_times_set_value_func(1, 1, 30)
            case 6:  # 寮突破
                now = time.strftime("%H:%M:%S")
                if now >= "21:00:00":
                    logger.ui("CD无限", "warn")
                    logger.ui("请尽情挑战，桌面版单账号上限100次")
                    _current = 100
                else:
                    logger.ui("CD 6次", "warn")
                    logger.ui("默认6次，可在每日21时后无限挑战")
                    _current = 6
                self.ui_spin_times_set_value_func(_current, 1, 200)
            case 7:  # 道馆突破
                logger.ui(DaoGuanTuPo.description)
                self.ui.stackedWidget.setCurrentIndex(3)  # 索引3，道馆突破
                self.ui.spin_times.setEnabled(False)
            case 8:  # 普通召唤
                logger.ui(ZhaoHuan.description)
            case 9:  # 百鬼夜行
                logger.ui(BaiGuiYeXing.description)
            case 10:  # 限时活动
                logger.ui(HuoDong.description)
            case 11:  # 组队日轮副本
                self.ui.stackedWidget.setCurrentIndex(1)  # 索引1，御魂
                self.ui_spin_times_set_value_func(50)

                self.ui.button_mode_team.setEnabled(True)
                self.ui.button_mode_single.setEnabled(True)
                self.ui.button_mode_team.setChecked(True)

                self.ui.button_driver_False.setChecked(True)

                self.ui.button_passengers_2.setEnabled(True)
                self.ui.button_passengers_3.setEnabled(True)
                self.ui.button_passengers_2.setChecked(True)
            case 12:  # 单人探索
                logger.ui(TanSuo.description)
            case 13:  # 契灵
                logger.ui(QiLing.description)
                self.ui.stackedWidget.setCurrentIndex(4)  # 索引4，契灵
                self.ui.button_qiling_jieqi.setChecked(True)
                self.ui.combo_qiling_jieqi_stone.addItem("镇墓兽")
                self.ui.spin_qiling_jieqi_stone.setValue(1)
            case 14:  # 觉醒副本
                logger.ui(JueXing.description)

    def start_stop(self) -> None:
        """开始&停止按钮"""

        def start() -> None:
            """开始函数"""
            _n = self.ui.spin_times.value()
            self.ui.text_completion_times.clear()
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
                            YuHunTeam(
                                n=_n,
                                flag_driver=_flag_driver,
                                flag_passengers=_flag_passengers,
                                flag_drop_statistics=_flag_drop_statistics,
                            ).task_start()
                        case "单人":
                            YuHunSingle(
                                n=_n, flag_drop_statistics=_flag_drop_statistics
                            ).task_start()
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
                            YongShengZhiHaiTeam(
                                n=_n,
                                flag_driver=_flag_driver,
                                flag_drop_statistics=_flag_drop_statistics,
                            ).task_start()
                        case "单人":
                            pass
                case 3:  # 业原火
                    YeYuanHuo(n=_n).task_start()
                case 4:  # 御灵
                    YuLing(n=_n).task_start()
                case 5:  # 个人突破
                    JieJieTuPoGeRen(n=_n).task_start()
                case 6:  # 寮突破
                    JieJieTuPoYinYangLiao(n=_n).task_start()
                case 7:  # 道馆突破
                    flag_guanzhan = self.ui.button_guanzhan.isChecked()
                    DaoGuanTuPo(flag_guanzhan=flag_guanzhan).task_start()
                case 8:  # 普通召唤
                    ZhaoHuan(n=_n).task_start()
                case 9:  # 百鬼夜行
                    BaiGuiYeXing(n=_n).task_start()
                case 10:  # 限时活动
                    HuoDong(n=_n).task_start()
                case 11:  # 组队日轮副本
                    # 是否司机（默认否）
                    # 组队人数（默认2人）
                    driver = self.ui.buttonGroup_driver.checkedButton().text()
                    _flag_driver = driver != "否"
                    _flag_passengers = int(
                        self.ui.buttonGroup_passengers.checkedButton().text()
                    )
                    RiLun(
                        n=_n,
                        flag_driver=_flag_driver,
                        flag_passengers=_flag_passengers,
                    ).task_start()
                case 12:  # 单人探索
                    TanSuo(n=_n).task_start()
                case 13:  # 契灵
                    _flag_tancha = self.ui.button_qiling_tancha.isChecked()
                    _flag_jieqi = self.ui.button_qiling_jieqi.isChecked()
                    _stone_pokemon = self.ui.combo_qiling_jieqi_stone.currentText()
                    _stone_numbers = self.ui.spin_qiling_jieqi_stone.value()
                    QiLing(
                        n=_n,
                        _flag_tancha=_flag_tancha,
                        _flag_jieqi=_flag_jieqi,
                        _stone_pokemon=_stone_pokemon,
                        _stone_numbers=_stone_numbers,
                    ).task_start()
                case 14:  # 觉醒副本
                    JueXing(n=_n).task_start()

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
        item: QWidget
        for item in [
            self.ui.combo_choice,
            self.ui.spin_times,
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

    def app_restart_func(self):
        Restart().app_restart()

    def open_GitHub_address(self, *args) -> None:
        import webbrowser
        logger.info("open GitHub address.")
        webbrowser.open("https://github.com/AquamarineCyan/Onmyoji_Python")

    def exit_func(self):
        sys.exit()

    def closeEvent(self, event) -> None:
        """关闭程序事件（继承类）"""
        with suppress(Exception):
            logger.info("[EXIT]")
        event.accept()

    def show_update_record_window(self):
        self.update_record_ui = UpdateRecordWindow()
        self.update_record_ui.show()

    def show_upgrade_new_version_window(self):
        self.upgrade_new_version_ui = UpgradeNewVersionWindow()
        self.upgrade_new_version_ui.show()


class UpdateRecordWindow(QWidget):
    """更新记录"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Update_Record()
        self.ui.setupUi(self)
        self.setWindowIcon(get_global_icon())
        # 关联事件
        ms.update_record.text_update.connect(self.textBrowser_update_func)
        ms.update_record.text_markdown_update.connect(self.textBrowser_markdown_update_func)
        # 初始化
        update_record()

    def textBrowser_update_func(self, text: str):
        logger.info(f"[update record]\n{text}")
        widget = self.ui.textBrowser
        widget.append(text)
        widget.ensureCursorVisible()
        widget.moveCursor(QTextCursor.MoveOperation.Start)

    def textBrowser_markdown_update_func(self, msg: str):
        widget = self.ui.textBrowser
        widget.setMarkdown(msg)


class UpgradeNewVersionWindow(QWidget):
    """更新新版本"""

    def __init__(self):
        super().__init__()
        self.ui = Ui_Upgrade_New_Version()
        self.ui.setupUi(self)
        self.setWindowIcon(get_global_icon())

        button_update = QPushButton("下载更新", self)
        button_download = QPushButton("仅下载", self)
        button_cancel = QPushButton("忽略本次", self)

        self.ui.buttonBox.addButton(button_update, QDialogButtonBox.ButtonRole.AcceptRole)
        self.ui.buttonBox.addButton(button_download, QDialogButtonBox.ButtonRole.AcceptRole)
        self.ui.buttonBox.addButton(button_cancel, QDialogButtonBox.ButtonRole.RejectRole)
        self.ui.progressBar.hide()

        button_update.clicked.connect(self.button_update_clicked_func)
        button_download.clicked.connect(self.button_download_clicked_func)
        button_cancel.clicked.connect(self.close)
        ms.upgrade_new_version.text_update.connect(self.textBrowser_update_func)
        ms.upgrade_new_version.text_insert.connect(self.textBrowser_insert_func)
        ms.upgrade_new_version.progressBar_update.connect(self.progressBar_update_func)
        ms.upgrade_new_version.close_ui.connect(self.close)

        ms.upgrade_new_version.text_update.emit(f"v{upgrade.new_version}\n{upgrade.new_version_info}")

    def textBrowser_update_func(self, msg: str) -> None:
        """输出内容至文本框

        参数:
            msg(str): 文本内容
        """
        self.ui.textBrowser.append(msg)
        self.ui.textBrowser.ensureCursorVisible()
        self.ui.textBrowser.moveCursor(QTextCursor.MoveOperation.End)

    def textBrowser_insert_func(self, msg: str):
        """插入内容

        参数:
            msg (str): 文本内容
        """
        cursor = self.ui.textBrowser.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(msg)

    def progressBar_update_func(self, value: int):
        """更新进度条

        参数:
            value (int): 百分比
        """
        self.ui.progressBar.setValue(value)

    def progressBar_show_func(self):
        if self.ui.progressBar.isHidden():
            self.ui.progressBar.show()

    def button_update_clicked_func(self):
        self.progressBar_show_func()
        upgrade.ui_update_func()

    def button_download_clicked_func(self):
        self.progressBar_show_func()
        upgrade.ui_download_func()

    def closeEvent(self, event):
        logger.info("[EXIT]")
        event.accept()
