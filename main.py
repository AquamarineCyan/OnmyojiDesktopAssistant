#!/usr/bin/env python3
# main_old.py

import sys
import pyautogui

from package import *
import time
from pathlib import Path
from threading import Thread

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QWidget, QTextBrowser
from PySide6.QtCore import QObject, Signal
from myui import Ui_MainWindow

version: str = '1.6'
"""版本号"""
fpath = Path.cwd()
"""文件路径"""


class MySignals(QObject):
    """自定义信号类"""
    # 自定义事件+参数类型
    text_print_update = Signal(str)
    text_num_update = Signal(str)


# 自定义信号类实例化
ms = MySignals()

"""
已知bug：子类无法成功调用父类的自定义信号
bug修复期间，使用# *#注明
代码存在冗余
"""


class MainWindow(QMainWindow):
    _handle_infodict = {
        0: '窗口横坐标',
        1: '窗口纵坐标',
        2: '窗口宽度',
        3: '窗口高度'
    }
    _list_function = [
        '1.组队御魂副本',
        '2.普通召唤',
        '3.寮突破',
        '4.个人突破',
        '5.百鬼夜行',
        '6.道馆突破',
        '7.御灵',
        '8.绘卷查分'
    ]
    _choice: int

    def __init__(self):
        super().__init__()
        # 使用ui文件导入定义界面类
        self.ui = Ui_MainWindow()
        # 初始化界面
        self.ui.setupUi(self)
        icon = QIcon()
        icon.addPixmap(QPixmap('buzhihuo.ico'))
        self.setWindowIcon(icon)
        # 初始化控件
        self.ui.combo_choice.addItems(self._list_function)
        self.ui.text_print.append(f'version={version}')
        # self.ui.text_print.append('仅供内部测试使用，请勿外传，本程序所产生的一切后果自负')
        # self.ui.text_print.append('如需中断程序，请将鼠标置于屏幕四角，这将触发安全措施')
        self.ui.button_start.setEnabled(False)
        self.ui.combo_choice.setEnabled(False)
        self.ui.spinB_num.setEnabled(False)
        self.ui.text_miaoshu.setPlaceholderText('仅供内部测试使用，请勿外传，本程序所产生的一切后果自负\
                                                请确认您是使用管理员权限打开本程序\
                                                请先运行“环境检测”')
        self.is_1_yuhun(False)
        self.ui.text_print.document().setMaximumBlockCount(50)
        # 关联事件
        self.ui.button_resources.clicked.connect(self.resources)  # 资源检测按钮
        self.ui.button_start.clicked.connect(self.start)  # 开始按钮
        self.ui.combo_choice.currentIndexChanged.connect(self.choice_text)  # 功能选择事件
        # 菜单栏
        self.ui.action_GitHub.triggered.connect(self.GitHub)  # GitHub地址
        self.ui.action_exit.triggered.connect(self.exit)  # 退出
        # 自定义信号
        ms.text_print_update.connect(self.text_print_update_signal)
        ms.text_num_update.connect(self.text_num_update_signal)

    def resources(self):
        """环境检测按钮"""
        picpath = fpath / 'pic'
        handle_coor = window.GetInfo_Window()  # 游戏窗口检测
        # 图片资源检测
        if not picpath.exists():
            QMessageBox.critical(self, 'ERROR', '图片资源不存在！')
        # 游戏环境检测
        elif handle_coor == (0, 0, 0, 0):
            QMessageBox.critical(self, 'ERROR', '请打开游戏！')
        elif handle_coor[0] < 0 or handle_coor[1] < 0 or handle_coor[2] < 0 or handle_coor[3] < 0:
            QMessageBox.critical(self, 'ERROR', '请前置游戏窗口！')
        elif not log.logInit():
            QMessageBox.critical(self, 'ERROR', '创建log目录失败，请重试！')
        # 环境完整
        else:
            self.ui.button_resources.setEnabled(False)
            self.ui.button_resources.setText('环境完整')
            self.ui.combo_choice.setEnabled(True)
            self.ui.spinB_num.setEnabled(True)
            self.ui.text_miaoshu.setPlaceholderText('使用过程中，请不要移动游戏窗口，会导致点击位置错误\n请选择功能以加载内容')
            for i in range(4):
                if i == 0:
                    self.text_print_update_signal(f'{self._handle_infodict[i]}：{handle_coor[i] + 9}')
                else:
                    self.text_print_update_signal(f'{self._handle_infodict[i]}：{handle_coor[i]}')

    def choice_text(self):
        """功能描述"""
        text = self.ui.combo_choice.currentText()
        self.ui.button_start.setEnabled(True)
        self.ui.spinB_num.setEnabled(True)
        self.is_1_yuhun(False)
        if text == self._list_function[0]:
            # 1.组队御魂副本
            self._choice = 1
            self.ui.text_miaoshu.setPlainText('请确保阵容稳定，仅适用于队友挂饼，不适用于极限卡速，默认打手')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 200)
            self.is_1_yuhun(True)
        elif text == self._list_function[1]:
            # 2.普通召唤
            self._choice = 2
            self.ui.text_miaoshu.setPlainText('普通召唤，请选择十连次数')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)
        elif text == self._list_function[2]:
            # 3.寮突破
            self._choice = 3
            self.ui.text_miaoshu.setPlainText('请锁定阵容，默认上限6次\n待开发：滚轮翻页')
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
            self.ui.text_miaoshu.setPlainText('目前仅支持正在进行中的道馆突破，无法实现跳转道馆场景\n待开发：冷却时间、观战助威')
            self.ui.spinB_num.setEnabled(False)
        elif text == self._list_function[6]:
            # 7.御灵副本
            self._choice = 7
            self.ui.text_miaoshu.setPlainText('绘卷期间请减少使用')
            self.ui.spinB_num.setValue(1)
            self.ui.spinB_num.setRange(1, 100)
        elif text == self._list_function[7]:
            # 8.绘卷查分
            self._choice = 8
            self.ui.text_miaoshu.setPlainText('待实现')
            self.ui.spinB_num.setEnabled(False)

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
            thread = Thread(target=self.run_1_yuhun, args=(n, flag_driver, flag_passengers))
            thread.daemon = True
            self.ui.text_num.setText(f'0/{n}')
            thread.start()
        elif self._choice == 2:
            # 2.普通召唤
            thread = Thread(target=self.run_2_zhaohuan, args=(n,))
            thread.daemon = True
            self.ui.text_num.setText(f'0/{n}')
            thread.start()
        elif self._choice == 3:
            # 3.寮突破
            # *#thread = Thread(target=jiejietupo.JieJieTuPoYinYangLiao.run, args=(self,n,))
            thread = Thread(target=self.run_3_tupo_yinyangliao, args=(n,))
            thread.daemon = True
            self.ui.text_num.setText(f'0/{n}')
            thread.start()
        elif self._choice == 4:
            # 4.个人突破
            self.is_fighting(True)
            thread = Thread(target=self.run_4_tupo_geren, args=(n,))
            thread.daemon = True
            self.ui.text_num.setText(f'0/{n}')
            thread.start()
        elif self._choice == 5:
            # 5.百鬼夜行
            # baiguiyexing.Run_BaiGuiYeXing(n)
            pass
        elif self._choice == 6:
            # 6.道馆突破
            self.is_fighting(True)
            thread = Thread(target=self.run_6_daoguantupo)
            thread.daemon = True
            thread.start()
        elif self._choice == 7:
            # 7.御灵
            # yuling.run_yuling(n)
            pass
        elif self._choice == 8:
            # 8.绘卷查分
            # thread = Thread(target=self.test)
            # thread.start()
            pass
        self.is_fighting(True)

    def is_1_yuhun(self, flag: bool):
        ###初始化组队御魂副本默认配置，显示/隐藏其他控件###
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

    def text_print_update_signal(self, text: str):
        """
        输出内容至文本框

        :param text: 文本
        """
        print(text)  # 输出至控制台调试
        log.logWrite(text)
        self.ui.text_print.append(text)
        self.ui.text_print.ensureCursorVisible()

    def text_num_update_signal(self, text: str):
        """
        输出内容至文本框“完成情况”

        :param text: 文本
        """
        print(text)  # 输出至控制台调试
        log.logWrite(text)
        self.ui.text_num.setText(text)

    """
    功能主程序
    run_num_function(*n,**arges)
    """

    # 1.组队御魂副本
    def run_1_yuhun(self, n: int, flag_driver: bool = False, flag_passengers: int = 2):
        """
        御魂副本主程序

        :param n: 次数
        :param flag_driver: 是否司机（默认否）
        :param flag_passengers: 人数（默认2人）
        """
        picpath = 'yuhun'  # 图片路径
        flag_driver: bool  # 是否为司机
        flag_passengers: int  # 组队人数
        flag_driver_start: bool  # 司机待机
        flag_fighting: bool  # 是否进行中对局
        flag_passenger_2: bool  # 队员2就位
        flag_passenger_3: bool  # 队员3就位
        x: int
        y: int
        m = 0  # 计数器
        time.sleep(2)
        yh = yuhun.yuhun()
        while m < n:
            flag_fighting = False
            flag_driver_start = False
            if yh.scene():
                flag_driver_start = True
                self.text_print_update_signal('场景：御魂组队')
            else:
                flag_fighting = True
                self.text_print_update_signal('场景：进行中对局')
            # driver
            if flag_driver_start and flag_driver:
                self.text_print_update_signal('waitng for passengers')
                # 队员2就位
                while 1:
                    x, y = function.get_coor_info_picture(f'{picpath}/passenger_2.png')
                    if x == 0 and y == 0:
                        flag_passenger_2 = True
                        self.text_print_update_signal('passenger 2 is already')
                        break
                # 是否3人组队
                if flag_passengers == 3:
                    while 1:
                        x, y = function.get_coor_info_picture(f'{picpath}/passenger_3.png')
                        if x == 0 and y == 0:
                            flag_passenger_3 = True
                            self.text_print_update_signal('passenger 3 is already')
                            break
                # start
                function.judge_click(f'{picpath}/tiaozhan.png')
            if not flag_fighting:
                function.judge_click(f'{picpath}/fighting.png', False)
                flag_fighting = False
                self.text_print_update_signal('对局进行中...')
            yh.finish()
            m += 1
            self.ui.text_num.setText(f'{m}/{n}')
            time.sleep(2)
        self.is_fighting(False)

    # 2.普通召唤
    def run_2_zhaohuan(self, n: int):
        flag = True
        flag_title = True  # 场景提示
        zh = zhaohuan.zhaohuan()
        while 1:
            if zh.title():
                ms.text_print_update.emit('场景：召唤')
                time.sleep(2)
                m = 0  # 计数器
                while m < n:
                    if flag:
                        zh.first()
                        flag = False
                    else:
                        zh.again()
                    m += 1
                    ms.text_num_update.emit(f'{m}/{n}')
                break
            elif flag_title:
                flag_title = False
                ms.text_print_update.emit('请检查游戏场景')
        self.is_fighting(False)

    # 3.阴阳寮突破
    def run_3_tupo_yinyangliao(self, n: int):
        """
        阴阳寮突破主程序

        :param n: 次数
        """
        picpath = 'jiejietupo'
        time.sleep(2)
        function.judge_scene(f'{picpath}/title.png')
        ms.text_print_update.emit('场景：结界突破')
        time.sleep(2)
        while 1:
            if function.judge_scene(f'{picpath}/tupojilu.png'):
                break
            else:
                function.judge_click(f'{picpath}/yinyangliao.png')
                time.sleep(4)
        time.sleep(2)
        tp = jiejietupo.JieJieTuPoYinYangLiao()
        m = 0  # 计数器
        while m < n:
            flag = tp.fighting()
            if flag:
                m += 1
                ms.text_num_update.emit(f'{m}/{n}')
            elif flag == -1:
                break
            time.sleep(3)
        self.is_fighting(False)

    # 4.个人突破
    def run_4_tupo_geren(self, n: int):
        """
        个人突破主程序

        :param n: 次数
        """
        picpath = 'jiejietupo'
        time.sleep(2)
        function.judge_scene(f'{picpath}/title.png', '结界突破')
        time.sleep(2)
        tp = jiejietupo.JieJieTuPoGeRen()
        tp.scene()
        time.sleep(2)
        m = 0  # 计数器
        while m < n:
            list_xunzhang = jiejietupo.list_num_xunzhang()
            # 打法 胜3刷新
            tupo_victory = list_xunzhang.count(-1)
            if tupo_victory == 3:
                tp.refresh()
            elif tupo_victory < 3:
                ms.text_print_update.emit(f'已攻破{tupo_victory}个')
                tp.fighting(list_xunzhang, tupo_victory)
                m += 1
                ms.text_num_update.emit(f'{m}/{n}')
            elif tupo_victory > 3:
                ms.text_print_update.emit('暂不支持大于3个，请自行处理')
                break
            time.sleep(3)
        self.is_fighting(False)

    # 5.百鬼夜行
    def run_5_baiguiyexing(self, n: int):
        m = 0  # 计数器
        while m < n:
            bgyx = baiguiyexing.baiguiyexing()
            if bgyx.title():
                time.sleep(1)
                function.random_sleep(0, 2)
                bgyx.start()
                function.random_sleep(1, 3)
                bgyx.choose()
                function.random_sleep(2, 4)
                bgyx.fighting()
                function.random_sleep(2, 4)
                bgyx.finish()
                m += 1
                ms.text_num_update.emit(f'{m}/{n}')
                time.sleep(4)
        self.is_fighting(False)

    # 6.道馆突破
    def run_6_daoguantupo(self):
        """道馆突破主程序"""
        picpath = 'daoguantupo'
        time.sleep(2)
        flag_title = True  # 场景提示
        flag_fighting = False  # 进行中
        flag_daojishi = True  # 倒计时
        flag_result = False  # 结束
        dgtp = daoguantupo.daoguantupo()
        # 场景判断
        while 1:
            if dgtp.title():
                while 1:
                    if dgtp.judge_scene() == '倒计时':
                        if flag_daojishi:
                            ms.text_print_update.emit('等待系统自行进入')
                            flag_daojishi = False
                        flag_fighting = True
                        time.sleep(10)
                    else:
                        break
                break
            elif dgtp.judge_scene() == '进行中':
                ms.text_print_update.emit('道馆突破进行中')
                flag_fighting = True
                break
            elif flag_title:
                flag_title = False
                ms.text_print_update.emit('请检查游戏场景')
        time.sleep(2)
        if not flag_fighting:
            function.judge_click(f'{picpath}/tiaozhan.png')
        time.sleep(4)
        # start
        n = 0  # 计数器
        while 1:
            scene = {
                f'{picpath}/zhunbei.png': '准备',
                'victory.png': '胜利',
                'fail.png': '失败'
            }
            for item in scene.keys():
                x, y = function.get_coor_info_picture(item)
                if x != 0 and y != 0:
                    if item == f'{picpath}/zhunbei.png':
                        n += 1
                        self.ui.text_num.setText(str(n))
                    if item == 'victory.png' or item == 'fail.png':
                        time.sleep(2)
                        flag_result = True
                    ms.text_print_update.emit(scene[item])
                    pyautogui.moveTo(x, y, duration=0.5)
                    pyautogui.click()
                    break
            time.sleep(4)
            if flag_result:
                break
        self.is_fighting(False)

    # 7.御灵
    def run_7_yuling(self, n: int):
        flag_title = True  # 场景提示
        yl = yuling.yuling()
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
        self.is_fighting(False)

    # 8.绘卷查分
    # 咕咕咕
    # GitHub地址
    def GitHub(self):
        QMessageBox.information(self, 'GitHub', 'https://github.com/AquamarineCyan/Onmyoji_Python')

    # 退出
    def exit(self):
        sys.exit()


if __name__ == '__main__':
    app = QApplication([])
    main_win_ui = MainWindow()
    main_win_ui.show()
    app.exec()
