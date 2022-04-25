#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# main.py

import sys
import time
from pathlib import Path
from threading import Thread

from PySide6.QtGui import QIcon, QPixmap, QTextCursor
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QWidget

from ui.mainui import Ui_MainWindow
from ui.updateui import Ui_Form
from mysignal import global_ms as ms
from package import *

version: str = '1.6.1'
"""版本号"""
fpath = Path.cwd()
"""文件路径"""


class MainWindow(QMainWindow):
    _list_function = [
        '1.组队御魂副本',
        '2.组队永生之海副本',
        '3.寮突破',
        '4.个人突破',
        '5.百鬼夜行',
        '6.道馆突破',
        '7.御灵',
        '8.普通召唤'
    ]
    _choice: int  # 功能

    def __init__(self):
        super().__init__()
        # 使用ui文件导入定义界面类
        self.ui = Ui_MainWindow()
        # 初始化界面
        self.ui.setupUi(self)
        icon = QIcon()
        icon.addPixmap(QPixmap('buzhihuo.ico'))
        self.setWindowIcon(icon)
        self.setWindowTitle(f'Onmyoji_Python - v{version}')
        timenow = time.strftime("%H:%M:%S")
        log.logWrite('[START]')
        log.logWrite(f'{timenow} [VERSION] {version}')

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
        self.is_fighting_yuhun(False)
        self.ui.text_print.document().setMaximumBlockCount(50)

        # 菜单栏
        self.ui.action_update.triggered.connect(self.update_info)  # 更新日志
        self.ui.action_GitHub.triggered.connect(self.GitHub)  # GitHub地址
        self.ui.action_exit.triggered.connect(self.exit)  # 退出

    def text_print_update_func(self, text: str):
        """
        输出内容至文本框\n
        WARN -> 红色\n
        SCENE -> 绿色\n
        :param text: 文本
        """
        timenow = time.strftime("%H:%M:%S")
        if '[' and ']' not in text:
            text = f'{timenow} [INFO] {text}'
            print(f'[DEBUG] {text}')  # 输出至控制台调试
            log.logWrite(text)
        else:
            if '[WARN]' in text:
                self.ui.text_print.setTextColor('red')
                print(f'[DEBUG] {timenow} {text}')
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
        log.logWrite(text)

    def text_wininfo_update_func(self, text: str):
        """输出窗口信息"""
        timenow = time.strftime("%H:%M:%S")
        self.ui.text_wininfo.setText(text)
        text = text.replace('\n', ' ')
        text = f'{timenow} [WIN] {text}'
        print(f'[DEBUG] {text}')
        log.logWrite(text)

    def resources(self):
        """环境检测按钮"""
        picpath = fpath / 'pic'
        handle_coor = window.getInfo_Window()  # 游戏窗口
        # log检测
        if not log.logInit():
            QMessageBox.critical(self, 'ERROR', '创建log目录失败，请重试！')
        # 图片资源检测
        elif not picpath.exists():
            QMessageBox.critical(self, 'ERROR', '图片资源不存在！')
            log.logWrite('[ERROR] no pic')
        # 游戏环境检测
        elif handle_coor == (0, 0, 0, 0):
            QMessageBox.critical(self, 'ERROR', '请打开游戏！')
            log.logWrite('[ERROR] no game')
        elif handle_coor[0] < 0 or handle_coor[1] < 0 or handle_coor[2] < 0 or handle_coor[3] < 0:
            QMessageBox.critical(self, 'ERROR', '请前置游戏窗口！')
            log.logWrite('[ERROR] no pre-game')
        # 环境完整
        else:
            self.ui.button_resources.setEnabled(False)
            self.ui.button_resources.setText('环境完整')
            self.ui.combo_choice.setEnabled(True)
            self.ui.spinB_num.setEnabled(True)
            self.ui.text_miaoshu.setPlaceholderText('使用过程中，请不要移动游戏窗口，会导致点击位置错误\n请选择功能以加载内容')

    def wininfo_update(self):
        """更新窗口信息"""
        window.getInfo_Window()

    def choice_text(self):
        """功能描述"""
        text = self.ui.combo_choice.currentText()
        self.ui.button_start.setEnabled(True)
        self.ui.spinB_num.setEnabled(True)
        self.is_fighting_yuhun(False)
        if text == self._list_function[0]:
            # 1.组队御魂副本
            self._choice = 1
            self.ui.text_miaoshu.setPlainText('请确保阵容稳定，仅适用于队友挂饼，不适用于极限卡速，默认打手\
                                               待开发：手动第一次锁定阵容')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 200)
            self.is_fighting_yuhun(True)
        elif text == self._list_function[1]:
            # 2.组队永生之海副本
            self._choice = 8
            self.ui.text_miaoshu.setPlainText('默认打手30次\
                                               阴阳师技能自行选择，如晴明灭\
                                               待开发：手动第一次锁定阵容')
            self.ui.spinB_num.setValue(30)
            self.ui.spinB_num.setRange(1, 100)
            self.is_fighting_yuhun(True)
        elif text == self._list_function[2]:
            # 3.寮突破
            self._choice = 3
            self.ui.text_miaoshu.setPlainText('请锁定阵容，默认上限6次\
                                               待开发：滚轮翻页')
            self.ui.spinB_num.setValue(6)
            self.ui.spinB_num.setRange(1, 6)
        elif text == self._list_function[3]:
            # 4.个人突破
            self._choice = 4
            self.ui.text_miaoshu.setPlainText('默认3胜刷新，上限30')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 30)
        elif text == self._list_function[4]:
            # 5.百鬼夜行
            self._choice = 5
            self.ui.text_miaoshu.setPlainText('仅适用于清票，且无法指定鬼王')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)
        elif text == self._list_function[5]:
            # 6.道馆突破
            self._choice = 6
            self.ui.text_miaoshu.setPlainText('目前仅支持正在进行中的道馆突破，无法实现跳转道馆场景\
                                               待开发：冷却时间、观战助威')
            self.ui.spinB_num.setEnabled(False)
        elif text == self._list_function[6]:
            # 7.御灵副本
            self._choice = 7
            self.ui.text_miaoshu.setPlainText('暗神龙-周二六日\
                                               暗白藏主-周三六日\
                                               暗黑豹-周四六\
                                               暗孔雀-周五六日\
                                               绘卷期间请减少使用')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)
        elif text == self._list_function[7]:

            # 8.普通召唤
            self._choice = 2
            self.ui.text_miaoshu.setPlainText('普通召唤，请选择十连次数')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)

    def start(self):
        """开始按钮"""
        n = self.ui.spinB_num.value()
        self.ui.text_num.clear()
        self.is_fighting(True)
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
            thread.daemon = True
            thread.start()
        elif self._choice == 2:
            # 2.普通召唤
            thread = Thread(target=zhaohuan.ZhaoHuan().run, args=(n,))
            thread.daemon = True
            thread.start()
        elif self._choice == 3:
            # 3.寮突破
            thread = Thread(target=jiejietupo.JieJieTuPoYinYangLiao().run, args=(n,))
            thread.daemon = True
            thread.start()
        elif self._choice == 4:
            # 4.个人突破
            thread = Thread(target=jiejietupo.JieJieTuPoGeRen().run, args=(n,))
            thread.daemon = True
            thread.start()
        elif self._choice == 5:
            # 5.百鬼夜行
            thread = Thread(target=baiguiyexing.BaiGuiYeXing().run, args=(n,))
            thread.daemon = True
            thread.start()
        elif self._choice == 6:
            # 6.道馆突破
            thread = Thread(target=daoguantupo.DaoGuanTuPo().run)
            thread.daemon = True
            thread.start()
        elif self._choice == 7:
            # 7.御灵
            thread = Thread(target=yuling.YuLing().run, args=(n,))
            thread.daemon = True
            thread.start()
        elif self._choice == 8:
            # 8.组队永生之海副本
            # 是否司机（默认否）
            driver = self.ui.buttonGroup_driver.checkedButton().text()
            if driver == '否':
                flag_driver = False
            else:
                flag_driver = True
            thread = Thread(target=yongshengzhihai.YongShengZhiHai().run, args=(n, flag_driver))
            thread.daemon = True
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

    """# 7.御灵
    def run_7_yuling(self, n: int):
        flag_title = True  # 场景提示
        yl = yuling.YuLing()
        while 1:
            if yl.title():
                m = 0  # 计数器
                while m < n:
                    time.sleep(1)
                    function.random_sleep(0, 1)
                    yl.start()
                    time.sleep(8)
                    function.result()
                    time.sleep(1)
                    x, y = function.random_finish_left_right()
                    function.random_sleep(1, 3)
                    m += 1
                    ms.text_num_update.emit(f'{m}/{n}')
                break
            elif flag_title:
                flag_title = False
                ms.text_print_update.emit('请检查游戏场景')
        self.is_fighting(False)"""

    # update info
    def update_info(self):
        self.update_win_ui = UpdateWindow()
        self.update_win_ui.show()

    # GitHub地址
    def GitHub(self):
        QMessageBox.information(self, 'GitHub', 'https://github.com/AquamarineCyan/Onmyoji_Python')

    # 退出
    def exit(self):
        log.logWrite('[EXIT]')
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
    app = QApplication([])
    main_win_ui = MainWindow()
    main_win_ui.show()
    app.exec()
