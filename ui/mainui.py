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
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QRadioButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSpinBox, QStackedWidget,
    QTabWidget, QTextBrowser, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(550, 450)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(0, 0, 551, 451))
        self.tab_home = QWidget()
        self.tab_home.setObjectName(u"tab_home")
        self.groupBox_basic = QGroupBox(self.tab_home)
        self.groupBox_basic.setObjectName(u"groupBox_basic")
        self.groupBox_basic.setGeometry(QRect(4, 20, 231, 131))
        font = QFont()
        font.setFamilies([u"\u5b8b\u4f53"])
        self.groupBox_basic.setFont(font)
        self.button_enviroment = QPushButton(self.groupBox_basic)
        self.button_enviroment.setObjectName(u"button_enviroment")
        self.button_enviroment.setGeometry(QRect(70, 90, 71, 23))
        font1 = QFont()
        font1.setFamilies([u"\u5b8b\u4f53"])
        font1.setPointSize(10)
        self.button_enviroment.setFont(font1)
        self.combo_choice = QComboBox(self.groupBox_basic)
        self.combo_choice.setObjectName(u"combo_choice")
        self.combo_choice.setGeometry(QRect(81, 24, 141, 19))
        font2 = QFont()
        font2.setFamilies([u"\u5b8b\u4f53"])
        font2.setPointSize(9)
        self.combo_choice.setFont(font2)
        self.label_2 = QLabel(self.groupBox_basic)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(26, 27, 26, 15))
        self.label_2.setFont(font1)
        self.spinB_num = QSpinBox(self.groupBox_basic)
        self.spinB_num.setObjectName(u"spinB_num")
        self.spinB_num.setGeometry(QRect(81, 55, 51, 19))
        self.spinB_num.setFont(font1)
        self.spinB_num.setMaximum(999)
        self.label_3 = QLabel(self.groupBox_basic)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(26, 57, 26, 15))
        self.groupBox_senior = QGroupBox(self.tab_home)
        self.groupBox_senior.setObjectName(u"groupBox_senior")
        self.groupBox_senior.setGeometry(QRect(6, 156, 221, 201))
        self.stackedWidget = QStackedWidget(self.groupBox_senior)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(10, 20, 201, 161))
        self.none_0 = QWidget()
        self.none_0.setObjectName(u"none_0")
        self.stackedWidget.addWidget(self.none_0)
        self.yuhun_1 = QWidget()
        self.yuhun_1.setObjectName(u"yuhun_1")
        self.label_driver = QLabel(self.yuhun_1)
        self.label_driver.setObjectName(u"label_driver")
        self.label_driver.setGeometry(QRect(20, 40, 48, 21))
        font3 = QFont()
        font3.setPointSize(9)
        self.label_driver.setFont(font3)
        self.button_driver_False = QRadioButton(self.yuhun_1)
        self.buttonGroup_driver = QButtonGroup(MainWindow)
        self.buttonGroup_driver.setObjectName(u"buttonGroup_driver")
        self.buttonGroup_driver.addButton(self.button_driver_False)
        self.button_driver_False.setObjectName(u"button_driver_False")
        self.button_driver_False.setGeometry(QRect(78, 40, 38, 20))
        self.button_driver_False.setFont(font3)
        self.button_driver_False.setMouseTracking(True)
        self.button_driver_True = QRadioButton(self.yuhun_1)
        self.buttonGroup_driver.addButton(self.button_driver_True)
        self.button_driver_True.setObjectName(u"button_driver_True")
        self.button_driver_True.setGeometry(QRect(128, 40, 38, 20))
        self.button_driver_True.setFont(font3)
        self.button_passengers_3 = QRadioButton(self.yuhun_1)
        self.buttonGroup_passengers = QButtonGroup(MainWindow)
        self.buttonGroup_passengers.setObjectName(u"buttonGroup_passengers")
        self.buttonGroup_passengers.addButton(self.button_passengers_3)
        self.button_passengers_3.setObjectName(u"button_passengers_3")
        self.button_passengers_3.setGeometry(QRect(128, 80, 33, 20))
        self.button_passengers_3.setFont(font3)
        self.button_passengers_2 = QRadioButton(self.yuhun_1)
        self.buttonGroup_passengers.addButton(self.button_passengers_2)
        self.button_passengers_2.setObjectName(u"button_passengers_2")
        self.button_passengers_2.setGeometry(QRect(79, 80, 33, 20))
        self.button_passengers_2.setFont(font3)
        self.label_passengers = QLabel(self.yuhun_1)
        self.label_passengers.setObjectName(u"label_passengers")
        self.label_passengers.setGeometry(QRect(20, 80, 48, 21))
        self.label_passengers.setFont(font3)
        self.stackedWidget.addWidget(self.yuhun_1)
        self.jiejietupo_2 = QWidget()
        self.jiejietupo_2.setObjectName(u"jiejietupo_2")
        self.button_jiejietupo_3victory = QRadioButton(self.jiejietupo_2)
        self.button_jiejietupo_3victory.setObjectName(u"button_jiejietupo_3victory")
        self.button_jiejietupo_3victory.setGeometry(QRect(80, 60, 51, 20))
        self.button_kaji = QCheckBox(self.jiejietupo_2)
        self.button_kaji.setObjectName(u"button_kaji")
        self.button_kaji.setGeometry(QRect(80, 100, 47, 20))
        self.button_jiejietupo_9victory = QRadioButton(self.jiejietupo_2)
        self.button_jiejietupo_9victory.setObjectName(u"button_jiejietupo_9victory")
        self.button_jiejietupo_9victory.setGeometry(QRect(140, 60, 51, 20))
        self.label_refresh_rule = QLabel(self.jiejietupo_2)
        self.label_refresh_rule.setObjectName(u"label_refresh_rule")
        self.label_refresh_rule.setGeometry(QRect(10, 60, 48, 16))
        self.label_refresh_rule.setFont(font3)
        self.stackedWidget.addWidget(self.jiejietupo_2)
        self.daoguantupo_3 = QWidget()
        self.daoguantupo_3.setObjectName(u"daoguantupo_3")
        self.button_guanzhan = QCheckBox(self.daoguantupo_3)
        self.button_guanzhan.setObjectName(u"button_guanzhan")
        self.button_guanzhan.setGeometry(QRect(60, 40, 51, 20))
        self.stackedWidget.addWidget(self.daoguantupo_3)
        self.groupBox_info = QGroupBox(self.tab_home)
        self.groupBox_info.setObjectName(u"groupBox_info")
        self.groupBox_info.setGeometry(QRect(250, 10, 281, 411))
        self.text_num = QLineEdit(self.groupBox_info)
        self.text_num.setObjectName(u"text_num")
        self.text_num.setEnabled(True)
        self.text_num.setGeometry(QRect(90, 30, 71, 21))
        self.text_num.setFont(font2)
        self.text_num.setMaxLength(32764)
        self.text_print = QTextBrowser(self.groupBox_info)
        self.text_print.setObjectName(u"text_print")
        self.text_print.setGeometry(QRect(10, 60, 261, 341))
        self.text_print.setFont(font)
        self.label = QLabel(self.groupBox_info)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(22, 32, 52, 17))
        self.button_start = QPushButton(self.tab_home)
        self.button_start.setObjectName(u"button_start")
        self.button_start.setGeometry(QRect(70, 370, 81, 31))
        font4 = QFont()
        font4.setFamilies([u"\u5b8b\u4f53"])
        font4.setPointSize(11)
        font4.setBold(True)
        self.button_start.setFont(font4)
        self.tabWidget.addTab(self.tab_home, "")
        self.tab_setting = QWidget()
        self.tab_setting.setObjectName(u"tab_setting")
        self.scrollArea = QScrollArea(self.tab_setting)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setGeometry(QRect(-4, -1, 551, 431))
        self.scrollArea.setMinimumSize(QSize(0, 0))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 532, 1000))
        self.scrollAreaWidgetContents.setMinimumSize(QSize(0, 1000))
        self.horizontalLayoutWidget = QWidget(self.scrollAreaWidgetContents)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(40, 20, 451, 80))
        self.horizontalLayout_setting_update = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_setting_update.setObjectName(u"horizontalLayout_setting_update")
        self.horizontalLayout_setting_update.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_setting_update.addItem(self.horizontalSpacer)

        self.setting_update_label = QLabel(self.horizontalLayoutWidget)
        self.setting_update_label.setObjectName(u"setting_update_label")

        self.horizontalLayout_setting_update.addWidget(self.setting_update_label)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_setting_update.addItem(self.horizontalSpacer_2)

        self.setting_update_comboBox = QComboBox(self.horizontalLayoutWidget)
        self.setting_update_comboBox.setObjectName(u"setting_update_comboBox")

        self.horizontalLayout_setting_update.addWidget(self.setting_update_comboBox)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_setting_update.addItem(self.horizontalSpacer_3)

        self.horizontalLayoutWidget_2 = QWidget(self.scrollAreaWidgetContents)
        self.horizontalLayoutWidget_2.setObjectName(u"horizontalLayoutWidget_2")
        self.horizontalLayoutWidget_2.setGeometry(QRect(40, 110, 451, 80))
        self.horizontalLayout_setting_xuanshangfengyin = QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_setting_xuanshangfengyin.setObjectName(u"horizontalLayout_setting_xuanshangfengyin")
        self.horizontalLayout_setting_xuanshangfengyin.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_setting_xuanshangfengyin.addItem(self.horizontalSpacer_4)

        self.setting_xuanshangfengyin_label = QLabel(self.horizontalLayoutWidget_2)
        self.setting_xuanshangfengyin_label.setObjectName(u"setting_xuanshangfengyin_label")

        self.horizontalLayout_setting_xuanshangfengyin.addWidget(self.setting_xuanshangfengyin_label)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_setting_xuanshangfengyin.addItem(self.horizontalSpacer_5)

        self.setting_xuanshangfengyin_comboBox = QComboBox(self.horizontalLayoutWidget_2)
        self.setting_xuanshangfengyin_comboBox.setObjectName(u"setting_xuanshangfengyin_comboBox")

        self.horizontalLayout_setting_xuanshangfengyin.addWidget(self.setting_xuanshangfengyin_comboBox)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_setting_xuanshangfengyin.addItem(self.horizontalSpacer_6)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.tabWidget.addTab(self.tab_setting, "")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox_basic.setTitle(QCoreApplication.translate("MainWindow", u"\u57fa\u672c\u529f\u80fd", None))
        self.button_enviroment.setText(QCoreApplication.translate("MainWindow", u"\u73af\u5883\u68c0\u6d4b", None))
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
        self.button_jiejietupo_9victory.setText(QCoreApplication.translate("MainWindow", u"9\u80dc", None))
        self.label_refresh_rule.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0\u89c4\u5219", None))
        self.button_guanzhan.setText(QCoreApplication.translate("MainWindow", u"\u89c2\u6218", None))
        self.groupBox_info.setTitle(QCoreApplication.translate("MainWindow", u"\u4fe1\u606f", None))
        self.text_num.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u5b8c\u6210\u60c5\u51b5", None))
        self.text_print.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8f93\u51fa\u4fe1\u606f", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:10pt;\">\u5b8c\u6210\u60c5\u51b5</span></p></body></html>", None))
        self.button_start.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_home), QCoreApplication.translate("MainWindow", u"\u9996\u9875", None))
        self.setting_update_label.setText(QCoreApplication.translate("MainWindow", u"\u66f4\u65b0\u65b9\u5f0f", None))
        self.setting_xuanshangfengyin_label.setText(QCoreApplication.translate("MainWindow", u"\u60ac\u8d4f\u5c01\u5370", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_setting), QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e", None))
    # retranslateUi

