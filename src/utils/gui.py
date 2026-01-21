from contextlib import suppress
from enum import Enum
from pathlib import Path

from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QTextCursor
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QWidget,
)

from ..package import *  # noqa: F403
from ..ui import icon_rc  # noqa: F401
from ..ui.mainui_ui import Ui_MainWindow
from ..ui.update_record_widget import UpdateRecordWindow
from ..ui.upgrade_new_version_widget import UpgradeNewVersionWidget
from .application import APP_NAME, APP_PATH, HELP_DOC_LINK, HOME_PAGE_LINK, QQ_GROUP_LINK, VERSION
from .config import config
from .decorator import log_function_call, run_in_thread
from .event import event_thread
from .function import is_Chinese_Path
from .global_task import global_task
from .keyboard_listener import KeyListenerThread
from .log import log_clean_up, logger
from .mysignal import global_ms as ms
from .mythread import WorkThread
from .paddleocr import check_ocr_folder, ocr
from .restart import Restart
from .screenshot import ScreenShot
from .shortcut import create_desktop_shortcut
from .update import get_update_info
from .upgrade import upgrade
from .window import window_manager


class GameFunction(Enum):
    """游戏功能"""

    YUHUN = 1  # 御魂副本
    YONGSHENGZHIHAI = 2  # 永生之海副本
    YEYUANHUO = 3  # 业原火副本
    YULING = 4  # 御灵副本
    GERENTUPO = 5  # 个人突破
    LIAOTUPO = 6  # 寮突破
    DAOGUANTUPO = 7  # 道馆突破
    ZHAOHUAN = 8  # 普通召唤
    BAIGUIYEXING = 9  # 百鬼夜行
    HUODONG = 10  # 限时活动
    RILUN = 11  # 日轮副本
    TANSUO = 12  # 单人探索
    QILING = 13  # 契灵之境
    JUEXING = 14  # 觉醒副本
    LIUDAOZHIMEN = 15  # 六道之门速刷
    DOUJI = 16  # 斗技自动上阵
    YINGJIESHILIAN = 17  # 英杰试炼
    HUIJUAN = 18  # 绘卷刷分


class StackedWidgetIndex(Enum):
    """高级设置窗口索引"""

    NONE = 0
    YUHUN = 1
    JIEJIETUPO = 2
    DAOGUANTUPO = 3
    QILING = 4
    YINGJIESHILIAN = 5
    HUIJUAN = 6


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
        "11.日轮副本",
        "12.单人探索",
        "13.契灵之境",
        "14.觉醒副本",
        "15.六道之门速刷",
        "16.斗技自动上阵",
        "17.英杰试炼",
        "18.绘卷刷分",
    ]

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icon/buzhihuo.jpg"))
        self.setWindowTitle(f"{APP_NAME} - v{VERSION} - {config.user.game_language}")

        # 通过先启动GUI再初始化各控件，提高启动加载速度
        self.ui_init()
        self.software_init()

    def ui_init(self):
        """初始化GUI"""
        self.ui.combo_choice.addItems(self._list_function)
        self.ui.button_start.setEnabled(False)
        self.ui.combo_choice.setEnabled(False)
        self.ui.spin_times.setEnabled(False)

        self.ui.stackedWidget.setCurrentIndex(0)  # 索引0，空白
        gerentupo_level_list = JieJieTuPoGeRen.get_level_list()
        self.ui.comboBox_jiejietupo_current_level.addItems(gerentupo_level_list)
        self.ui.comboBox_jiejietupo_target_level.addItems(gerentupo_level_list)
        self.ui.comboBox_huijuan_jiejietupo_current_level.addItems(gerentupo_level_list)
        self.ui.comboBox_huijuan_jiejietupo_target_level.addItems(gerentupo_level_list)
        self.ui.combo_qiling_jieqi_stone.addItems(QiLing.get_pockmon_list())

        self._init_settings()
        self._init_signals()
        self._init_events()

        self.key_listener = KeyListenerThread()
        ms.main.key_pressed.connect(self._shortcut_handle)
        self.key_listener.start()

    def _init_settings(self):
        """初始化设置"""
        _setting_QComboBox_dict = {
            self.ui.setting_language_comboBox: "game_language",
            self.ui.setting_update_comboBox: "update",
            self.ui.setting_update_download_comboBox: "update_download",
            self.ui.setting_xuanshangfengyin_comboBox: "xuanshangfengyin",
            self.ui.setting_window_style_comboBox: "window_style",
            self.ui.setting_shortcut_start_stop_comboBox: "shortcut_start_stop",
        }
        for key, value in _setting_QComboBox_dict.items():
            key.addItems(config.default.model_dump()[value])
            key.setCurrentText(config.user.model_dump().get(value))

        self.ui.setting_interaction_mode_comboBox.addItems(config.default.model_dump()["interaction_mode"]["mode"])
        self.ui.setting_interaction_mode_comboBox.setCurrentText(config.user.model_dump()["interaction_mode"]["mode"])

        _status = config.user.model_dump().get("interaction_mode").get("frontend").get("force_window")
        self.ui.setting_interaction_mode_frontend_button.setChecked(_status)

        _status = config.user.model_dump().get("interaction_mode").get("backend").get("prevent_sleep")
        self.ui.setting_interaction_mode_backend_button.setChecked(_status)

        _status = config.user.model_dump().get("remember_last_choice")
        self.ui.setting_remember_last_choice_button.setChecked(_status != -1)

        _status = config.user.model_dump().get("win_toast")
        self.ui.setting_win_toast_button.setChecked(_status)

        _restart_msg = "重启生效"
        self.ui.setting_language_comboBox.setToolTip(_restart_msg)
        self.ui.setting_update_comboBox.setToolTip(_restart_msg)
        self.ui.setting_update_download_comboBox.setToolTip(_restart_msg)
        self.ui.setting_xuanshangfengyin_comboBox.setToolTip("立即生效")
        self.ui.setting_window_style_comboBox.setToolTip(_restart_msg)

        self.ui.button_about_homePage.setToolTip("通过浏览器打开")
        self.ui.button_about_helpDoc.setToolTip("通过浏览器打开")
        self.ui.button_about_Qgroup.setToolTip("通过浏览器打开")

    def _init_signals(self):
        """初始化信号"""
        ms.main.qmessagbox_update.connect(self.qmessagbox_update_func)
        ms.main.ui_text_info_update.connect(self.ui_text_info_update_func)
        ms.main.is_fighting_update.connect(self.is_fighting)
        ms.main.ui_text_progress_update.connect(self.ui_text_progress_update_func)
        ms.main.valid_listWidget_update.connect(self.ui_valid_listWidget_update_handle)
        ms.main.sys_exit.connect(self._exit_handle)
        ms.upgrade_new_version.show_ui.connect(self.show_upgrade_new_version_window)

    def _init_events(self):
        """初始化事件"""
        self.ui.button_game_handle.clicked.connect(self.check_game_handle)
        self.ui.combo_choice.currentIndexChanged.connect(self.game_function_description)
        self.ui.button_start.clicked.connect(self.app_running)

        self.ui.buttonGroup_yuhun_mode.buttonClicked.connect(self.buttonGroup_yuhun_mode_handle)
        self.ui.buttonGroup_yuhun_driver.buttonClicked.connect(self.buttonGroup_yuhun_driver_handle)
        self.ui.buttonGroup_jiejietupo_switch.buttonClicked.connect(self.buttonGroup_jiejietupo_switch_handle)
        self.ui.button_qiling_tancha.checkStateChanged.connect(self.button_qiling_tancha_handle)
        self.ui.button_qiling_jieqi.checkStateChanged.connect(self.button_qiling_jieqi_handle)
        self.ui.buttonGroup_yingjieshilian.buttonClicked.connect(self.buttonGroup_yingjieshilian_handle)
        self.ui.buttonGroup_huijuan_jiejietupo_switch.buttonClicked.connect(
            self.buttonGroup_huijuan_jiejietupo_switch_handle
        )

        self.ui.tab_window_manager_preview_button.clicked.connect(self.preview_window)
        self.ui.tab_window_manager_apply_button.clicked.connect(self.apply_selected_window)

        self.ui.valid_pushButton.clicked.connect(self.score_handle)

        self.ui.setting_language_comboBox.currentIndexChanged.connect(self.setting_language_comboBox_handle)
        self.ui.setting_update_comboBox.currentIndexChanged.connect(self.setting_update_comboBox_handle)
        self.ui.setting_update_download_comboBox.currentIndexChanged.connect(
            self.setting_update_download_comboBox_handle
        )
        self.ui.setting_xuanshangfengyin_comboBox.currentIndexChanged.connect(
            self.setting_xuanshangfengyin_comboBox_handle
        )
        self.ui.setting_window_style_comboBox.currentIndexChanged.connect(self.setting_window_style_comboBox_hanle)
        self.ui.setting_shortcut_start_stop_comboBox.currentIndexChanged.connect(
            self.setting_shortcut_start_stop_comboBox_handle
        )
        self.ui.setting_interaction_mode_comboBox.currentIndexChanged.connect(
            self.setting_interaction_mode_comboBox_handle
        )
        self.ui.setting_remember_last_choice_button.clicked.connect(self.setting_remember_last_choice_handle)
        self.ui.setting_interaction_mode_frontend_button.clicked.connect(self.setting_interaction_mode_frontend_handle)
        self.ui.setting_interaction_mode_backend_button.clicked.connect(self.setting_interaction_mode_backend_handle)
        self.ui.setting_win_toast_button.clicked.connect(self.setting_win_toast_handle)

        self.ui.button_about_appRestart.clicked.connect(self.app_restart_handle)
        self.ui.button_about_updateRecord.clicked.connect(self.show_update_record_window)
        self.ui.button_about_shortCut.clicked.connect(create_desktop_shortcut)
        self.ui.button_about_homePage.mousePressEvent = self.open_homepage
        self.ui.button_about_helpDoc.mousePressEvent = self.open_helpdoc
        self.ui.button_about_Qgroup.mousePressEvent = self.open_Qgroup

    def _shortcut_handle(self, key: str):
        """快捷键处理"""
        try:
            logger.info(f"Key pressed: {key}")
            if key.lower() == config.user.shortcut_start_stop.lower():
                logger.info(f"Shortcut key pressed: {config.user.shortcut_start_stop}")
                self.app_running()
        except AttributeError:
            # 特殊键处理
            logger.warning(f"Key pressed: {key}")

    @log_function_call
    @run_in_thread
    def software_init(self) -> None:
        """程序初始化"""
        logger.info(f"application path: {APP_PATH}")
        logger.info(f"resource path: {config.resource_dir}")
        logger.info(f"[VERSION] {VERSION}")
        logger.info(f"config_user: {config.user}")
        logger.ui_warn("未正确使用所产生的一切后果自负，保持您的肝度与日常无较大差距，本程序目前仅兼容桌面版")
        logger.ui("程序初始化中，请稍候")
        log_clean_up()

        # 优先在新线程中检查更新
        upgrade.check_latest()
        get_update_info()

        if not self.software_selfcheck():
            logger.ui_error("初始化失败")
            return
        logger.ui("初始化成功")

        self._global_task_init()

    def _global_task_init(self):
        """全局任务初始化"""
        window_manager.set_window_title(config.user.game_language)
        window_manager.set_gui_button_callback(self._window_button_enabled_handle)
        window_manager.set_gui_window_manager_list_callback(self.refresh_window_list)
        window_manager.screen_init()

        global_task.add(window_manager.update_window_task)
        global_task.add(XuanShangFengYin().check_task)
        global_task.start()

    def qmessagbox_update_func(self, level: str, msg: str) -> None:
        if level == "ERROR":
            QMessageBox.critical(self, level, msg)
        elif level == "question":
            if msg == "强制缩放":
                logger.error("游戏窗口大小不匹配")
                if (
                    QMessageBox.question(
                        self,
                        "窗口大小不匹配",
                        "是否强制缩放，如不缩放，请自行靠近1136*640，或者参考 README.MD 在data/myresource文件夹中添加对应素材",
                    )
                    == QMessageBox.StandardButton.Yes
                ):
                    logger.info("用户接受强制缩放")
                    window_manager.force_zoom()
                else:
                    logger.info("用户拒绝强制缩放")
            elif msg == "更新重启":
                logger.info("提示：更新重启")
                if (
                    QMessageBox.question(
                        self,
                        "检测到更新包",
                        "是否更新重启，如有自己替换的素材，请在取消后手动解压更新包",
                    )
                    == QMessageBox.StandardButton.Yes
                ):
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

    def ui_text_progress_update_func(self, msg: str) -> None:
        """输出内容至文本框`完成情况`

        参数:
            msg (str): 文本
        """
        self.ui.text_progress.setText(msg)

    def ui_spin_times_set_value_func(self, current: int = 1, min: int = 0, max: int = 99):
        widget = self.ui.spin_times
        widget.setValue(current)
        widget.setMinimum(min)
        widget.setMaximum(max)

    @log_function_call
    def software_selfcheck(self) -> bool:
        """软件自检，打开软件时调用，只执行一次

        返回:
            bool: 是否正常
        """
        # 中文路径
        if is_Chinese_Path():
            ms.main.qmessagbox_update.emit("ERROR", "请在英文路径打开！")
            return False

        # 资源文件夹完整度
        if not self.is_resource_directory_complete():
            logger.ui_error("资源丢失")
            return False

        # 检查文字识别资源
        if check_ocr_folder():
            logger.info("文字识别资源检查通过")
        else:
            logger.ui_error("未检测到文字识别资源")
            return False

        # 初始化文字识别
        if ocr.init():
            logger.info("文字识别资源初始化成功")
        else:
            logger.ui_error("文字识别资源初始化失败")
            return False

        return True

    def _window_button_enabled_handle(self):
        logger.ui("检测到游戏窗口")
        self.ui.combo_choice.setEnabled(True)
        self.ui.spin_times.setEnabled(True)

        # 记忆上次所选功能
        if config.user.remember_last_choice > 0:
            self.ui.combo_choice.setCurrentIndex(config.user.remember_last_choice - 1)

    @log_function_call
    def is_resource_directory_complete(self) -> bool:
        """资源文件夹完整度

        返回:
            bool: 是否完整
        """
        logger.info("开始检查资源")
        if not config.resource_dir.exists():
            return False

        _package_resource_list = get_package_resource_list()
        for P in _package_resource_list:
            # 检查子文件夹
            if not Path(config.resource_dir / P.resource_path).exists():
                _msg = f"资源文件夹 {config.resource_dir} 不存在！"
                logger.ui_error(_msg)
                ms.main.qmessagbox_update.emit("ERROR", _msg)
                return False

            # 检查资源文件
            p = P()
            if not p.init:
                return False

        logger.info("资源完整")
        return True

    """设置项变更回调函数"""

    def setting_language_comboBox_handle(self) -> None:
        """设置-游戏服务器-更改"""
        text = self.ui.setting_language_comboBox.currentText()
        logger.info(f"设置项：游戏服务器已更改为 {text}")
        config.update("game_language", text)

    def setting_update_comboBox_handle(self) -> None:
        """设置-更新模式-更改"""
        text = self.ui.setting_update_comboBox.currentText()
        logger.info(f"设置项：更新模式已更改为 {text}")
        config.update("update", text)

    def setting_update_download_comboBox_handle(self) -> None:
        """设置-下载线路-更改"""
        text = self.ui.setting_update_download_comboBox.currentText()
        logger.info(f"设置项：下载线路已更改为 {text}")
        config.update("update_download", text)

    def setting_xuanshangfengyin_comboBox_handle(self) -> None:
        """设置-悬赏封印-更改"""
        text = self.ui.setting_xuanshangfengyin_comboBox.currentText()
        logger.info(f"设置项：悬赏封印已更改为 {text}")
        config.update("xuanshangfengyin", text)

    def setting_window_style_comboBox_hanle(self) -> None:
        """设置-界面风格-更改"""
        text = self.ui.setting_window_style_comboBox.currentText()
        logger.info(f"设置项：界面风格已更改为 {text}")
        config.update("window_style", text)

    def setting_shortcut_start_stop_comboBox_handle(self) -> None:
        """设置-快捷键-开始/停止-更改"""
        text = self.ui.setting_shortcut_start_stop_comboBox.currentText()
        logger.info(f"设置项：快捷键-开始/停止已更改为 {text}")
        config.update("shortcut_start_stop", text)

    def setting_interaction_mode_comboBox_handle(self) -> None:
        """设置-交互模式-更改"""
        text = self.ui.setting_interaction_mode_comboBox.currentText()
        logger.info(f"设置项：交互模式已更改为 {text}")
        config.update("interaction_mode.mode", text)

    def setting_remember_last_choice_handle(self) -> None:
        """设置-记忆上次所选功能-更改"""
        flag = self.ui.setting_remember_last_choice_button.isChecked()
        if flag:
            _text = "开启"
            _status = 0
        else:
            _text = "关闭"
            _status = -1
        logger.info(f"设置项：记忆上次所选功能已更改为 {_text}")
        config.update("remember_last_choice", _status)

    def setting_interaction_mode_frontend_handle(self) -> None:
        """设置-前台运行前置游戏窗口-更改"""
        status = self.ui.setting_interaction_mode_frontend_button.isChecked()
        config.update("interaction_mode.frontend.force_window", status)

    def setting_interaction_mode_backend_handle(self) -> None:
        """设置-后台运行禁止系统休眠-更改"""
        status = self.ui.setting_interaction_mode_backend_button.isChecked()
        config.update("interaction_mode.backend.prevent_sleep", status)

    def setting_win_toast_handle(self) -> None:
        """设置-系统通知-更改"""
        flag = self.ui.setting_win_toast_button.isChecked()
        if flag:
            _text = "开启"
            _status = True
        else:
            _text = "关闭"
            _status = False
        logger.info(f"设置项：系统通知已更改为 {_text}")
        config.update("win_toast", _status)

    def check_game_handle(self):
        return window_manager.force_update()

    def game_function_description(self):
        """功能描述"""
        self.game_function_choice = GameFunction(self.ui.combo_choice.currentIndex() + 1)
        if config.user.remember_last_choice != -1:
            config.update("remember_last_choice", self.game_function_choice.value)
        self.ui.button_start.setEnabled(True)
        self.ui.spin_times.setEnabled(True)
        self.ui_spin_times_set_value_func(1, 1, 999)
        self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.NONE.value)

        match self.game_function_choice:
            case GameFunction.YUHUN:
                YuHun.description()
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.YUHUN.value)
                self.ui.button_mode_team.setEnabled(True)
                self.ui.button_mode_single.setEnabled(True)
                self.ui.button_mode_team.setChecked(True)
                self.ui.button_driver_False.setChecked(True)
                self.ui.button_passengers_2.setEnabled(True)
                self.ui.button_passengers_3.setEnabled(True)
                self.ui.button_passengers_2.setChecked(True)

            case GameFunction.YONGSHENGZHIHAI:
                YongShengZhiHai.description()
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.YUHUN.value)
                self.ui_spin_times_set_value_func(30)
                self.ui.button_mode_team.setChecked(True)
                # 只有组队，最多2人
                self.ui.button_mode_team.setEnabled(False)
                self.ui.button_mode_single.setEnabled(False)
                self.ui.button_driver_False.setChecked(True)
                self.ui.button_passengers_2.setChecked(True)
                self.ui.button_passengers_2.setEnabled(False)
                self.ui.button_passengers_3.setEnabled(False)

            case GameFunction.YEYUANHUO:
                YeYuanHuo.description()

            case GameFunction.YULING:
                YuLing.description()
                self.ui_spin_times_set_value_func(1, 1, 400)  # 桌面版上限300

            case GameFunction.GERENTUPO:
                JieJieTuPoGeRen.description()
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.JIEJIETUPO.value)
                self.ui.button_jiejietupo_switch_level.setChecked(True)
                self.ui.button_jiejietupo_fail.setChecked(True)

                self.ui.button_jiejietupo_refresh_rule_3.setChecked(True)
                # TODO
                self.ui.button_jiejietupo_refresh_rule_6.hide()
                self.ui.button_jiejietupo_refresh_rule_9.hide()
                self.buttonGroup_jiejietupo_switch_handle()
                self.ui_spin_times_set_value_func(1, 1, 30)

            case GameFunction.LIAOTUPO:
                times = JieJieTuPoYinYangLiao.description()
                self.ui_spin_times_set_value_func(times, 1, 200)

            case GameFunction.DAOGUANTUPO:
                DaoGuanTuPo.description()
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.DAOGUANTUPO.value)
                self.ui.spin_times.setEnabled(False)

            case GameFunction.ZHAOHUAN:
                ZhaoHuan.description()

            case GameFunction.BAIGUIYEXING:
                BaiGuiYeXing.description()

            case GameFunction.HUODONG:
                HuoDong.description()
                self.ui_spin_times_set_value_func(1, 1, 9999)

            case GameFunction.RILUN:
                RiLun.description()
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.YUHUN.value)
                self.ui_spin_times_set_value_func(50)
                self.ui.button_mode_team.setEnabled(True)
                self.ui.button_mode_single.setEnabled(True)
                self.ui.button_mode_team.setChecked(True)
                self.ui.button_driver_False.setChecked(True)
                self.ui.button_passengers_2.setEnabled(True)
                self.ui.button_passengers_3.setEnabled(True)
                self.ui.button_passengers_2.setChecked(True)

            case GameFunction.TANSUO:
                TanSuo.description()

            case GameFunction.QILING:
                QiLing.description()
                self.ui.spin_times.setEnabled(False)
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.QILING.value)
                # 只是为了触发事件
                self.ui.button_qiling_tancha.setChecked(True)
                self.ui.button_qiling_tancha.setChecked(False)
                self.ui.button_qiling_jieqi.setChecked(True)
                self.ui.button_qiling_jieqi.setChecked(False)
                self.ui.spin_qiling_jieqi_stone.setValue(0)

            case GameFunction.JUEXING:
                JueXing.description()

            case GameFunction.LIUDAOZHIMEN:
                LiuDaoZhiMen.description()

            case GameFunction.DOUJI:
                DouJi.description()

            case GameFunction.YINGJIESHILIAN:
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.YINGJIESHILIAN.value)
                self.ui.button_yingjieshilian_skill.setChecked(True)
                self.buttonGroup_yingjieshilian_handle()

            case GameFunction.HUIJUAN:
                HuiJuan.description()
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.HUIJUAN.value)
                self.ui.button_huijuan_jiejietupo_switch_level.setChecked(True)
                self.ui.button_huijuan_jiejietupo_fail.setChecked(True)
                self.ui.button_huijuan_jiejietupo_switch_rule.setChecked(False)

    def _app_start(self) -> None:
        # 没有选功能前禁止通过快捷键启动程序
        if self.ui.combo_choice.currentIndex() == -1:
            logger.ui_error("请选择功能")
            return

        n = self.ui.spin_times.value()
        self.ui.text_progress.clear()
        self.is_fighting(True)

        match self.game_function_choice:
            case GameFunction.YUHUN:
                if self.ui.buttonGroup_yuhun_mode.checkedButton() == self.ui.button_mode_team:
                    driver = self.ui.buttonGroup_yuhun_driver.checkedButton() == self.ui.button_driver_True
                    passengers = int(self.ui.buttonGroup_yuhun_passengers.checkedButton().text())
                    YuHunTeam(n=n, flag_driver=driver, flag_passengers=passengers).task_start()
                else:
                    YuHunSingle(n=n).task_start()

            case GameFunction.YONGSHENGZHIHAI:
                if self.ui.buttonGroup_yuhun_mode.checkedButton() == self.ui.button_mode_team:
                    driver = self.ui.buttonGroup_yuhun_driver.checkedButton() == self.ui.button_driver_True
                    YongShengZhiHaiTeam(n=n, flag_driver=driver).task_start()

            case GameFunction.YEYUANHUO:
                YeYuanHuo(n=n).task_start()

            case GameFunction.YULING:
                YuLing(n=n).task_start()

            case GameFunction.GERENTUPO:
                flag_refresh_need: int = 0
                current_level = target_level = 57
                if self.ui.buttonGroup_jiejietupo_switch.checkedButton() == self.ui.button_jiejietupo_switch_level:
                    current_level = int(self.ui.comboBox_jiejietupo_current_level.currentText())
                    target_level = int(self.ui.comboBox_jiejietupo_target_level.currentText())
                else:
                    # 3胜
                    flag_refresh_need = int(self.ui.buttonGroup_jiejietupo_refresh_rule.checkedButton().text()[0])
                JieJieTuPoGeRen(
                    n=n,
                    flag_refresh_rule=flag_refresh_need,
                    flag_current_level=current_level,
                    flag_target_level=target_level,
                    flag_first_round_failure=self.ui.button_jiejietupo_fail.isChecked(),
                ).task_start()

            case GameFunction.LIAOTUPO:
                JieJieTuPoYinYangLiao(n=n).task_start()

            case GameFunction.DAOGUANTUPO:
                flag_guanzhan = self.ui.button_guanzhan.isChecked()
                DaoGuanTuPo(flag_guanzhan=flag_guanzhan).task_start()

            case GameFunction.ZHAOHUAN:
                ZhaoHuan(n=n).task_start()

            case GameFunction.BAIGUIYEXING:
                BaiGuiYeXing(n=n).task_start()

            case GameFunction.HUODONG:
                HuoDong(n=n).task_start()

            case GameFunction.RILUN:
                if self.ui.buttonGroup_yuhun_mode.checkedButton() == self.ui.button_mode_team:
                    driver = self.ui.buttonGroup_yuhun_driver.checkedButton() == self.ui.button_driver_True
                    passengers = int(self.ui.buttonGroup_yuhun_passengers.checkedButton().text())
                    RiLunTeam(n=n, flag_driver=driver, flag_passengers=passengers).task_start()
                else:
                    RiLunSingle(n=n).task_start()

            case GameFunction.TANSUO:
                TanSuo(n=n).task_start()

            case GameFunction.QILING:
                _tancha = self.ui.button_qiling_tancha.isChecked()
                tancha_times = self.ui.spin_qiling_tancha.value()
                _jieqi = self.ui.button_qiling_jieqi.isChecked()
                stone_pokemon = self.ui.combo_qiling_jieqi_stone.currentText()
                stone_numbers = self.ui.spin_qiling_jieqi_stone.value()
                QiLing(
                    n=tancha_times,
                    if_tancha=_tancha,
                    if_jieqi=_jieqi,
                    stone_pokemon=stone_pokemon,
                    stone_numbers=stone_numbers,
                ).task_start()

            case GameFunction.JUEXING:
                JueXing(n=n).task_start()

            case GameFunction.LIUDAOZHIMEN:
                LiuDaoZhiMen(n=n).task_start()

            case GameFunction.DOUJI:
                DouJi(n=n).task_start()

            case GameFunction.YINGJIESHILIAN:
                if self.ui.buttonGroup_yingjieshilian.checkedButton() == self.ui.button_yingjieshilian_skill:
                    BingZangMiJing(n=n).task_start()
                else:
                    GuiBingYanWu(n=n).task_start()

            case GameFunction.HUIJUAN:
                flag_refresh_need: int = 0
                current_level = target_level = 57
                if (
                    self.ui.buttonGroup_huijuan_jiejietupo_switch.checkedButton()
                    == self.ui.button_huijuan_jiejietupo_switch_level
                ):
                    current_level = int(self.ui.comboBox_huijuan_jiejietupo_current_level.currentText())
                    target_level = int(self.ui.comboBox_huijuan_jiejietupo_target_level.currentText())
                else:
                    flag_refresh_need = 3
                HuiJuan(
                    n=n,
                    loop_count=self.ui.huijuan_tansuo_spin_times.value(),
                    flag_refresh_rule=flag_refresh_need,
                    flag_current_level=current_level,
                    flag_target_level=target_level,
                    flag_first_round_failure=self.ui.button_huijuan_jiejietupo_fail.isChecked(),
                ).task_start()

    def _app_stop(self) -> None:
        event_thread.set()
        logger.ui("停止中，请稍候")

    def app_running(self) -> None:
        if self.ui.button_start.text() == "开始":
            event_thread.clear()
            self._app_start()
        else:
            self._app_stop()

    def is_fighting(self, flag: bool):
        """程序是否运行中，启用/禁用其他控件"""
        if flag:
            self.ui.button_start.setText("停止")  # 进行中
        else:
            self.ui.button_start.setText("开始")
        item: QWidget
        for item in [
            # 主界面
            self.ui.combo_choice,
            self.ui.spin_times,
            # 御魂
            self.ui.button_mode_team,
            self.ui.button_mode_single,
            self.ui.button_driver_False,
            self.ui.button_driver_True,
            self.ui.button_passengers_2,
            self.ui.button_passengers_3,
            # 个人突破
            self.ui.button_jiejietupo_switch_level,
            self.ui.button_jiejietupo_switch_rule,
            self.ui.comboBox_jiejietupo_current_level,
            self.ui.comboBox_jiejietupo_target_level,
            self.ui.button_jiejietupo_fail,
        ]:
            item.setEnabled(not flag)
        return

    def buttonGroup_yuhun_mode_handle(self):
        flag = self.ui.buttonGroup_yuhun_mode.checkedButton() == self.ui.button_mode_team
        self.ui.button_driver_False.setEnabled(flag)
        self.ui.button_driver_True.setEnabled(flag)
        self.ui.button_passengers_2.setEnabled(flag)
        self.ui.button_passengers_3.setEnabled(flag)

    def buttonGroup_yuhun_driver_handle(self):
        flag = self.ui.buttonGroup_yuhun_driver.checkedButton() == self.ui.button_driver_True
        self.ui.button_passengers_2.setEnabled(flag)
        self.ui.button_passengers_3.setEnabled(flag)

    def buttonGroup_jiejietupo_switch_handle(self):
        flag = self.ui.buttonGroup_jiejietupo_switch.checkedButton() == self.ui.button_jiejietupo_switch_level
        self.ui.comboBox_jiejietupo_current_level.setEnabled(flag)
        self.ui.comboBox_jiejietupo_target_level.setEnabled(flag)
        self.ui.button_jiejietupo_fail.setEnabled(flag)
        for widget in self.ui.buttonGroup_jiejietupo_refresh_rule.buttons():
            widget.setEnabled(not flag)

    def button_qiling_tancha_handle(self):
        if self.ui.button_qiling_tancha.isChecked():
            self.ui.spin_qiling_tancha.show()
        else:
            self.ui.spin_qiling_tancha.hide()

    def button_qiling_jieqi_handle(self):
        if self.ui.button_qiling_jieqi.isChecked():
            self.ui.combo_qiling_jieqi_stone.show()
            self.ui.spin_qiling_jieqi_stone.show()
        else:
            self.ui.combo_qiling_jieqi_stone.hide()
            self.ui.spin_qiling_jieqi_stone.hide()

    def buttonGroup_yingjieshilian_handle(self):
        flag = self.ui.buttonGroup_yingjieshilian.checkedButton() == self.ui.button_yingjieshilian_skill
        if flag:
            self.ui_spin_times_set_value_func(50)
            BingZangMiJing.description()
        else:
            self.ui_spin_times_set_value_func(1)
            GuiBingYanWu.description()

    def buttonGroup_huijuan_jiejietupo_switch_handle(self):
        flag = (
            self.ui.buttonGroup_huijuan_jiejietupo_switch.checkedButton()
            == self.ui.button_huijuan_jiejietupo_switch_level
        )
        self.ui.comboBox_huijuan_jiejietupo_current_level.setEnabled(flag)
        self.ui.comboBox_huijuan_jiejietupo_target_level.setEnabled(flag)
        self.ui.button_huijuan_jiejietupo_fail.setEnabled(flag)

    def refresh_window_list(self, handles):
        self.ui.tab_window_manager_comboBox.clear()
        if handles:
            for handle in handles:
                self.ui.tab_window_manager_comboBox.addItem(f"{handle.title} - {handle.handle}")
            self.ui.tab_window_manager_comboBox.setCurrentIndex(0)

            logger.info(f"刷新窗口列表，当前窗口数量：{len(handles)}")
        else:
            logger.info("刷新窗口列表，当前窗口数量：0")

    def preview_window(self):
        """预览选中的窗口"""

        current_text = self.ui.tab_window_manager_comboBox.currentText()
        if current_text:
            handle = current_text.split(" - ")[-1]
            if handle:
                image = ScreenShot(handle=int(handle)).get_image()

                qimage = ImageQt(image)
                pixmap = QPixmap.fromImage(qimage)

                # 缩放图像以适应预览区域
                scaled_pixmap = pixmap.scaled(
                    self.ui.tab_window_manager_preview_image.width(),
                    self.ui.tab_window_manager_preview_image.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.ui.tab_window_manager_preview_image.setPixmap(scaled_pixmap)

                logger.info(f"预览窗口：{handle}")
            else:
                logger.warning("未选中窗口")
                ms.main.qmessagbox_update.emit("ERROR", "未选中窗口")

    def apply_selected_window(self):
        """应用选中的窗口"""
        current_text = self.ui.tab_window_manager_comboBox.currentText()
        if current_text:
            handle = current_text.split(" - ")[-1]
            window_manager.force_update(handle)
            logger.info(f"应用选中的窗口：{handle}")
        else:
            logger.warning("未选中窗口")
            ms.main.qmessagbox_update.emit("ERROR", "未选中窗口")

    def ui_valid_listWidget_update_handle(self, func: str, item: str) -> None:
        """valid_listWidget

        参数:
            func (str): 方法
            item (str): 内容
        """
        if func == "add":
            self.ui.valid_listWidget.addItem(item)
        elif func == "clear":
            self.ui.valid_listWidget.clear()

    def score_handle(self):
        from .valid import score_handle

        self.ui.valid_pushButton.setEnabled(False)
        score_handle()
        self.ui.valid_pushButton.setEnabled(True)

    def app_restart_handle(self):
        Restart().app_restart()

    def open_homepage(self, *args) -> None:
        import webbrowser

        logger.info("open homepage address.")
        webbrowser.open(HOME_PAGE_LINK)

    def open_helpdoc(self, *args) -> None:
        import webbrowser

        logger.info("open helpdoc address.")
        webbrowser.open(HELP_DOC_LINK)

    def open_Qgroup(self, *args) -> None:
        import webbrowser

        logger.info("open Qgroup address.")
        webbrowser.open(QQ_GROUP_LINK)

    def closeEvent(self, event) -> None:
        """关闭程序事件"""
        # 清理线程
        self.key_listener.stop()
        global_task.stop()

        # 关闭子窗口
        if hasattr(self.ui, "update_record_ui"):
            self.ui.update_record_ui.close()
        if hasattr(self.ui, "upgrade_new_version_ui"):
            self.ui.upgrade_new_version_ui.close()

        with suppress(Exception):
            logger.info("[EXIT]")

        super().closeEvent(event)

    def _exit_handle(self):
        self.close()

    def show_update_record_window(self):
        self.ui.update_record_ui = UpdateRecordWindow()
        self.ui.update_record_ui.show()

    def show_upgrade_new_version_window(self):
        self.ui.upgrade_new_version_ui = UpgradeNewVersionWidget()
        self.ui.upgrade_new_version_ui.show()
