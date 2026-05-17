import shutil
from contextlib import suppress
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import Thread
from typing import Literal

from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QTextCursor
from qfluentwidgets import Dialog, MessageBox

from ..package import *  # noqa: F403
from ..package.types import GameFunction
from ..ui import icon_rc  # noqa: F401
from ..ui.fluent import Window as FluentWindow
from ..ui.update_record_widget import UpdateRecordWindow
from ..ui.upgrade_new_version_widget import UpgradeNewVersionWidget
from .application import APP_NAME, APP_PATH, CACHE_DIR_PATH, VERSION
from .config import _game_language_list, _interaction_mode_list, config, default_config
from .decorator import log_function_call, run_in_thread
from .event import event_thread
from .function import is_Chinese_Path
from .global_task import global_task
from .keyboard_listener import KeyListenerThread
from .log import log_clean_up, logger
from .mysignal import global_ms as ms
from .paddleocr import check_ocr_folder, ocr_manager
from .restart import Restart
from .screenshot import ScreenShot
from .shortcut import create_desktop_shortcut
from .update import get_update_info
from .upgrade import upgrade
from .valid import score_handle
from .window import GameWindow, window_manager


class StackedWidgetIndex(Enum):
    """高级设置窗口索引"""

    NONE = 0
    YUHUN = 1
    JIEJIETUPO = 2
    DAOGUANTUPO = 3
    QILING = 4
    YINGJIESHILIAN = 5
    HUIJUAN = 6


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        if config.user.game_language == "国服":
            title = f"{APP_NAME} - v{VERSION}"
        else:
            title = f"{APP_NAME} - v{VERSION} - {config.user.game_language}"
        self.setWindowTitle(title)

        # 通过先启动GUI再初始化各控件，提高启动加载速度
        self.ui_init()
        self.software_init()

    def ui_init(self):
        """初始化UI"""
        self.homeInterface.basic_group.func_combobox.setEnabled(False)
        self.homeInterface.basic_group.number_spinbox.setEnabled(False)
        self.homeInterface.button_status.setEnabled(False)

        self._init_settings()
        self._init_signals()
        self._init_events()

        self.key_listener = KeyListenerThread()
        ms.main.key_pressed.connect(self._shortcut_handle)
        self.key_listener.start()

    def _init_settings(self):
        """初始化设置"""
        card = self.settingInterface
        setting = config.user

        card.language_card.combobox.setCurrentText(setting.game_language)
        card.xuanshangfengyin_card.combobox.setCurrentText(setting.xuanshangfengyin)
        card.interaction_mode_card.mode_combobox.setCurrentText(setting.interaction_mode.mode)
        card.interaction_mode_card.frontend_force_window_switch.setChecked(
            setting.interaction_mode.frontend.force_window
        )
        card.interaction_mode_card.backend_prevent_sleep_switch.setChecked(
            setting.interaction_mode.backend.prevent_sleep
        )
        card.interaction_mode_card.backend_screenshot_combobox.setCurrentText(
            setting.interaction_mode.backend.screenshot_method
        )
        card.remember_last_choice_card.switch.setChecked(
            setting.remember_last_choice != default_config.remember_last_choice
        )
        card.shortcut_start_stop_card.combobox.setCurrentText(setting.shortcut_start_stop)
        card.win_toast_card.switch.setChecked(setting.win_toast)
        card.group_update.mode_switch.setChecked(setting.auto_update)
        card.group_update.download_combobox.setCurrentText(setting.update_download)

    def _init_signals(self):
        """初始化信号"""
        ms.main.qmessagbox_update.connect(self.qmessagbox_update_handle)
        ms.main.ui_text_info_update.connect(self.ui_text_info_update_handle)
        ms.main.is_fighting_update.connect(self.is_fighting)
        ms.main.ui_text_progress_update.connect(self.ui_text_progress_update_handle)
        ms.main.effective_entry_analysis_list_widget_update.connect(
            self.ui_effective_entry_analysis_list_widget_update_handle
        )
        ms.main.sys_exit.connect(self._exit_handle)
        ms.upgrade_new_version.show_ui.connect(self.show_upgrade_new_version_window)

    def _init_events(self):
        """初始化事件"""
        self.homeInterface.basic_group.func_combobox.currentIndexChanged.connect(self.game_function_description)
        self.homeInterface.button_status.clicked.connect(self.app_running)

        self.windowManagerInterface.preview_button.clicked.connect(self.preview_window)
        self.windowManagerInterface.apply_button.clicked.connect(self.apply_selected_window)

        self.effectiveEntryAnalysisInterface.button.clicked.connect(
            self.effective_entry_analysis_interface_score_handle
        )

        self.settingInterface.about_card.short_cut_button.clicked.connect(create_desktop_shortcut)
        self.settingInterface.about_card.app_restart_button.clicked.connect(self.app_restart_handle)
        self.settingInterface.about_card.update_record_button.clicked.connect(self.show_update_record_window)

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
    def software_init(self):
        """程序初始化"""
        logger.info(f"application path: {APP_PATH}")
        logger.info(f"resource path: {config.resource_dir}")
        logger.info(f"[VERSION] {VERSION}")
        config.show_log()
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

        if not config.user.game_language == _game_language_list[0]:
            logger.ui_warn("当前非国服，请注意部分资源可能不兼容")

        if config.user.interaction_mode.mode == _interaction_mode_list[1]:
            logger.ui_warn(
                "当前为后台交互模式，需要在窗口管理中检查截图是否正常。如果在移动游戏窗口后截图黑屏，可尝试切换后台截图模式解决"
            )

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

    def qmessagbox_update_handle(self, level: str, msg: str):
        # TODO 弹窗类型
        # TODO 弹窗内容
        if level == "ERROR":
            message_box = MessageBox("错误", msg, self)
            message_box.yesButton.setText("确定")
            message_box.hideCancelButton()  # 隐藏取消按钮
            message_box.exec()

        elif level == "question":
            if msg == "强制缩放":
                logger.error("游戏窗口大小不匹配")
                title = "窗口大小不匹配"
                content = "是否强制缩放，如不缩放，请自行靠近1136*640，或者参考 README.MD 在data/myresource文件夹中添加对应素材"
                dialog = Dialog(title, content)

                if dialog.exec():
                    logger.info("用户接受强制缩放")
                    window_manager.force_zoom()
                else:
                    logger.info("用户拒绝强制缩放")

            elif msg == "更新重启":
                logger.info("提示：更新重启")
                title = "检测到更新包"
                content = "是否更新重启，如有自己替换的素材，请在取消后手动解压更新包"
                dialog = Dialog(title, content)

                if dialog.exec():
                    logger.info("用户接受更新重启")
                    Thread(target=upgrade.restart, name="upgrade_restart", daemon=True).start()
                else:
                    logger.info("用户拒绝更新重启")

    # TODO 移动到UI内部
    def ui_text_info_update_handle(self, msg: str, color: str):
        """输出内容至文本框

        WARN | ERROR -> 红色

        SCENE -> 绿色

        参数:
            msg(str): 文本内容
        """
        widget = self.homeInterface.output_info_group.text_info
        widget.setTextColor(color)
        widget.append(msg)
        # 自动换行
        widget.ensureCursorVisible()
        # 自动滑动到底
        widget.moveCursor(QTextCursor.MoveOperation.End)
        widget.setTextColor("black")

    def ui_text_progress_update_handle(self, msg: str):
        """输出内容至文本框`完成情况`

        参数:
            msg (str): 文本
        """
        self.homeInterface.output_info_group.progress_text.setText(msg)

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
        try:
            ocr_manager.init()
            logger.info("文字识别资源初始化成功")
        except Exception as e:
            logger.ui_error(f"文字识别资源初始化失败: {e}")
            return False

        return True

    def _window_button_enabled_handle(self):
        logger.ui("检测到游戏窗口")
        self.homeInterface.basic_group.func_combobox.setEnabled(True)
        self.homeInterface.basic_group.number_spinbox.setEnabled(True)

        # 记忆上次所选功能
        last_choice = config.user.remember_last_choice
        if last_choice > 0:
            self.homeInterface.basic_group.func_combobox.setCurrentIndex(last_choice - 1)

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
            if not check_assets(P.resource_path):
                return False

        logger.info("资源完整")
        return True

    def check_game_handle(self):
        return window_manager.force_update()

    def game_function_description(self):
        """功能描述"""

        def set_stack(index: StackedWidgetIndex):
            self.homeInterface.advanced_stack.setCurrentIndex(index.value)

        basic_group = self.homeInterface.basic_group
        advanced_stack = self.homeInterface.advanced_stack

        self.game_function_choice = GameFunction(basic_group.func_combobox.currentIndex() + 1)
        if config.user.remember_last_choice != -1:
            config.update("remember_last_choice", self.game_function_choice.value)
        self.homeInterface.button_status.setEnabled(True)
        basic_group.number_spinbox.setEnabled(True)
        basic_group.set_number_spinbox_value(1, 1, 999)
        set_stack(StackedWidgetIndex.NONE)

        match self.game_function_choice:
            case GameFunction.YUHUN:
                YuHun.description()
                set_stack(StackedWidgetIndex.YUHUN)
                card = advanced_stack.yuhun_card
                card.mode_team_button.setEnabled(True)
                card.mode_single_button.setEnabled(True)
                card.mode_team_button.setChecked(True)
                card.driver_no_button.setChecked(True)
                card.passengers_2_button.setEnabled(True)
                card.passengers_3_button.setEnabled(True)
                card.passengers_2_button.setChecked(True)

            case GameFunction.YONGSHENGZHIHAI:
                YongShengZhiHai.description()
                set_stack(StackedWidgetIndex.YUHUN)
                basic_group.set_number_spinbox_value(30)
                card = advanced_stack.yuhun_card
                card.mode_team_button.setChecked(True)
                # 只有组队，最多2人
                card.mode_team_button.setEnabled(False)
                card.mode_single_button.setEnabled(False)
                card.driver_no_button.setChecked(True)
                card.passengers_2_button.setChecked(True)
                card.passengers_2_button.setEnabled(False)
                card.passengers_3_button.setEnabled(False)

            case GameFunction.YEYUANHUO:
                YeYuanHuo.description()

            case GameFunction.YULING:
                YuLing.description()
                basic_group.set_number_spinbox_value(1, 1, 400)  # 桌面版上限300

            case GameFunction.GERENTUPO:
                JieJieTuPoGeRen.description()
                set_stack(StackedWidgetIndex.JIEJIETUPO)
                basic_group.set_number_spinbox_value(1, 1, 30)
                card = advanced_stack.jiejietupo_card
                card.mode_level.setChecked(True)
                card.fail_checkbox.setChecked(True)

            case GameFunction.LIAOTUPO:
                times = JieJieTuPoYinYangLiao.description()
                basic_group.set_number_spinbox_value(times, 1, 200)

            case GameFunction.DAOGUANTUPO:
                DaoGuanTuPo.description()
                set_stack(StackedWidgetIndex.DAOGUANTUPO)
                basic_group.number_spinbox.setEnabled(False)

            case GameFunction.ZHAOHUAN:
                ZhaoHuan.description()

            case GameFunction.BAIGUIYEXING:
                BaiGuiYeXing.description()

            case GameFunction.HUODONG:
                HuoDong.description()
                basic_group.set_number_spinbox_value(1, 1, 9999)

            case GameFunction.RILUN:
                RiLun.description()
                set_stack(StackedWidgetIndex.YUHUN)
                basic_group.set_number_spinbox_value(50)
                card = advanced_stack.yuhun_card
                card.mode_team_button.setEnabled(True)
                card.mode_single_button.setEnabled(True)
                card.mode_team_button.setChecked(True)
                card.driver_no_button.setChecked(True)
                card.passengers_2_button.setEnabled(True)
                card.passengers_3_button.setEnabled(True)
                card.passengers_2_button.setChecked(True)

            case GameFunction.TANSUO:
                TanSuo.description()

            case GameFunction.QILING:
                QiLing.description()
                set_stack(StackedWidgetIndex.QILING)
                basic_group.number_spinbox.setEnabled(False)

            case GameFunction.JUEXING:
                JueXing.description()

            case GameFunction.LIUDAOZHIMEN:
                LiuDaoZhiMen.description()

            case GameFunction.DOUJI:
                DouJi.description()

            case GameFunction.YINGJIESHILIAN:
                set_stack(StackedWidgetIndex.YINGJIESHILIAN)
                self.buttonGroup_yingjieshilian_handle()

            case GameFunction.HUIJUAN:
                set_stack(StackedWidgetIndex.HUIJUAN)
                HuiJuan.description()
                # basic_group.number_spinbox.setEnabled(False)
                card = advanced_stack.huijuan_card
                card.mode_level.setChecked(True)
                card.fail_checkbox.setChecked(True)
                card.mode_refresh.setChecked(False)

    def _app_start(self):
        # 没有选功能前禁止通过快捷键启动程序
        if self.homeInterface.basic_group.func_combobox.currentIndex() == -1:
            logger.ui_error("请选择功能")
            return

        selected_number: int = self.homeInterface.basic_group.number_spinbox.value()
        self.homeInterface.output_info_group.progress_text.clear()
        self.is_fighting(True)

        advanced_stack = self.homeInterface.advanced_stack

        match self.game_function_choice:
            case GameFunction.YUHUN:
                card = advanced_stack.yuhun_card
                if card.mode_group.checkedButton() == card.mode_team_button:
                    driver = card.driver_group.checkedButton() == card.driver_yes_button
                    passengers = int(card.passengers_group.checkedButton().text())
                    YuHunTeam(
                        n=selected_number,
                        flag_driver=driver,
                        flag_passengers=passengers,
                    ).task_start()
                else:
                    YuHunSingle(n=selected_number).task_start()

            case GameFunction.YONGSHENGZHIHAI:
                card = advanced_stack.yuhun_card
                if card.mode_group.checkedButton() == card.mode_team_button:
                    driver = card.driver_group.checkedButton() == card.driver_yes_button
                    YongShengZhiHaiTeam(n=selected_number, flag_driver=driver).task_start()

            case GameFunction.YEYUANHUO:
                YeYuanHuo(n=selected_number).task_start()

            case GameFunction.YULING:
                YuLing(n=selected_number).task_start()

            case GameFunction.GERENTUPO:
                flag_refresh_need: int = 0
                current_level = target_level = 57
                card = advanced_stack.jiejietupo_card
                if card.mode_group.checkedButton() == card.mode_level:
                    current_level = int(card.current_combobox.currentText())
                    target_level = int(card.target_combobox.currentText())
                else:
                    flag_refresh_need = 3  # 3胜
                JieJieTuPoGeRen(
                    n=selected_number,
                    flag_refresh_rule=flag_refresh_need,
                    flag_current_level=current_level,
                    flag_target_level=target_level,
                    flag_first_round_failure=card.fail_checkbox.isChecked(),
                ).task_start()

            case GameFunction.LIAOTUPO:
                JieJieTuPoYinYangLiao(n=selected_number).task_start()

            case GameFunction.DAOGUANTUPO:
                flag_guanzhan = advanced_stack.daoguantupo_card.checkbox.isChecked()
                DaoGuanTuPo(flag_guanzhan=flag_guanzhan).task_start()

            case GameFunction.ZHAOHUAN:
                ZhaoHuan(n=selected_number).task_start()

            case GameFunction.BAIGUIYEXING:
                BaiGuiYeXing(n=selected_number).task_start()

            case GameFunction.HUODONG:
                HuoDong(n=selected_number).task_start()

            case GameFunction.RILUN:
                card = advanced_stack.yuhun_card
                if card.mode_group.checkedButton() == card.mode_team_button:
                    driver = card.driver_group.checkedButton() == card.driver_yes_button
                    passengers = int(card.passengers_group.checkedButton().text())
                    RiLunTeam(
                        n=selected_number,
                        flag_driver=driver,
                        flag_passengers=passengers,
                    ).task_start()
                else:
                    RiLunSingle(n=selected_number).task_start()

            case GameFunction.TANSUO:
                TanSuo(n=selected_number).task_start()

            case GameFunction.QILING:
                card = advanced_stack.qiling_card
                _tancha = card.tancha_checkbox.isChecked()
                tancha_times = card.tancha_spinbox.value()
                _jieqi = card.jieqi_checkbox.isChecked()
                stone_pokemon = card.jieqi_stone_combobox.currentText()
                stone_numbers = card.jieqi_stone_spinbox.value()
                QiLing(
                    n=tancha_times,
                    if_tancha=_tancha,
                    if_jieqi=_jieqi,
                    stone_pokemon=stone_pokemon,
                    stone_numbers=stone_numbers,
                ).task_start()

            case GameFunction.JUEXING:
                JueXing(n=selected_number).task_start()

            case GameFunction.LIUDAOZHIMEN:
                LiuDaoZhiMen(n=selected_number).task_start()

            case GameFunction.DOUJI:
                DouJi(n=selected_number).task_start()

            case GameFunction.YINGJIESHILIAN:
                card = advanced_stack.yingjieshilian_card
                yingjie = card.combobox.currentText()
                if card.button_group.checkedButton() == card.skill_button:
                    YingJieShiLianSkill(yingjie, n=selected_number).task_start()
                else:
                    YingJieShiLianExp(yingjie, n=selected_number).task_start()

            case GameFunction.HUIJUAN:
                card = advanced_stack.huijuan_card
                flag_refresh_need: int = 0
                current_level = target_level = 57
                if card.mode_group.checkedButton() == card.mode_level:
                    current_level = int(card.current_combobox.currentText())
                    target_level = int(card.target_combobox.currentText())
                else:
                    flag_refresh_need = 3
                HuiJuan(
                    n=selected_number,
                    loop_count=card.tansuo_count_spinbox.value(),
                    flag_refresh_rule=flag_refresh_need,
                    flag_current_level=current_level,
                    flag_target_level=target_level,
                    flag_first_round_failure=card.fail_checkbox.isChecked(),
                ).task_start()

    def _app_stop(self):
        event_thread.set()
        logger.ui("停止中，请稍候")

    def app_running(self):
        if not self.homeInterface.button_status.is_start():
            event_thread.clear()
            self._app_start()
        else:
            self._app_stop()

    def is_fighting(self, flag: bool):
        """程序是否运行中，启用/禁用其他控件"""
        if flag:
            self.homeInterface.button_status.start()
        else:
            self.homeInterface.button_status.stop()

    def buttonGroup_yingjieshilian_handle(self):
        card = self.homeInterface.advanced_stack.yingjieshilian_card
        flag = card.button_group.checkedButton() == card.skill_button
        if flag:
            self.homeInterface.basic_group.set_number_spinbox_value(50, 0, 999)
            YingJieShiLianSkill.description()
        else:
            self.homeInterface.basic_group.set_number_spinbox_value(1, 0, 999)
            YingJieShiLianExp.description()

    def refresh_window_list(self, game_window_list: list[GameWindow]):
        """刷新窗口列表

        Args:
            game_window_list (list[GameWindow]): 窗口句柄列表
        """
        self.windowManagerInterface.update_label(len(game_window_list))
        combobox = self.windowManagerInterface.comboBox
        combobox.clear()
        if game_window_list:
            for item in game_window_list:
                combobox.addItem(f"{item.title} - {item.handle}", userData=item.handle)  # 存储窗口句柄
            combobox.setCurrentIndex(0)

            logger.info(f"刷新窗口列表，当前窗口数量：{len(game_window_list)}")
        else:
            logger.info("刷新窗口列表，当前窗口数量：0")

        self.windowManagerInterface.comboBox.setEnabled(len(game_window_list) > 0)
        self.windowManagerInterface.preview_button.setEnabled(len(game_window_list) > 0)
        self.windowManagerInterface.apply_button.setEnabled(len(game_window_list) > 0)

    def preview_window(self):
        """预览选中的窗口"""
        widget = self.windowManagerInterface
        data = widget.comboBox.currentData()
        if data and int(data):
            handle = int(data)
            logger.info(f"当前窗口：{handle}")
            image = ScreenShot(handle=handle).get_image()
            qimage = ImageQt(image)
            pixmap = QPixmap.fromImage(qimage)
            # 缩放图像以适应预览区域
            scaled_pixmap = pixmap.scaled(
                widget.preview_image.width(),
                widget.preview_image.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            widget.preview_image.setPixmap(scaled_pixmap)
            widget.update_capture_size_label(f"{image.size[0]} X {image.size[1]}")
            widget.update_capture_time_label(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

            logger.info(f"预览窗口：{handle}")
        else:
            logger.warning("未选中窗口")
            ms.main.qmessagbox_update.emit("ERROR", "未选中窗口")

    def apply_selected_window(self):
        """应用选中的窗口"""
        widget = self.windowManagerInterface
        data = widget.comboBox.currentData()
        if data and int(data):
            handle = int(data)
            window_manager.force_update(handle)
            logger.info(f"应用选中的窗口：{handle}")
        else:
            logger.warning("未选中窗口")
            ms.main.qmessagbox_update.emit("ERROR", "未选中窗口")

    def ui_effective_entry_analysis_list_widget_update_handle(self, method: Literal["ADD", "CLEAR"], item: str):
        """更新有效词条分析列表框

        Args:
            method (Literal["ADD", "CLEAR"]): 方法
            item (str): 内容
        """
        if method == "ADD":
            self.effectiveEntryAnalysisInterface.add_item(item)
        elif method == "CLEAR":
            self.effectiveEntryAnalysisInterface.clear()

    def effective_entry_analysis_interface_score_handle(self):
        """有效词条分析界面计算分数"""
        button = self.effectiveEntryAnalysisInterface.button
        button.setDisabled(True)
        score_handle()
        button.setEnabled(True)

    def app_restart_handle(self):
        Restart().app_restart()

    def closeEvent(self, event):
        """关闭程序事件"""
        # 清理线程
        self.key_listener.stop()
        global_task.stop()

        # 关闭子窗口
        if hasattr(self, "update_record_widget"):
            self.update_record_widget.close()
        if hasattr(self, "upgrade_new_version_widget"):
            self.upgrade_new_version_widget.close()

        # 删除缓存文件夹
        with suppress(Exception):
            if CACHE_DIR_PATH.exists():
                shutil.rmtree(CACHE_DIR_PATH)
                logger.info(f"已删除缓存文件夹: {CACHE_DIR_PATH}")

        with suppress(Exception):
            logger.info("[EXIT]")

        super().closeEvent(event)

    def _exit_handle(self):
        self.close()

    def show_update_record_window(self):
        self.update_record_widget = UpdateRecordWindow()
        self.update_record_widget.show()

    def show_upgrade_new_version_window(self):
        self.upgrade_new_version_widget = UpgradeNewVersionWidget()
        self.upgrade_new_version_widget.show()
