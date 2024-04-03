import sys
import time
from contextlib import suppress
from enum import Enum
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
from .event import event_thread, event_ocr_init
from .log import log_clean_up, logger
from .myschedule import global_scheduler
from .mysignal import global_ms as ms
from .mythread import WorkThread
from .restart import Restart
from .paddleocr import ocr
from .update import get_update_info, update_record
from .upgrade import upgrade
from .window import window, check_game_handle


def get_global_icon():
    """窗口图标"""
    global_icon = QIcon()
    global_icon.addPixmap(QPixmap("buzhihuo.ico"))
    return global_icon


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
    RILUN = 11  # 组队日轮副本
    TANSUO = 12  # 单人探索
    QILING = 13  # 契灵
    JUEXING = 14  # 觉醒副本
    LIUDAOZHIMEN = 15  # 六道之门


class StackedWidgetIndex(Enum):
    """高级设置窗口索引"""
    NONE = 0
    YUHUN = 1
    JIEJIETUPO = 2
    DAOGUANTUPO = 3
    QILING = 4


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
        _flag_check = _status != -1
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
        # 游戏检测按钮
        self.ui.button_game_handle.clicked.connect(self.check_game_handle)
        # 开始按钮
        self.ui.button_start.clicked.connect(self.app_running)
        # 功能选择事件
        self.ui.combo_choice.currentIndexChanged.connect(self.game_function_description)
        # 重启
        self.ui.button_restart.clicked.connect(self.app_restart_func)
        # 更新记录事件
        self.ui.button_update_record.clicked.connect(self.show_update_record_window)
        # GitHub地址悬停事件
        self.ui.label_GitHub_address.mousePressEvent = self.open_GitHub_address
        self.ui.buttonGroup_yuhun_mode.buttonClicked.connect(self.buttonGroup_yuhun_mode_change)
        self.ui.buttonGroup_jiejietupo_switch.buttonClicked.connect(self.buttonGroup_jiejietupo_switch_change)

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
        global_scheduler.add_job(
            window.scheduler_get_game_window_handle,
            "interval", seconds=1,
            id='scheduler_get_game_window_handle'
        )
        task_xuanshangfengyin.task_start()
        # 文字识别
        ocr.init()
        if event_ocr_init.is_set():
            self.ui.combo_choice.addItem("15.六道之门")
        logger.info(global_scheduler.get_jobs())
        global_scheduler.start()

    def qmessagbox_update_func(self, level: str, msg: str) -> None:
        if level == "ERROR":
            QMessageBox.critical(self, level, msg)
        elif level == "question":
            if msg == "强制缩放":
                logger.error("游戏窗口大小不匹配")
                if QMessageBox.question(
                    self,
                    "窗口大小不匹配",
                    "是否强制缩放，如不缩放，请自行靠近1136*640，或者参考 README.MD 在data/myresource文件夹中添加对应素材",
                ) == QMessageBox.StandardButton.Yes:
                    logger.info("用户接受强制缩放")
                    window.force_zoom()
                else:
                    logger.info("用户拒绝强制缩放")
            elif msg == "更新重启":
                logger.info("提示：更新重启")
                if QMessageBox.question(
                    self,
                    "检测到更新包",
                    "是否更新重启，如有自己替换的素材，请在取消后手动解压更新包",
                ) == QMessageBox.StandardButton.Yes:
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

    def ui_spin_times_set_value_func(self, current: int = 1, min: int = 0, max: int = 99):
        widget = self.ui.spin_times
        widget.setValue(current)
        widget.setMinimum(min)
        widget.setMaximum(max)

    @log_function_call
    def _check_enviroment(self) -> bool:
        """环境检测

        返回:
            bool: 是否完成
        """
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
        logger.info(f"设置项：悬赏封印已更改为 {text}")
        config.config_user_changed("xuanshangfengyin", text)
        task_xuanshangfengyin.task_start()

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

    def check_game_handle(self):
        return check_game_handle()

    def game_function_description(self):
        """功能描述"""
        self.game_function_choice = GameFunction(self.ui.combo_choice.currentIndex() + 1)
        if config.config_user.remember_last_choice != -1:
            config.config_user_changed("remember_last_choice", self.game_function_choice.value)
        self.ui.button_start.setEnabled(True)
        self.ui.spin_times.setEnabled(True)
        self.ui_spin_times_set_value_func(1, 1, 999)
        self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.NONE.value)

        match self.game_function_choice:
            case GameFunction.YUHUN:
                logger.ui(YuHun.description)
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.YUHUN.value)
                self.ui.button_mode_team.setEnabled(True)
                self.ui.button_mode_single.setEnabled(True)
                self.ui.button_mode_team.setChecked(True)
                self.ui.button_driver_False.setChecked(True)
                self.ui.button_passengers_2.setEnabled(True)
                self.ui.button_passengers_3.setEnabled(True)
                self.ui.button_passengers_2.setChecked(True)
            case GameFunction.YONGSHENGZHIHAI:
                logger.ui(YongShengZhiHai.description)
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.YUHUN.value)
                self.ui_spin_times_set_value_func(30)
                self.ui.button_mode_team.setChecked(True)
                # TODO
                self.ui.button_mode_team.setEnabled(False)
                self.ui.button_mode_single.setEnabled(False)
                self.ui.button_driver_False.setChecked(True)
                self.ui.button_passengers_2.setChecked(True)
                self.ui.button_passengers_2.setEnabled(False)
                self.ui.button_passengers_3.setEnabled(False)
            case GameFunction.YEYUANHUO:
                logger.ui(YeYuanHuo.description)
            case GameFunction.YULING:
                logger.ui(YuLing.description)
                self.ui_spin_times_set_value_func(1, 1, 400)  # 桌面版上限300
            case GameFunction.GERENTUPO:
                logger.ui(JieJieTuPoGeRen.description)
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.JIEJIETUPO.value)
                self.ui.button_jiejietupo_switch_rule.setChecked(True)
                self.ui.button_jiejietupo_current_level_60.setChecked(True)
                self.ui.button_jiejietupo_target_level_60.setChecked(True)
                self.ui.button_jiejietupo_refresh_rule_3.setChecked(True)
                # TODO
                self.ui.button_jiejietupo_refresh_rule_6.hide()
                self.ui.button_jiejietupo_refresh_rule_9.hide()
                self.buttonGroup_jiejietupo_switch_change()
                self.ui_spin_times_set_value_func(1, 1, 30)
            case GameFunction.LIAOTUPO:
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
            case GameFunction.DAOGUANTUPO:
                logger.ui(DaoGuanTuPo.description)
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.DAOGUANTUPO.value)
                self.ui.spin_times.setEnabled(False)
            case GameFunction.ZHAOHUAN:
                logger.ui(ZhaoHuan.description)
            case GameFunction.BAIGUIYEXING:
                logger.ui(BaiGuiYeXing.description)
            case GameFunction.HUODONG:
                logger.ui(HuoDong.description)
            case GameFunction.RILUN:
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
                logger.ui(TanSuo.description)
            case GameFunction.QILING:
                logger.ui(QiLing.description)
                self.ui.stackedWidget.setCurrentIndex(StackedWidgetIndex.QILING.value)
                self.ui.button_qiling_jieqi.setChecked(True)
                self.ui.combo_qiling_jieqi_stone.addItem("镇墓兽")
                self.ui.spin_qiling_jieqi_stone.setValue(1)
            case GameFunction.JUEXING:
                logger.ui(JueXing.description)
            case GameFunction.LIUDAOZHIMEN:
                logger.ui(LiuDaoZhiMen.description, "warn")

    def _app_start(self) -> None:
        n = self.ui.spin_times.value()
        flag_drop_statistics = self.ui.button_yuhun_drop_statistics.isChecked()
        self.ui.text_completion_times.clear()
        self.is_fighting(True)

        match self.game_function_choice:
            case GameFunction.YUHUN:
                if self.ui.buttonGroup_yuhun_mode.checkedButton().text() == "组队":
                    flag_driver = (
                        self.ui.buttonGroup_yuhun_driver.checkedButton().text() != "否"
                    )
                    flag_passengers = int(
                        self.ui.buttonGroup_yuhun_passengers.checkedButton().text()
                    )
                    YuHunTeam(
                        n=n,
                        flag_driver=flag_driver,
                        flag_passengers=flag_passengers,
                        flag_drop_statistics=flag_drop_statistics
                    ).task_start()
                else:
                    YuHunSingle(
                        n=n,
                        flag_drop_statistics=flag_drop_statistics
                    ).task_start()
            case GameFunction.YONGSHENGZHIHAI:
                if self.ui.buttonGroup_yuhun_mode.checkedButton().text() == "组队":
                    flag_driver = (
                        self.ui.buttonGroup_yuhun_driver.checkedButton().text() != "否"
                    )
                    YongShengZhiHaiTeam(
                        n=n,
                        flag_driver=flag_driver,
                        flag_drop_statistics=flag_drop_statistics
                    ).task_start()
            case GameFunction.YEYUANHUO:
                YeYuanHuo(n=n).task_start()
            case GameFunction.YULING:
                YuLing(n=n).task_start()
            case GameFunction.GERENTUPO:
                flag_refresh_need = 0
                current_level = target_level = 60
                if self.ui.buttonGroup_jiejietupo_switch.checkedButton().text() == "卡级":
                    current_level = self.ui.buttonGroup_jiejietupo_current_level.checkedButton().text()
                    target_level = self.ui.buttonGroup_jiejietupo_target_level.checkedButton().text()
                else:
                    flag_refresh_need = self.ui.buttonGroup_jiejietupo_refresh_rule.checkedButton().text()[0]
                JieJieTuPoGeRen(
                    n=n,
                    flag_refresh_rule=flag_refresh_need,
                    flag_current_level=current_level,
                    flag_target_level=target_level
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
                flag_driver = (
                    self.ui.buttonGroup_yuhun_driver.checkedButton().text() != "否"
                )
                flag_passengers = int(
                    self.ui.buttonGroup_yuhun_passengers.checkedButton().text()
                )
                RiLun(
                    n=n,
                    flag_driver=flag_driver,
                    flag_passengers=flag_passengers
                ).task_start()
            case GameFunction.TANSUO:
                TanSuo(n=n).task_start()
            case GameFunction.QILING:
                flag_tancha = self.ui.button_qiling_tancha.isChecked()
                flag_jieqi = self.ui.button_qiling_jieqi.isChecked()
                stone_pokemon = self.ui.combo_qiling_jieqi_stone.currentText()
                stone_numbers = self.ui.spin_qiling_jieqi_stone.value()
                QiLing(
                    n=n,
                    _flag_tancha=flag_tancha,
                    _flag_jieqi=flag_jieqi,
                    _stone_pokemon=stone_pokemon,
                    _stone_numbers=stone_numbers
                ).task_start()
            case GameFunction.JUEXING:
                JueXing(n=n).task_start()
            case GameFunction.LIUDAOZHIMEN:
                LiuDaoZhiMen(n=n).task_start()

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

    def buttonGroup_yuhun_mode_change(self):
        flag = self.ui.buttonGroup_yuhun_mode.checkedButton().text() == "组队"
        self.ui.button_driver_False.setEnabled(flag)
        self.ui.button_driver_True.setEnabled(flag)
        self.ui.button_passengers_2.setEnabled(flag)
        self.ui.button_passengers_3.setEnabled(flag)

    def buttonGroup_jiejietupo_switch_change(self):
        flag = self.ui.buttonGroup_jiejietupo_switch.checkedButton().text() == "卡级"
        for widget in self.ui.buttonGroup_jiejietupo_current_level.buttons():
            widget.setEnabled(flag)
        for widget in self.ui.buttonGroup_jiejietupo_target_level.buttons():
            widget.setEnabled(flag)
        for widget in self.ui.buttonGroup_jiejietupo_refresh_rule.buttons():
            widget.setEnabled(not flag)

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
        global_scheduler.shutdown()
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
