#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# main.py

import sys
from ctypes import windll
import time
import httpx
import json
from pathlib import Path
from threading import Thread

from PySide6.QtGui import QIcon, QPixmap, QTextCursor
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QWidget

from ui.mainui import Ui_MainWindow
from ui.updateui import Ui_Form
from mysignal import global_ms as ms
from package import *

version: str = "1.6.5"
"""版本号"""
fpath = Path.cwd()
"""文件路径"""


class MainWindow(QMainWindow, Log):
    _list_function = [  # 功能列表
        '1.组队御魂副本',
        '2.组队永生之海副本',
        '3.业原火副本',
        '4.御灵副本',
        '5.个人突破',
        '6.寮突破',
        '7.道馆突破',
        '8.普通召唤',
        '9.百鬼夜行',
        '10.限时活动',
        '11.组队日轮副本'
    ]
    _package_ = [  # 图片素材文件夹
        'yuhun',
        'yongshengzhihai',
        'yeyuanhuo',
        'yuling',
        'jiejietupo',
        'daoguantupo',
        'zhaohuan',
        'baiguiyexing',
        'huodong'
    ]
    _choice: int  # 功能

    def __init__(self):
        super().__init__()
        self.fpath = Path.cwd()
        # 使用ui文件导入定义界面类
        self.ui = Ui_MainWindow()
        # 初始化界面
        self.setFixedSize(550, 450)  # 固定宽高
        self.ui.setupUi(self)
        # 窗口图标
        icon = QIcon()
        icon.addPixmap(QPixmap('buzhihuo.ico'))
        self.setWindowIcon(icon)
        self.setWindowTitle(f'Onmyoji_Python - v{version}')  # 版本号显示
        timenow = time.strftime("%H:%M:%S")
        try:
            self.log_write('[START]')
            self.log_write('[START]')
            self.log_write(f'{timenow} [VERSION] {version}')
        except:
            pass

        # 事件连接
        self.ui.button_resources.clicked.connect(self.resources)  # 资源检测按钮
        self.ui.button_wininfo.clicked.connect(self.wininfo_update)  # 更新窗口信息
        self.ui.button_start.clicked.connect(self.start)  # 开始按钮
        self.ui.combo_choice.currentIndexChanged.connect(self.choice_text)  # 功能选择事件

        # 自定义信号
        ms.text_print_update.connect(self.text_print_update_func)  # 主界面信息文本更新
        ms.text_wininfo_update.connect(self.text_wininfo_update_func)  # 窗口信息文本更新
        ms.text_num_update.connect(self.text_num_update_func)  # 完成情况文本更新
        ms.is_fighting_update.connect(self.is_fighting)  # 运行状态更新

        # 初始化控件
        self.ui.combo_choice.addItems(self._list_function)
        self.ui.button_start.setEnabled(False)
        self.ui.combo_choice.setEnabled(False)
        self.ui.spinB_num.setEnabled(False)
        self.ui.text_miaoshu.setPlaceholderText('仅供内部测试使用，请勿外传，本程序所产生的一切后果自负\
                                                请确认您是使用管理员权限打开本程序\
                                                请先运行“环境检测”')
        # self.is_fighting_yuhun(False)
        self.ui.stackedWidget.setCurrentIndex(0)  # 索引0，空白
        self.ui.text_print.document().setMaximumBlockCount(50)

        # 菜单栏
        self.ui.action_update.triggered.connect(self.update_info)  # 更新日志
        self.ui.action_clean_log.triggered.connect(self.clean_log)  # 清理日志
        self.ui.action_GitHub.triggered.connect(self.GitHub_address)  # GitHub地址
        self.ui.action_exit.triggered.connect(self.exit)  # 退出

        # update_auto
        thread_update = Thread(target=self.update_auto)
        thread_update.daemon = True
        thread_update.start()

    def pic_is_complete(self):
        picpath: Path = fpath / 'pic'
        for i in range(len(self._package_)):
            flag = Path(Path(picpath).joinpath(self._package_[i])).exists()
            if not flag:
                QMessageBox.critical(self, 'ERROR', f'无{self._package_[i]}文件夹')
                return False
        return True

    def text_print_update_func(self, text: str):
        """
        输出内容至文本框\n
        WARN -> 红色\n
        SCENE -> 绿色\n
        :param text: 文本
        """
        timenow = time.strftime("%H:%M:%S")
        if ('[' and ']' not in text) or ('勋章' in text):  # 勋章数单独适配
            text = f'{timenow} [INFO] {text}'
            print(f'[DEBUG] {text}')  # 输出至控制台调试
            self.log_write(text)
        else:
            if '[WARN]' in text:
                self.ui.text_print.setTextColor('red')
            elif '[SCENE]' in text:
                self.ui.text_print.setTextColor('green')
            print(f'[DEBUG] {timenow} {text}')
            text = f'{timenow} {text}'

        self.ui.text_print.append(text)
        self.ui.text_print.ensureCursorVisible()
        self.ui.text_print.setTextColor('black')

    def text_num_update_func(self, text: str):
        """输出内容至文本框“完成情况”"""
        timenow = time.strftime("%H:%M:%S")
        self.ui.text_num.setText(text)
        text = f'{timenow} [NUM] {text}'
        print(f'[DEBUG] {text}')  # 输出至控制台调试
        self.log_write(text)

    def text_wininfo_update_func(self, text: str):
        """输出窗口信息"""
        timenow = time.strftime("%H:%M:%S")
        self.ui.text_wininfo.setText(text)
        text = text.replace('\n', ' ')
        text = f'{timenow} [WINDOW] {text}'
        print(f'[DEBUG] {text}')
        self.log_write(text)

    def resources(self):
        """环境检测按钮"""
        picpath = fpath / 'pic'
        handle_coor = window.getInfo_Window()  # 游戏窗口
        # log检测
        if not self.log_init():
            QMessageBox.critical(self, 'ERROR', '创建log目录失败，请重试！')
        # 图片资源检测
        elif not picpath.exists():
            QMessageBox.critical(self, 'ERROR', '图片资源不存在！')
            self.log_write('[ERROR] no pic')
        # 图片资源是否完整
        elif not self.pic_is_complete():
            pass
        # 游戏环境检测
        elif handle_coor == (0, 0, 0, 0):
            QMessageBox.critical(self, 'ERROR', '请打开游戏！')
            self.log_write('[ERROR] no game')
        elif handle_coor[0] < -9 or handle_coor[1] < 0 or handle_coor[2] < 0 or handle_coor[3] < 0:
            QMessageBox.critical(self, 'ERROR', '请前置游戏窗口！')
            self.log_write('[ERROR] no pre-game')
        elif handle_coor[2] - handle_coor[0] != window.absolute_window_width and handle_coor[3] - handle_coor[
            1] != window.absolute_window_height:
            QMessageBox.critical(self, 'ERROR', '窗口大小不匹配!')
            self.log_write('[ERROR] no right size')
        # 环境完整
        else:
            self.ui.button_resources.setEnabled(False)
            self.ui.button_resources.setText('环境完整')
            self.ui.combo_choice.setEnabled(True)
            self.ui.spinB_num.setEnabled(True)
            self.ui.text_miaoshu.setPlaceholderText('使用过程中，请不要移动游戏窗口，会导致点击位置错误\n请选择功能以加载内容')
            # 悬赏封印
            thread_xuanshang = Thread(target=xuanshangfengyin.XuanShangFengYin().judge)
            thread_xuanshang.daemon = True
            thread_xuanshang.start()

    def wininfo_update(self):
        """更新窗口信息"""
        window.getInfo_Window()

    def choice_text(self):
        """功能描述"""
        text = self.ui.combo_choice.currentText()
        self.ui.button_start.setEnabled(True)
        self.ui.spinB_num.setEnabled(True)
        # self.is_fighting_yuhun(False)
        self.ui.stackedWidget.setCurrentIndex(0)  # 索引0，空白
        if text == self._list_function[0]:
            # 1.组队御魂副本
            self._choice = 1
            self.ui.text_miaoshu.setPlainText('请确保阵容稳定，仅适用于队友挂饼，不适用于极限卡速，默认打手\
                                               待开发：手动第一次锁定阵容')
            self.ui.stackedWidget.setCurrentIndex(1)  # 索引1，御魂
            # 默认值
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 200)
            # self.is_fighting_yuhun(True)
            self.ui.button_driver_False.setChecked(True)
            self.ui.button_passengers_2.setChecked(True)
        elif text == self._list_function[1]:
            # 2.组队永生之海副本
            self._choice = 2
            self.ui.text_miaoshu.setPlainText('默认打手30次\
                                               阴阳师技能自行选择，如晴明灭\
                                               待开发：手动第一次锁定阵容')
            self.ui.stackedWidget.setCurrentIndex(1)  # 索引1，御魂
            # 默认值
            self.ui.spinB_num.setValue(30)
            self.ui.spinB_num.setRange(1, 100)
            # self.is_fighting_yuhun(True)
            self.ui.button_driver_False.setChecked(True)
            self.ui.button_passengers_2.setChecked(True)
        elif text == self._list_function[2]:
            # 3.业原火副本
            self._choice = 3
            self.ui.text_miaoshu.setPlainText('默认为“痴”，有“贪”“嗔”需求的，可替换pic路径下"tiaozhan.png"素材')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)
        elif text == self._list_function[3]:
            # 4.御灵副本
            self._choice = 4
            self.ui.text_miaoshu.setPlainText('暗神龙-周二六日\
                                                   暗白藏主-周三六日\
                                                   暗黑豹-周四六\
                                                   暗孔雀-周五六日\
                                                   绘卷期间请减少使用')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)
        elif text == self._list_function[4]:
            # 5.个人突破
            self._choice = 5
            self.ui.text_miaoshu.setPlainText('默认3胜刷新，上限30')
            # self.ui.stackedWidget.setCurrentIndex(2)  # 索引2，结界突破
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 30)
        elif text == self._list_function[5]:
            # 6.寮突破
            self._choice = 6
            self.ui.text_miaoshu.setPlainText('请锁定阵容，默认上限6次\
                                                   待开发：滚轮翻页')
            self.ui.spinB_num.setValue(6)
            self.ui.spinB_num.setRange(1, 6)
        elif text == self._list_function[6]:
            # 7.道馆突破
            self._choice = 7
            self.ui.text_miaoshu.setPlainText('目前仅支持正在进行中的道馆突破，无法实现跳转道馆场景\
                                               待开发：冷却时间、观战助威')
            self.ui.stackedWidget.setCurrentIndex(3)  # 索引3，道馆突破
            self.ui.spinB_num.setEnabled(False)

        elif text == self._list_function[7]:
            # 8.普通召唤
            self._choice = 8
            self.ui.text_miaoshu.setPlainText('普通召唤，请选择十连次数')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)
        elif text == self._list_function[8]:
            # 9.百鬼夜行
            self._choice = 9
            self.ui.text_miaoshu.setPlainText('仅适用于清票，且无法指定鬼王')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)
        elif text == self._list_function[9]:
            # 10.限时活动
            self._choice = 10
            self.ui.text_miaoshu.setPlainText('适用于限时活动及其他连点，请提前确保阵容完好并锁定，替换pic文件夹huodong下的title.png、tiaozhan.png，周年庆活动素材已替换')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 999)
        elif text == self._list_function[10]:
            # 11.组队日轮副本
            self._choice = 11
            self.ui.text_miaoshu.setPlainText('请确保阵容稳定，仅适用于队友挂饼，不适用于极限卡速，默认打手\
                                               待开发：手动第一次锁定阵容')
            self.ui.stackedWidget.setCurrentIndex(1)  # 索引1，御魂
            # 默认值
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)
            self.ui.button_driver_False.setChecked(True)
            self.ui.button_passengers_2.setChecked(True)

    def start(self):
        """开始按钮"""
        n = self.ui.spinB_num.value()
        self.ui.text_num.clear()
        self.is_fighting(True)
        thread = None  # 线程
        if self._choice == 1:
            # 1.组队御魂副本
            # 是否司机（默认否）
            # 组队人数（默认2人）
            driver = self.ui.buttonGroup_driver.checkedButton().text()
            if driver == '否':
                flag_driver = False
            else:
                flag_driver = True
            flag_passengers = int(self.ui.buttonGroup_passengers.checkedButton().text())
            thread = Thread(target=yuhun.YuHun().run, args=(n, flag_driver, flag_passengers))
        elif self._choice == 2:
            # 2.组队永生之海副本
            # 是否司机（默认否）
            driver = self.ui.buttonGroup_driver.checkedButton().text()
            if driver == '否':
                flag_driver = False
            else:
                flag_driver = True
            thread = Thread(target=yongshengzhihai.YongShengZhiHai().run, args=(n, flag_driver))
        elif self._choice == 3:
            # 3.业原火
            thread = Thread(target=yeyuanhuo.YeYuanHuo().run, args=(n,))
        elif self._choice == 4:
            # 4.御灵
            thread = Thread(target=yuling.YuLing().run, args=(n,))
        elif self._choice == 5:
            # 5.个人突破
            thread = Thread(target=jiejietupo.JieJieTuPoGeRen().run, args=(n,))
        elif self._choice == 6:
            # 6.寮突破
            thread = Thread(target=jiejietupo.JieJieTuPoYinYangLiao().run, args=(n,))
        elif self._choice == 7:
            # 7.道馆突破
            flag_guanzhan = self.ui.button_guanzhan.isChecked()
            thread = Thread(target=daoguantupo.DaoGuanTuPo().run, args=(flag_guanzhan,))
        elif self._choice == 8:
            # 8.普通召唤
            thread = Thread(target=zhaohuan.ZhaoHuan().run, args=(n,))
        elif self._choice == 9:
            # 9.百鬼夜行
            thread = Thread(target=baiguiyexing.BaiGuiYeXing().run, args=(n,))
        elif self._choice == 10:
            # 10.限时活动
            thread = Thread(target=huodong.HuoDong().run, args=(n,))
        elif self._choice == 11:
            # 1.组队日轮副本
            # 是否司机（默认否）
            # 组队人数（默认2人）
            driver = self.ui.buttonGroup_driver.checkedButton().text()
            if driver == '否':
                flag_driver = False
            else:
                flag_driver = True
            flag_passengers = int(self.ui.buttonGroup_passengers.checkedButton().text())
            thread = Thread(target=rilun.RiLun().run, args=(n, flag_driver, flag_passengers))

        # 线程存在
        if thread is not None:
            thread.daemon = True  # 线程守护
            thread.start()
        # 进行中
        self.is_fighting(True)

    def is_fighting(self, flag: bool):
        """程序是否运行中，启用/禁用其他控件"""
        if flag:
            self.ui.button_start.setText('进行中')
        else:
            self.ui.button_start.setText('开始')
        self.ui.combo_choice.setEnabled(not flag)
        self.ui.spinB_num.setEnabled(not flag)
        self.ui.button_start.setEnabled(not flag)
        # 御魂类小按钮
        self.ui.button_driver_False.setEnabled(not flag)
        self.ui.button_driver_True.setEnabled(not flag)
        self.ui.button_passengers_2.setEnabled(not flag)
        self.ui.button_passengers_3.setEnabled(not flag)

    def is_fighting_yuhun(self, flag: bool):
        """初始化组队御魂副本默认配置，显示/隐藏其他控件"""
        if flag:
            self.ui.label_driver.show()
            self.ui.button_driver_False.show()
            self.ui.button_driver_True.show()
            self.ui.label_passengers.show()
            self.ui.button_passengers_2.show()
            self.ui.button_passengers_3.show()
            self.ui.button_driver_False.setChecked(True)
            self.ui.button_passengers_2.setChecked(True)
        else:
            self.ui.label_driver.hide()
            self.ui.button_driver_False.hide()
            self.ui.button_driver_True.hide()
            self.ui.label_passengers.hide()
            self.ui.button_passengers_2.hide()
            self.ui.button_passengers_3.hide()

    # update info
    def update_info(self):
        self.update_win_ui = UpdateWindow()
        self.update_win_ui.show()

    # auto update
    def update_auto(self):
        url_releases_1 = "https://github.com/AquamarineCyan/Onmyoji_Python/releases"
        url_releases_2 = "https://hub.fastgit.xyz/AquamarineCyan/Onmyoji_Python/releases"
        url_releases_3 = "https://hub.fastgit.org/AquamarineCyan/Onmyoji_Python/releases"
        url_update = "https://raw.fastgit.org/AquamarineCyan/Onmyoji_Python/main/update.json"
        try:
            r = httpx.get(url_update)
            if r.status_code == 200:
                data = json.loads(r.text)
                update_version = data["version"]
                update_version_info = data["version_info"]
                if version < update_version:
                    ms.text_print_update.emit(f'[WARN] 有新版本 {update_version}')
                    ms.text_print_update.emit(f'更新内容\n{update_version_info}')
                    ms.text_print_update.emit(f'[WARN] 可前往链接下载，删除原文件，重新解压，如替换可能会造成pic资源问题')
                    ms.text_print_update.emit(f'链接1：{url_releases_1}')
                    ms.text_print_update.emit(f'推荐链接2：{url_releases_2}')
                    ms.text_print_update.emit(f'链接3：{url_releases_3}')
                else:
                    ms.text_print_update.emit('暂无更新')
            else:
                ms.text_print_update.emit('自动检查更新失败，请稍后重试')
        except:
            ms.text_print_update.emit('[WARN] 自动检查更新失败，请稍后重试')

    # clean log
    def clean_log(self):
        self.log_remove()

    # GitHub地址
    def GitHub_address(self):
        QMessageBox.information(self, 'GitHub', 'https://github.com/AquamarineCyan/Onmyoji_Python')

    # 退出
    def exit(self):
        try:
            self.log_write('[EXIT]')
        except:
            pass
        sys.exit()


class UpdateWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        icon = QIcon()
        icon.addPixmap(QPixmap('buzhihuo.ico'))
        self.setWindowIcon(icon)
        # 关联事件
        ms.updateui_textBrowser_update.connect(self.textBrowser_update)
        # 初始化
        update.update_record()

    def textBrowser_update(self, text: str):
        print('[update info]', text)  # 控制台调试输出
        self.ui.textBrowser.append(text)
        self.ui.textBrowser.ensureCursorVisible()
        self.ui.textBrowser.moveCursor(QTextCursor.Start)


if __name__ == '__main__':
    if windll.shell32.IsUserAnAdmin():  # 是否以管理员身份运行
        print("管理员")
        app = QApplication([])
        main_win_ui = MainWindow()
        main_win_ui.show()
        app.exec()
    else:
        windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)  # 调起UAC以管理员身份运行
        sys.exit(0)
