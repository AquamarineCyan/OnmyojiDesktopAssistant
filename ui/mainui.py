# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainui.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QGroupBox, QLabel, QLineEdit, QMainWindow,
    QMenu, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QSpinBox, QStackedWidget, QTextBrowser,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(550, 450)
        MainWindow.setStyleSheet(u"")
        self.exit = QAction(MainWindow)
        self.exit.setObjectName(u"exit")
        self.action_exit = QAction(MainWindow)
        self.action_exit.setObjectName(u"action_exit")
        font = QFont()
        font.setFamilies([u"\u5b8b\u4f53"])
        self.action_exit.setFont(font)
        self.action_update = QAction(MainWindow)
        self.action_update.setObjectName(u"action_update")
        self.action_update.setFont(font)
        self.action_GitHub = QAction(MainWindow)
        self.action_GitHub.setObjectName(u"action_GitHub")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.groupBox_basic = QGroupBox(self.centralwidget)
        self.groupBox_basic.setObjectName(u"groupBox_basic")
        self.groupBox_basic.setGeometry(QRect(10, 10, 261, 201))
        self.groupBox_basic.setFont(font)
        self.text_miaoshu = QTextBrowser(self.groupBox_basic)
        self.text_miaoshu.setObjectName(u"text_miaoshu")
        self.text_miaoshu.setGeometry(QRect(10, 120, 241, 71))
        self.button_start = QPushButton(self.groupBox_basic)
        self.button_start.setObjectName(u"button_start")
        self.button_start.setGeometry(QRect(130, 90, 71, 23))
        font1 = QFont()
        font1.setFamilies([u"\u5b8b\u4f53"])
        font1.setPointSize(10)
        self.button_start.setFont(font1)
        self.button_resources = QPushButton(self.groupBox_basic)
        self.button_resources.setObjectName(u"button_resources")
        self.button_resources.setGeometry(QRect(30, 89, 71, 23))
        self.button_resources.setFont(font1)
        self.combo_choice = QComboBox(self.groupBox_basic)
        self.combo_choice.setObjectName(u"combo_choice")
        self.combo_choice.setGeometry(QRect(100, 20, 121, 19))
        font2 = QFont()
        font2.setFamilies([u"\u5b8b\u4f53"])
        font2.setPointSize(9)
        self.combo_choice.setFont(font2)
        self.label_2 = QLabel(self.groupBox_basic)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(30, 23, 26, 15))
        self.label_2.setFont(font1)
        self.spinB_num = QSpinBox(self.groupBox_basic)
        self.spinB_num.setObjectName(u"spinB_num")
        self.spinB_num.setGeometry(QRect(100, 51, 51, 19))
        self.spinB_num.setFont(font1)
        self.spinB_num.setMaximum(999)
        self.label_3 = QLabel(self.groupBox_basic)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(30, 53, 26, 15))
        self.groupBox_senior = QGroupBox(self.centralwidget)
        self.groupBox_senior.setObjectName(u"groupBox_senior")
        self.groupBox_senior.setGeometry(QRect(280, 10, 261, 201))
        self.stackedWidget = QStackedWidget(self.groupBox_senior)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(10, 20, 231, 161))
        self.none = QWidget()
        self.none.setObjectName(u"none")
        self.stackedWidget.addWidget(self.none)
        self.yuhun = QWidget()
        self.yuhun.setObjectName(u"yuhun")
        self.label_driver = QLabel(self.yuhun)
        self.label_driver.setObjectName(u"label_driver")
        self.label_driver.setGeometry(QRect(32, 40, 48, 21))
        font3 = QFont()
        font3.setPointSize(9)
        self.label_driver.setFont(font3)
        self.button_driver_False = QRadioButton(self.yuhun)
        self.buttonGroup_driver = QButtonGroup(MainWindow)
        self.buttonGroup_driver.setObjectName(u"buttonGroup_driver")
        self.buttonGroup_driver.addButton(self.button_driver_False)
        self.button_driver_False.setObjectName(u"button_driver_False")
        self.button_driver_False.setGeometry(QRect(90, 40, 38, 20))
        self.button_driver_False.setFont(font3)
        self.button_driver_False.setMouseTracking(True)
        self.button_driver_True = QRadioButton(self.yuhun)
        self.buttonGroup_driver.addButton(self.button_driver_True)
        self.button_driver_True.setObjectName(u"button_driver_True")
        self.button_driver_True.setGeometry(QRect(140, 40, 38, 20))
        self.button_driver_True.setFont(font3)
        self.button_passengers_3 = QRadioButton(self.yuhun)
        self.buttonGroup_passengers = QButtonGroup(MainWindow)
        self.buttonGroup_passengers.setObjectName(u"buttonGroup_passengers")
        self.buttonGroup_passengers.addButton(self.button_passengers_3)
        self.button_passengers_3.setObjectName(u"button_passengers_3")
        self.button_passengers_3.setGeometry(QRect(140, 80, 33, 20))
        self.button_passengers_3.setFont(font3)
        self.button_passengers_2 = QRadioButton(self.yuhun)
        self.buttonGroup_passengers.addButton(self.button_passengers_2)
        self.button_passengers_2.setObjectName(u"button_passengers_2")
        self.button_passengers_2.setGeometry(QRect(91, 80, 33, 20))
        self.button_passengers_2.setFont(font3)
        self.label_passengers = QLabel(self.yuhun)
        self.label_passengers.setObjectName(u"label_passengers")
        self.label_passengers.setGeometry(QRect(32, 80, 48, 21))
        self.label_passengers.setFont(font3)
        self.stackedWidget.addWidget(self.yuhun)
        self.jiejietupo = QWidget()
        self.jiejietupo.setObjectName(u"jiejietupo")
        self.button_jiejietupo_3victory = QRadioButton(self.jiejietupo)
        self.button_jiejietupo_3victory.setObjectName(u"button_jiejietupo_3victory")
        self.button_jiejietupo_3victory.setGeometry(QRect(80, 60, 43, 20))
        self.button_kaji = QCheckBox(self.jiejietupo)
        self.button_kaji.setObjectName(u"button_kaji")
        self.button_kaji.setGeometry(QRect(80, 100, 47, 20))
        self.button_jiejietupo_3victory_2 = QRadioButton(self.jiejietupo)
        self.button_jiejietupo_3victory_2.setObjectName(u"button_jiejietupo_3victory_2")
        self.button_jiejietupo_3victory_2.setGeometry(QRect(140, 60, 43, 20))
        self.label_refresh_rule = QLabel(self.jiejietupo)
        self.label_refresh_rule.setObjectName(u"label_refresh_rule")
        self.label_refresh_rule.setGeometry(QRect(10, 60, 48, 16))
        self.label_refresh_rule.setFont(font3)
        self.stackedWidget.addWidget(self.jiejietupo)
        self.daoguantupo = QWidget()
        self.daoguantupo.setObjectName(u"daoguantupo")
        self.button_guanzhan = QCheckBox(self.daoguantupo)
        self.button_guanzhan.setObjectName(u"button_guanzhan")
        self.button_guanzhan.setGeometry(QRect(60, 40, 47, 20))
        self.stackedWidget.addWidget(self.daoguantupo)
        self.groupBox_info = QGroupBox(self.centralwidget)
        self.groupBox_info.setObjectName(u"groupBox_info")
        self.groupBox_info.setGeometry(QRect(10, 220, 531, 201))
        self.text_num = QLineEdit(self.groupBox_info)
        self.text_num.setObjectName(u"text_num")
        self.text_num.setEnabled(True)
        self.text_num.setGeometry(QRect(270, 30, 71, 21))
        self.text_num.setFont(font2)
        self.text_num.setMaxLength(32764)
        self.button_wininfo = QPushButton(self.groupBox_info)
        self.button_wininfo.setObjectName(u"button_wininfo")
        self.button_wininfo.setGeometry(QRect(22, 26, 101, 31))
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_wininfo.sizePolicy().hasHeightForWidth())
        self.button_wininfo.setSizePolicy(sizePolicy)
        font4 = QFont()
        font4.setPointSize(10)
        self.button_wininfo.setFont(font4)
        self.text_print = QTextBrowser(self.groupBox_info)
        self.text_print.setObjectName(u"text_print")
        self.text_print.setGeometry(QRect(170, 70, 341, 121))
        self.text_print.setFont(font)
        self.text_wininfo = QTextBrowser(self.groupBox_info)
        self.text_wininfo.setObjectName(u"text_wininfo")
        self.text_wininfo.setGeometry(QRect(10, 70, 135, 121))
        sizePolicy1 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.text_wininfo.sizePolicy().hasHeightForWidth())
        self.text_wininfo.setSizePolicy(sizePolicy1)
        self.label = QLabel(self.groupBox_info)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(190, 30, 52, 17))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 550, 22))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.action_update)
        self.menu.addAction(self.action_GitHub)
        self.menu.addAction(self.action_exit)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Onmyoji_Python", None))
        self.exit.setText(QCoreApplication.translate("MainWindow", u"\u9000\u51fa", None))
        self.action_exit.setText(QCoreApplication.translate("MainWindow", u"\u9000\u51fa", None))
        self.action_update.setText(QCoreApplication.translate("MainWindow", u"\u66f4\u65b0\u65e5\u5fd7", None))
        self.action_GitHub.setText(QCoreApplication.translate("MainWindow", u"GitHub\u5730\u5740", None))
        self.groupBox_basic.setTitle(QCoreApplication.translate("MainWindow", u"\u57fa\u672c\u529f\u80fd", None))
        self.text_miaoshu.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u529f\u80fd\u63cf\u8ff0", None))
        self.button_start.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb", None))
        self.button_resources.setText(QCoreApplication.translate("MainWindow", u"\u73af\u5883\u68c0\u6d4b", None))
        self.combo_choice.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u9009\u62e9\u529f\u80fd", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:10pt;\">\u529f\u80fd</span></p></body></html>", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:10pt;\">\u6b21\u6570</span></p></body></html>", None))
        self.groupBox_senior.setTitle(QCoreApplication.translate("MainWindow", u"\u9ad8\u7ea7\u8bbe\u7f6e", None))
        self.label_driver.setText(QCoreApplication.translate("MainWindow", u"\u662f\u5426\u53f8\u673a", None))
        self.button_driver_False.setText(QCoreApplication.translate("MainWindow", u"\u5426", None))
        self.button_driver_True.setText(QCoreApplication.translate("MainWindow", u"\u662f", None))
        self.button_passengers_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.button_passengers_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.label_passengers.setText(QCoreApplication.translate("MainWindow", u"\u7ec4\u961f\u4eba\u6570", None))
        self.button_jiejietupo_3victory.setText(QCoreApplication.translate("MainWindow", u"3\u80dc", None))
        self.button_kaji.setText(QCoreApplication.translate("MainWindow", u"\u5361\u7ea7", None))
        self.button_jiejietupo_3victory_2.setText(QCoreApplication.translate("MainWindow", u"9\u80dc", None))
        self.label_refresh_rule.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0\u89c4\u5219", None))
        self.button_guanzhan.setText(QCoreApplication.translate("MainWindow", u"\u89c2\u6218", None))
        self.groupBox_info.setTitle(QCoreApplication.translate("MainWindow", u"\u4fe1\u606f", None))
        self.text_num.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u5b8c\u6210\u60c5\u51b5", None))
        self.button_wininfo.setText(QCoreApplication.translate("MainWindow", u"\u66f4\u65b0\u7a97\u53e3\u4fe1\u606f", None))
        self.text_print.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8f93\u51fa\u4fe1\u606f", None))
        self.text_wininfo.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u7a97\u53e3\u4fe1\u606f", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:10pt;\">\u5b8c\u6210\u60c5\u51b5</span></p></body></html>", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u83dc\u5355", None))
    # retranslateUi

