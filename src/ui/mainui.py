# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainui.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QRadioButton,
    QScrollArea, QSizePolicy, QSpacerItem, QSpinBox,
    QStackedWidget, QTabWidget, QTextBrowser, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(550, 450)
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        MainWindow.setPalette(palette)
        font = QFont()
        font.setFamilies([u"\u5b8b\u4f53"])
        MainWindow.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_centralwidget = QGridLayout(self.centralwidget)
        self.gridLayout_centralwidget.setSpacing(0)
        self.gridLayout_centralwidget.setObjectName(u"gridLayout_centralwidget")
        self.gridLayout_centralwidget.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_home = QWidget()
        self.tab_home.setObjectName(u"tab_home")
        self.gridLayout_tab_home = QGridLayout(self.tab_home)
        self.gridLayout_tab_home.setObjectName(u"gridLayout_tab_home")
        self.gridLayout_tab_home.setContentsMargins(4, 11, 4, 4)
        self.groupBox_info = QGroupBox(self.tab_home)
        self.groupBox_info.setObjectName(u"groupBox_info")
        self.gridLayout_groupBox_info = QGridLayout(self.groupBox_info)
        self.gridLayout_groupBox_info.setObjectName(u"gridLayout_groupBox_info")
        self.horizontalSpacer_groupBox_info_right = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_groupBox_info.addItem(self.horizontalSpacer_groupBox_info_right, 0, 4, 1, 1)

        self.horizontalSpacer_groupBox_info_left = QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_groupBox_info.addItem(self.horizontalSpacer_groupBox_info_left, 0, 1, 1, 1)

        self.text_completion_times = QLineEdit(self.groupBox_info)
        self.text_completion_times.setObjectName(u"text_completion_times")
        self.text_completion_times.setEnabled(True)
        font1 = QFont()
        font1.setFamilies([u"\u5b8b\u4f53"])
        font1.setPointSize(9)
        self.text_completion_times.setFont(font1)
        self.text_completion_times.setMaxLength(32764)

        self.gridLayout_groupBox_info.addWidget(self.text_completion_times, 0, 3, 1, 1)

        self.text_info = QTextBrowser(self.groupBox_info)
        self.text_info.setObjectName(u"text_info")

        self.gridLayout_groupBox_info.addWidget(self.text_info, 1, 0, 1, 6)

        self.label_completion_times = QLabel(self.groupBox_info)
        self.label_completion_times.setObjectName(u"label_completion_times")
        self.label_completion_times.setFont(font)
        self.label_completion_times.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_completion_times.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_groupBox_info.addWidget(self.label_completion_times, 0, 2, 1, 1)


        self.gridLayout_tab_home.addWidget(self.groupBox_info, 0, 1, 13, 1)

        self.horizontalLayout_button_start = QHBoxLayout()
        self.horizontalLayout_button_start.setObjectName(u"horizontalLayout_button_start")
        self.button_start = QPushButton(self.tab_home)
        self.button_start.setObjectName(u"button_start")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_start.sizePolicy().hasHeightForWidth())
        self.button_start.setSizePolicy(sizePolicy)
        self.button_start.setMinimumSize(QSize(0, 30))
        font2 = QFont()
        font2.setFamilies([u"\u5b8b\u4f53"])
        font2.setPointSize(11)
        font2.setBold(True)
        self.button_start.setFont(font2)

        self.horizontalLayout_button_start.addWidget(self.button_start)


        self.gridLayout_tab_home.addLayout(self.horizontalLayout_button_start, 7, 0, 1, 1)

        self.verticalSpacer_button_start_up = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_tab_home.addItem(self.verticalSpacer_button_start_up, 3, 0, 1, 1)

        self.groupBox_advanced = QGroupBox(self.tab_home)
        self.groupBox_advanced.setObjectName(u"groupBox_advanced")
        self.gridLayout_advanced = QGridLayout(self.groupBox_advanced)
        self.gridLayout_advanced.setObjectName(u"gridLayout_advanced")
        self.stackedWidget = QStackedWidget(self.groupBox_advanced)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self._0_none = QWidget()
        self._0_none.setObjectName(u"_0_none")
        self.stackedWidget.addWidget(self._0_none)
        self._1_yuhun = QWidget()
        self._1_yuhun.setObjectName(u"_1_yuhun")
        self.label_driver = QLabel(self._1_yuhun)
        self.label_driver.setObjectName(u"label_driver")
        self.label_driver.setGeometry(QRect(20, 55, 48, 21))
        self.label_driver.setFont(font1)
        self.button_driver_False = QRadioButton(self._1_yuhun)
        self.buttonGroup_yuhun_driver = QButtonGroup(MainWindow)
        self.buttonGroup_yuhun_driver.setObjectName(u"buttonGroup_yuhun_driver")
        self.buttonGroup_yuhun_driver.addButton(self.button_driver_False)
        self.button_driver_False.setObjectName(u"button_driver_False")
        self.button_driver_False.setGeometry(QRect(78, 55, 38, 20))
        self.button_driver_False.setFont(font1)
        self.button_driver_False.setMouseTracking(True)
        self.button_driver_True = QRadioButton(self._1_yuhun)
        self.buttonGroup_yuhun_driver.addButton(self.button_driver_True)
        self.button_driver_True.setObjectName(u"button_driver_True")
        self.button_driver_True.setGeometry(QRect(128, 55, 38, 20))
        self.button_driver_True.setFont(font1)
        self.button_passengers_3 = QRadioButton(self._1_yuhun)
        self.buttonGroup_yuhun_passengers = QButtonGroup(MainWindow)
        self.buttonGroup_yuhun_passengers.setObjectName(u"buttonGroup_yuhun_passengers")
        self.buttonGroup_yuhun_passengers.addButton(self.button_passengers_3)
        self.button_passengers_3.setObjectName(u"button_passengers_3")
        self.button_passengers_3.setGeometry(QRect(128, 81, 33, 20))
        self.button_passengers_3.setFont(font1)
        self.button_passengers_2 = QRadioButton(self._1_yuhun)
        self.buttonGroup_yuhun_passengers.addButton(self.button_passengers_2)
        self.button_passengers_2.setObjectName(u"button_passengers_2")
        self.button_passengers_2.setGeometry(QRect(79, 81, 33, 20))
        self.button_passengers_2.setFont(font1)
        self.label_passengers = QLabel(self._1_yuhun)
        self.label_passengers.setObjectName(u"label_passengers")
        self.label_passengers.setGeometry(QRect(20, 81, 48, 21))
        self.label_passengers.setFont(font1)
        self.button_yuhun_drop_statistics = QCheckBox(self._1_yuhun)
        self.button_yuhun_drop_statistics.setObjectName(u"button_yuhun_drop_statistics")
        self.button_yuhun_drop_statistics.setGeometry(QRect(20, 109, 100, 20))
        sizePolicy.setHeightForWidth(self.button_yuhun_drop_statistics.sizePolicy().hasHeightForWidth())
        self.button_yuhun_drop_statistics.setSizePolicy(sizePolicy)
        self.button_yuhun_drop_statistics.setMinimumSize(QSize(100, 0))
        self.button_yuhun_drop_statistics.setMaximumSize(QSize(100, 16777215))
        self.button_mode_single = QRadioButton(self._1_yuhun)
        self.buttonGroup_yuhun_mode = QButtonGroup(MainWindow)
        self.buttonGroup_yuhun_mode.setObjectName(u"buttonGroup_yuhun_mode")
        self.buttonGroup_yuhun_mode.addButton(self.button_mode_single)
        self.button_mode_single.setObjectName(u"button_mode_single")
        self.button_mode_single.setGeometry(QRect(128, 28, 51, 20))
        self.button_mode_single.setFont(font1)
        self.button_mode_team = QRadioButton(self._1_yuhun)
        self.buttonGroup_yuhun_mode.addButton(self.button_mode_team)
        self.button_mode_team.setObjectName(u"button_mode_team")
        self.button_mode_team.setGeometry(QRect(78, 28, 51, 20))
        self.button_mode_team.setFont(font1)
        self.button_mode_team.setMouseTracking(True)
        self.label_mode = QLabel(self._1_yuhun)
        self.label_mode.setObjectName(u"label_mode")
        self.label_mode.setGeometry(QRect(20, 28, 48, 21))
        self.label_mode.setFont(font1)
        self.stackedWidget.addWidget(self._1_yuhun)
        self._2_jiejietupo = QWidget()
        self._2_jiejietupo.setObjectName(u"_2_jiejietupo")
        self.groupBox_jiejietupo_switch_level = QGroupBox(self._2_jiejietupo)
        self.groupBox_jiejietupo_switch_level.setObjectName(u"groupBox_jiejietupo_switch_level")
        self.groupBox_jiejietupo_switch_level.setGeometry(QRect(0, 5, 191, 80))
        self.button_jiejietupo_target_level_60 = QRadioButton(self.groupBox_jiejietupo_switch_level)
        self.buttonGroup_jiejietupo_target_level = QButtonGroup(MainWindow)
        self.buttonGroup_jiejietupo_target_level.setObjectName(u"buttonGroup_jiejietupo_target_level")
        self.buttonGroup_jiejietupo_target_level.addButton(self.button_jiejietupo_target_level_60)
        self.button_jiejietupo_target_level_60.setObjectName(u"button_jiejietupo_target_level_60")
        self.button_jiejietupo_target_level_60.setGeometry(QRect(153, 45, 35, 20))
        self.button_jiejietupo_target_level_59 = QRadioButton(self.groupBox_jiejietupo_switch_level)
        self.buttonGroup_jiejietupo_target_level.addButton(self.button_jiejietupo_target_level_59)
        self.button_jiejietupo_target_level_59.setObjectName(u"button_jiejietupo_target_level_59")
        self.button_jiejietupo_target_level_59.setGeometry(QRect(120, 45, 35, 20))
        self.button_jiejietupo_target_level_58 = QRadioButton(self.groupBox_jiejietupo_switch_level)
        self.buttonGroup_jiejietupo_target_level.addButton(self.button_jiejietupo_target_level_58)
        self.button_jiejietupo_target_level_58.setObjectName(u"button_jiejietupo_target_level_58")
        self.button_jiejietupo_target_level_58.setGeometry(QRect(87, 45, 35, 20))
        self.button_jiejietupo_target_level_57 = QRadioButton(self.groupBox_jiejietupo_switch_level)
        self.buttonGroup_jiejietupo_target_level.addButton(self.button_jiejietupo_target_level_57)
        self.button_jiejietupo_target_level_57.setObjectName(u"button_jiejietupo_target_level_57")
        self.button_jiejietupo_target_level_57.setGeometry(QRect(54, 45, 35, 20))
        self.label_jiejietupo_target_level = QLabel(self.groupBox_jiejietupo_switch_level)
        self.label_jiejietupo_target_level.setObjectName(u"label_jiejietupo_target_level")
        self.label_jiejietupo_target_level.setGeometry(QRect(5, 45, 48, 20))
        self.button_jiejietupo_current_level_60 = QRadioButton(self.groupBox_jiejietupo_switch_level)
        self.buttonGroup_jiejietupo_current_level = QButtonGroup(MainWindow)
        self.buttonGroup_jiejietupo_current_level.setObjectName(u"buttonGroup_jiejietupo_current_level")
        self.buttonGroup_jiejietupo_current_level.addButton(self.button_jiejietupo_current_level_60)
        self.button_jiejietupo_current_level_60.setObjectName(u"button_jiejietupo_current_level_60")
        self.button_jiejietupo_current_level_60.setGeometry(QRect(153, 20, 35, 20))
        self.button_jiejietupo_current_level_59 = QRadioButton(self.groupBox_jiejietupo_switch_level)
        self.buttonGroup_jiejietupo_current_level.addButton(self.button_jiejietupo_current_level_59)
        self.button_jiejietupo_current_level_59.setObjectName(u"button_jiejietupo_current_level_59")
        self.button_jiejietupo_current_level_59.setGeometry(QRect(120, 20, 35, 20))
        self.button_jiejietupo_current_level_58 = QRadioButton(self.groupBox_jiejietupo_switch_level)
        self.buttonGroup_jiejietupo_current_level.addButton(self.button_jiejietupo_current_level_58)
        self.button_jiejietupo_current_level_58.setObjectName(u"button_jiejietupo_current_level_58")
        self.button_jiejietupo_current_level_58.setGeometry(QRect(87, 20, 35, 20))
        self.button_jiejietupo_current_level_57 = QRadioButton(self.groupBox_jiejietupo_switch_level)
        self.buttonGroup_jiejietupo_current_level.addButton(self.button_jiejietupo_current_level_57)
        self.button_jiejietupo_current_level_57.setObjectName(u"button_jiejietupo_current_level_57")
        self.button_jiejietupo_current_level_57.setGeometry(QRect(54, 20, 35, 20))
        self.button_jiejietupo_current_level_57.setMouseTracking(True)
        self.label_jiejietupo_current_level = QLabel(self.groupBox_jiejietupo_switch_level)
        self.label_jiejietupo_current_level.setObjectName(u"label_jiejietupo_current_level")
        self.label_jiejietupo_current_level.setGeometry(QRect(5, 20, 48, 20))
        self.button_jiejietupo_switch_level = QRadioButton(self.groupBox_jiejietupo_switch_level)
        self.buttonGroup_jiejietupo_switch = QButtonGroup(MainWindow)
        self.buttonGroup_jiejietupo_switch.setObjectName(u"buttonGroup_jiejietupo_switch")
        self.buttonGroup_jiejietupo_switch.addButton(self.button_jiejietupo_switch_level)
        self.button_jiejietupo_switch_level.setObjectName(u"button_jiejietupo_switch_level")
        self.button_jiejietupo_switch_level.setGeometry(QRect(5, 5, 47, 16))
        self.groupBox_jiejietupo_switch_rule = QGroupBox(self._2_jiejietupo)
        self.groupBox_jiejietupo_switch_rule.setObjectName(u"groupBox_jiejietupo_switch_rule")
        self.groupBox_jiejietupo_switch_rule.setGeometry(QRect(0, 95, 191, 51))
        self.button_jiejietupo_refresh_rule_3 = QRadioButton(self.groupBox_jiejietupo_switch_rule)
        self.buttonGroup_jiejietupo_refresh_rule = QButtonGroup(MainWindow)
        self.buttonGroup_jiejietupo_refresh_rule.setObjectName(u"buttonGroup_jiejietupo_refresh_rule")
        self.buttonGroup_jiejietupo_refresh_rule.addButton(self.button_jiejietupo_refresh_rule_3)
        self.button_jiejietupo_refresh_rule_3.setObjectName(u"button_jiejietupo_refresh_rule_3")
        self.button_jiejietupo_refresh_rule_3.setGeometry(QRect(20, 20, 40, 20))
        self.button_jiejietupo_refresh_rule_6 = QRadioButton(self.groupBox_jiejietupo_switch_rule)
        self.buttonGroup_jiejietupo_refresh_rule.addButton(self.button_jiejietupo_refresh_rule_6)
        self.button_jiejietupo_refresh_rule_6.setObjectName(u"button_jiejietupo_refresh_rule_6")
        self.button_jiejietupo_refresh_rule_6.setGeometry(QRect(70, 20, 40, 20))
        self.button_jiejietupo_refresh_rule_9 = QRadioButton(self.groupBox_jiejietupo_switch_rule)
        self.buttonGroup_jiejietupo_refresh_rule.addButton(self.button_jiejietupo_refresh_rule_9)
        self.button_jiejietupo_refresh_rule_9.setObjectName(u"button_jiejietupo_refresh_rule_9")
        self.button_jiejietupo_refresh_rule_9.setGeometry(QRect(120, 20, 40, 20))
        self.button_jiejietupo_switch_rule = QRadioButton(self.groupBox_jiejietupo_switch_rule)
        self.buttonGroup_jiejietupo_switch.addButton(self.button_jiejietupo_switch_rule)
        self.button_jiejietupo_switch_rule.setObjectName(u"button_jiejietupo_switch_rule")
        self.button_jiejietupo_switch_rule.setGeometry(QRect(5, 5, 71, 16))
        self.stackedWidget.addWidget(self._2_jiejietupo)
        self._3_daoguantupo = QWidget()
        self._3_daoguantupo.setObjectName(u"_3_daoguantupo")
        self.button_guanzhan = QCheckBox(self._3_daoguantupo)
        self.button_guanzhan.setObjectName(u"button_guanzhan")
        self.button_guanzhan.setGeometry(QRect(60, 40, 51, 20))
        self.stackedWidget.addWidget(self._3_daoguantupo)
        self._4_qiling = QWidget()
        self._4_qiling.setObjectName(u"_4_qiling")
        self.button_qiling_tancha = QCheckBox(self._4_qiling)
        self.button_qiling_tancha.setObjectName(u"button_qiling_tancha")
        self.button_qiling_tancha.setGeometry(QRect(10, 20, 51, 20))
        self.button_qiling_jieqi = QCheckBox(self._4_qiling)
        self.button_qiling_jieqi.setObjectName(u"button_qiling_jieqi")
        self.button_qiling_jieqi.setGeometry(QRect(10, 50, 51, 20))
        self.label_qiling_jieqi_stone = QLabel(self._4_qiling)
        self.label_qiling_jieqi_stone.setObjectName(u"label_qiling_jieqi_stone")
        self.label_qiling_jieqi_stone.setGeometry(QRect(10, 90, 41, 20))
        self.label_qiling_jieqi_stone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.combo_qiling_jieqi_stone = QComboBox(self._4_qiling)
        self.combo_qiling_jieqi_stone.setObjectName(u"combo_qiling_jieqi_stone")
        self.combo_qiling_jieqi_stone.setGeometry(QRect(55, 90, 70, 20))
        self.spin_qiling_jieqi_stone = QSpinBox(self._4_qiling)
        self.spin_qiling_jieqi_stone.setObjectName(u"spin_qiling_jieqi_stone")
        self.spin_qiling_jieqi_stone.setGeometry(QRect(130, 90, 88, 20))
        font3 = QFont()
        font3.setFamilies([u"\u5b8b\u4f53"])
        font3.setPointSize(10)
        self.spin_qiling_jieqi_stone.setFont(font3)
        self.spin_qiling_jieqi_stone.setMaximum(30)
        self.stackedWidget.addWidget(self._4_qiling)

        self.gridLayout_advanced.addWidget(self.stackedWidget, 0, 0, 1, 1)


        self.gridLayout_tab_home.addWidget(self.groupBox_advanced, 1, 0, 1, 1)

        self.groupBox_basic = QGroupBox(self.tab_home)
        self.groupBox_basic.setObjectName(u"groupBox_basic")
        self.gridLayout_groupBox_basic = QGridLayout(self.groupBox_basic)
        self.gridLayout_groupBox_basic.setObjectName(u"gridLayout_groupBox_basic")
        self.gridLayout_groupBox_basic.setContentsMargins(20, -1, 22, -1)
        self.horizontalLayout_groupBox_basic_1 = QHBoxLayout()
        self.horizontalLayout_groupBox_basic_1.setObjectName(u"horizontalLayout_groupBox_basic_1")
        self.label_function = QLabel(self.groupBox_basic)
        self.label_function.setObjectName(u"label_function")
        self.label_function.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_groupBox_basic_1.addWidget(self.label_function)

        self.combo_choice = QComboBox(self.groupBox_basic)
        self.combo_choice.setObjectName(u"combo_choice")

        self.horizontalLayout_groupBox_basic_1.addWidget(self.combo_choice)

        self.horizontalLayout_groupBox_basic_1.setStretch(0, 1)
        self.horizontalLayout_groupBox_basic_1.setStretch(1, 3)

        self.gridLayout_groupBox_basic.addLayout(self.horizontalLayout_groupBox_basic_1, 1, 0, 1, 1)

        self.horizontalLayout_groupBox_basic_2 = QHBoxLayout()
        self.horizontalLayout_groupBox_basic_2.setObjectName(u"horizontalLayout_groupBox_basic_2")
        self.label_numbers = QLabel(self.groupBox_basic)
        self.label_numbers.setObjectName(u"label_numbers")
        self.label_numbers.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_groupBox_basic_2.addWidget(self.label_numbers)

        self.spin_times = QSpinBox(self.groupBox_basic)
        self.spin_times.setObjectName(u"spin_times")
        self.spin_times.setMinimumSize(QSize(60, 0))
        self.spin_times.setFont(font3)
        self.spin_times.setMaximum(999)

        self.horizontalLayout_groupBox_basic_2.addWidget(self.spin_times)

        self.horizontalSpacer_groupBox_basic = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_groupBox_basic_2.addItem(self.horizontalSpacer_groupBox_basic)

        self.horizontalLayout_groupBox_basic_2.setStretch(0, 2)
        self.horizontalLayout_groupBox_basic_2.setStretch(1, 5)
        self.horizontalLayout_groupBox_basic_2.setStretch(2, 1)

        self.gridLayout_groupBox_basic.addLayout(self.horizontalLayout_groupBox_basic_2, 3, 0, 1, 1)

        self.horizontalLayout_groupBox_basic_3 = QHBoxLayout()
        self.horizontalLayout_groupBox_basic_3.setObjectName(u"horizontalLayout_groupBox_basic_3")
        self.button_game_handle = QPushButton(self.groupBox_basic)
        self.button_game_handle.setObjectName(u"button_game_handle")
        sizePolicy.setHeightForWidth(self.button_game_handle.sizePolicy().hasHeightForWidth())
        self.button_game_handle.setSizePolicy(sizePolicy)
        self.button_game_handle.setFont(font3)

        self.horizontalLayout_groupBox_basic_3.addWidget(self.button_game_handle)


        self.gridLayout_groupBox_basic.addLayout(self.horizontalLayout_groupBox_basic_3, 4, 0, 1, 1)

        self.gridLayout_groupBox_basic.setColumnStretch(0, 1)

        self.gridLayout_tab_home.addWidget(self.groupBox_basic, 0, 0, 1, 1)

        self.verticalSpacer_button_start_down = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_tab_home.addItem(self.verticalSpacer_button_start_down, 11, 0, 1, 1)

        self.gridLayout_tab_home.setRowStretch(0, 2)
        self.gridLayout_tab_home.setRowStretch(1, 3)
        self.gridLayout_tab_home.setColumnStretch(0, 2)
        self.gridLayout_tab_home.setColumnStretch(1, 3)
        self.tabWidget.addTab(self.tab_home, "")
        self.tab_setting = QWidget()
        self.tab_setting.setObjectName(u"tab_setting")
        self.gridLayout_6 = QGridLayout(self.tab_setting)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.tab_setting)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 542, 423))
        self.verticalLayout_setting = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_setting.setObjectName(u"verticalLayout_setting")
        self.label_tip_setting_restart = QLabel(self.scrollAreaWidgetContents)
        self.label_tip_setting_restart.setObjectName(u"label_tip_setting_restart")
        self.label_tip_setting_restart.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_setting.addWidget(self.label_tip_setting_restart)

        self.groupBox_config = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_config.setObjectName(u"groupBox_config")
        self.vboxLayout = QVBoxLayout(self.groupBox_config)
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.horizontalLayout_setting_update = QHBoxLayout()
        self.horizontalLayout_setting_update.setObjectName(u"horizontalLayout_setting_update")
        self.horizontalSpacer_setting_update_left = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_update.addItem(self.horizontalSpacer_setting_update_left)

        self.setting_update_label = QLabel(self.groupBox_config)
        self.setting_update_label.setObjectName(u"setting_update_label")
        self.setting_update_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_setting_update.addWidget(self.setting_update_label)

        self.horizontalSpacer_setting_update_middle = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_update.addItem(self.horizontalSpacer_setting_update_middle)

        self.setting_update_comboBox = QComboBox(self.groupBox_config)
        self.setting_update_comboBox.setObjectName(u"setting_update_comboBox")
        self.setting_update_comboBox.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_setting_update.addWidget(self.setting_update_comboBox)

        self.horizontalSpacer_setting_update_right = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_update.addItem(self.horizontalSpacer_setting_update_right)

        self.horizontalLayout_setting_update.setStretch(0, 4)
        self.horizontalLayout_setting_update.setStretch(1, 2)
        self.horizontalLayout_setting_update.setStretch(3, 2)
        self.horizontalLayout_setting_update.setStretch(4, 4)

        self.vboxLayout.addLayout(self.horizontalLayout_setting_update)

        self.horizontalLayout_setting_update_download = QHBoxLayout()
        self.horizontalLayout_setting_update_download.setObjectName(u"horizontalLayout_setting_update_download")
        self.horizontalSpacer_setting_update_download_left = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_update_download.addItem(self.horizontalSpacer_setting_update_download_left)

        self.setting_update_download_label = QLabel(self.groupBox_config)
        self.setting_update_download_label.setObjectName(u"setting_update_download_label")
        self.setting_update_download_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_setting_update_download.addWidget(self.setting_update_download_label)

        self.horizontalSpacer_setting_update_download_middle = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_update_download.addItem(self.horizontalSpacer_setting_update_download_middle)

        self.setting_update_download_comboBox = QComboBox(self.groupBox_config)
        self.setting_update_download_comboBox.setObjectName(u"setting_update_download_comboBox")
        self.setting_update_download_comboBox.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_setting_update_download.addWidget(self.setting_update_download_comboBox)

        self.horizontalSpacer_setting_update_download_right = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_update_download.addItem(self.horizontalSpacer_setting_update_download_right)

        self.horizontalLayout_setting_update_download.setStretch(0, 4)
        self.horizontalLayout_setting_update_download.setStretch(1, 2)
        self.horizontalLayout_setting_update_download.setStretch(3, 2)
        self.horizontalLayout_setting_update_download.setStretch(4, 4)

        self.vboxLayout.addLayout(self.horizontalLayout_setting_update_download)

        self.horizontalLayout_setting_xuanshangfengyin = QHBoxLayout()
        self.horizontalLayout_setting_xuanshangfengyin.setObjectName(u"horizontalLayout_setting_xuanshangfengyin")
        self.horizontalSpacer_setting_xuanshangfengyin_left = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_xuanshangfengyin.addItem(self.horizontalSpacer_setting_xuanshangfengyin_left)

        self.setting_xuanshangfengyin_label = QLabel(self.groupBox_config)
        self.setting_xuanshangfengyin_label.setObjectName(u"setting_xuanshangfengyin_label")
        self.setting_xuanshangfengyin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_setting_xuanshangfengyin.addWidget(self.setting_xuanshangfengyin_label)

        self.horizontalSpacer_setting_xuanshangfengyin_middle = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_xuanshangfengyin.addItem(self.horizontalSpacer_setting_xuanshangfengyin_middle)

        self.setting_xuanshangfengyin_comboBox = QComboBox(self.groupBox_config)
        self.setting_xuanshangfengyin_comboBox.setObjectName(u"setting_xuanshangfengyin_comboBox")
        self.setting_xuanshangfengyin_comboBox.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_setting_xuanshangfengyin.addWidget(self.setting_xuanshangfengyin_comboBox)

        self.horizontalSpacer_setting_xuanshangfengyin_right = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_xuanshangfengyin.addItem(self.horizontalSpacer_setting_xuanshangfengyin_right)

        self.horizontalLayout_setting_xuanshangfengyin.setStretch(0, 4)
        self.horizontalLayout_setting_xuanshangfengyin.setStretch(1, 2)
        self.horizontalLayout_setting_xuanshangfengyin.setStretch(3, 2)
        self.horizontalLayout_setting_xuanshangfengyin.setStretch(4, 4)

        self.vboxLayout.addLayout(self.horizontalLayout_setting_xuanshangfengyin)

        self.horizontalLayout_setting_window_style = QHBoxLayout()
        self.horizontalLayout_setting_window_style.setObjectName(u"horizontalLayout_setting_window_style")
        self.horizontalSpacer_setting_window_style = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_window_style.addItem(self.horizontalSpacer_setting_window_style)

        self.setting_window_style_label = QLabel(self.groupBox_config)
        self.setting_window_style_label.setObjectName(u"setting_window_style_label")
        self.setting_window_style_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_setting_window_style.addWidget(self.setting_window_style_label)

        self.horizontalSpacer_setting_window_style_middle = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_window_style.addItem(self.horizontalSpacer_setting_window_style_middle)

        self.setting_window_style_comboBox = QComboBox(self.groupBox_config)
        self.setting_window_style_comboBox.setObjectName(u"setting_window_style_comboBox")
        self.setting_window_style_comboBox.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_setting_window_style.addWidget(self.setting_window_style_comboBox)

        self.horizontalSpacer_setting_window_style_right = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_window_style.addItem(self.horizontalSpacer_setting_window_style_right)

        self.horizontalLayout_setting_window_style.setStretch(0, 4)
        self.horizontalLayout_setting_window_style.setStretch(1, 2)
        self.horizontalLayout_setting_window_style.setStretch(3, 2)
        self.horizontalLayout_setting_window_style.setStretch(4, 4)

        self.vboxLayout.addLayout(self.horizontalLayout_setting_window_style)

        self.horizontalLayout_setting_shortcut_start_stop = QHBoxLayout()
        self.horizontalLayout_setting_shortcut_start_stop.setObjectName(u"horizontalLayout_setting_shortcut_start_stop")
        self.horizontalSpacer_setting_shortcut_start_stop_left = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_shortcut_start_stop.addItem(self.horizontalSpacer_setting_shortcut_start_stop_left)

        self.setting_shortcut_start_stop_label = QLabel(self.groupBox_config)
        self.setting_shortcut_start_stop_label.setObjectName(u"setting_shortcut_start_stop_label")
        self.setting_shortcut_start_stop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_setting_shortcut_start_stop.addWidget(self.setting_shortcut_start_stop_label)

        self.horizontalSpacer_setting_shortcut_start_stop_middle = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_shortcut_start_stop.addItem(self.horizontalSpacer_setting_shortcut_start_stop_middle)

        self.setting_shortcut_start_stop_comboBox = QComboBox(self.groupBox_config)
        self.setting_shortcut_start_stop_comboBox.setObjectName(u"setting_shortcut_start_stop_comboBox")
        self.setting_shortcut_start_stop_comboBox.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_setting_shortcut_start_stop.addWidget(self.setting_shortcut_start_stop_comboBox)

        self.horizontalSpacer_setting_shortcut_start_stop_right = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_setting_shortcut_start_stop.addItem(self.horizontalSpacer_setting_shortcut_start_stop_right)

        self.horizontalLayout_setting_shortcut_start_stop.setStretch(0, 4)
        self.horizontalLayout_setting_shortcut_start_stop.setStretch(1, 2)
        self.horizontalLayout_setting_shortcut_start_stop.setStretch(3, 2)
        self.horizontalLayout_setting_shortcut_start_stop.setStretch(4, 4)

        self.vboxLayout.addLayout(self.horizontalLayout_setting_shortcut_start_stop)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_setting_remember_last_choice_left = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_setting_remember_last_choice_left)

        self.setting_remember_last_choice_button = QCheckBox(self.groupBox_config)
        self.setting_remember_last_choice_button.setObjectName(u"setting_remember_last_choice_button")

        self.horizontalLayout.addWidget(self.setting_remember_last_choice_button)

        self.horizontalSpacer_setting_remember_last_choice_right = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_setting_remember_last_choice_right)


        self.vboxLayout.addLayout(self.horizontalLayout)


        self.verticalLayout_setting.addWidget(self.groupBox_config)

        self.horizontalLayout_restart_update_record = QHBoxLayout()
        self.horizontalLayout_restart_update_record.setObjectName(u"horizontalLayout_restart_update_record")
        self.horizontalSpacer_other_1 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_restart_update_record.addItem(self.horizontalSpacer_other_1)

        self.pushButton_homepage = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_homepage.setObjectName(u"pushButton_homepage")

        self.horizontalLayout_restart_update_record.addWidget(self.pushButton_homepage)

        self.horizontalSpacer_other_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_restart_update_record.addItem(self.horizontalSpacer_other_2)

        self.pushButton_helpdoc = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_helpdoc.setObjectName(u"pushButton_helpdoc")

        self.horizontalLayout_restart_update_record.addWidget(self.pushButton_helpdoc)

        self.horizontalSpacer_other_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_restart_update_record.addItem(self.horizontalSpacer_other_3)

        self.button_restart = QPushButton(self.scrollAreaWidgetContents)
        self.button_restart.setObjectName(u"button_restart")

        self.horizontalLayout_restart_update_record.addWidget(self.button_restart)

        self.horizontalSpacer_other_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_restart_update_record.addItem(self.horizontalSpacer_other_4)

        self.button_update_record = QPushButton(self.scrollAreaWidgetContents)
        self.button_update_record.setObjectName(u"button_update_record")

        self.horizontalLayout_restart_update_record.addWidget(self.button_update_record)

        self.horizontalSpacer_other_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_restart_update_record.addItem(self.horizontalSpacer_other_5)

        self.horizontalLayout_restart_update_record.setStretch(2, 1)
        self.horizontalLayout_restart_update_record.setStretch(5, 1)
        self.horizontalLayout_restart_update_record.setStretch(6, 1)
        self.horizontalLayout_restart_update_record.setStretch(7, 1)
        self.horizontalLayout_restart_update_record.setStretch(8, 1)

        self.verticalLayout_setting.addLayout(self.horizontalLayout_restart_update_record)

        self.verticalLayout_setting.setStretch(1, 4)
        self.verticalLayout_setting.setStretch(2, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_6.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_setting, "")

        self.gridLayout_centralwidget.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox_info.setTitle(QCoreApplication.translate("MainWindow", u"\u4fe1\u606f", None))
        self.text_completion_times.setPlaceholderText("")
        self.label_completion_times.setText(QCoreApplication.translate("MainWindow", u"\u5b8c\u6210\u6b21\u6570", None))
        self.button_start.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb", None))
        self.groupBox_advanced.setTitle(QCoreApplication.translate("MainWindow", u"\u9ad8\u7ea7\u8bbe\u7f6e", None))
        self.label_driver.setText(QCoreApplication.translate("MainWindow", u"\u662f\u5426\u53f8\u673a", None))
        self.button_driver_False.setText(QCoreApplication.translate("MainWindow", u"\u5426", None))
        self.button_driver_True.setText(QCoreApplication.translate("MainWindow", u"\u662f", None))
        self.button_passengers_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.button_passengers_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.label_passengers.setText(QCoreApplication.translate("MainWindow", u"\u7ec4\u961f\u4eba\u6570", None))
        self.button_yuhun_drop_statistics.setText(QCoreApplication.translate("MainWindow", u"\u6389\u843d\u7edf\u8ba1beta", None))
        self.button_mode_single.setText(QCoreApplication.translate("MainWindow", u"\u5355\u4eba", None))
        self.button_mode_team.setText(QCoreApplication.translate("MainWindow", u"\u7ec4\u961f", None))
        self.label_mode.setText(QCoreApplication.translate("MainWindow", u"\u6a21\u5f0f", None))
        self.button_jiejietupo_target_level_60.setText(QCoreApplication.translate("MainWindow", u"60", None))
        self.button_jiejietupo_target_level_59.setText(QCoreApplication.translate("MainWindow", u"59", None))
        self.button_jiejietupo_target_level_58.setText(QCoreApplication.translate("MainWindow", u"58", None))
        self.button_jiejietupo_target_level_57.setText(QCoreApplication.translate("MainWindow", u"57", None))
        self.label_jiejietupo_target_level.setText(QCoreApplication.translate("MainWindow", u"\u76ee\u6807\u7b49\u7ea7", None))
        self.button_jiejietupo_current_level_60.setText(QCoreApplication.translate("MainWindow", u"60", None))
        self.button_jiejietupo_current_level_59.setText(QCoreApplication.translate("MainWindow", u"59", None))
        self.button_jiejietupo_current_level_58.setText(QCoreApplication.translate("MainWindow", u"58", None))
        self.button_jiejietupo_current_level_57.setText(QCoreApplication.translate("MainWindow", u"57", None))
        self.label_jiejietupo_current_level.setText(QCoreApplication.translate("MainWindow", u"\u5f53\u524d\u7b49\u7ea7", None))
        self.button_jiejietupo_switch_level.setText(QCoreApplication.translate("MainWindow", u"\u5361\u7ea7", None))
        self.button_jiejietupo_refresh_rule_3.setText(QCoreApplication.translate("MainWindow", u"3\u80dc", None))
        self.button_jiejietupo_refresh_rule_6.setText(QCoreApplication.translate("MainWindow", u"6\u80dc", None))
        self.button_jiejietupo_refresh_rule_9.setText(QCoreApplication.translate("MainWindow", u"9\u80dc", None))
        self.button_jiejietupo_switch_rule.setText(QCoreApplication.translate("MainWindow", u"\u5237\u65b0\u89c4\u5219", None))
        self.button_guanzhan.setText(QCoreApplication.translate("MainWindow", u"\u89c2\u6218", None))
        self.button_qiling_tancha.setText(QCoreApplication.translate("MainWindow", u"\u63a2\u67e5", None))
        self.button_qiling_jieqi.setText(QCoreApplication.translate("MainWindow", u"\u7ed3\u5951", None))
        self.label_qiling_jieqi_stone.setText(QCoreApplication.translate("MainWindow", u"\u9e23\u5951\u77f3", None))
        self.groupBox_basic.setTitle(QCoreApplication.translate("MainWindow", u"\u57fa\u672c\u529f\u80fd", None))
        self.label_function.setText(QCoreApplication.translate("MainWindow", u"\u529f\u80fd", None))
        self.combo_choice.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u8bf7\u9009\u62e9\u529f\u80fd", None))
        self.label_numbers.setText(QCoreApplication.translate("MainWindow", u"\u6b21\u6570", None))
        self.button_game_handle.setText(QCoreApplication.translate("MainWindow", u"\u6e38\u620f\u68c0\u6d4b", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_home), QCoreApplication.translate("MainWindow", u"\u9996\u9875", None))
        self.label_tip_setting_restart.setText(QCoreApplication.translate("MainWindow", u"\u90e8\u5206\u8bbe\u7f6e\u9700\u8981\u91cd\u542f\u751f\u6548", None))
        self.groupBox_config.setTitle(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e", None))
        self.setting_update_label.setText(QCoreApplication.translate("MainWindow", u"\u66f4\u65b0\u6a21\u5f0f", None))
        self.setting_update_download_label.setText(QCoreApplication.translate("MainWindow", u"\u4e0b\u8f7d\u7ebf\u8def", None))
        self.setting_xuanshangfengyin_label.setText(QCoreApplication.translate("MainWindow", u"\u60ac\u8d4f\u5c01\u5370", None))
        self.setting_window_style_label.setText(QCoreApplication.translate("MainWindow", u"\u754c\u9762\u98ce\u683c", None))
        self.setting_shortcut_start_stop_label.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb/\u505c\u6b62\u70ed\u952e", None))
        self.setting_remember_last_choice_button.setText(QCoreApplication.translate("MainWindow", u"\u8bb0\u5fc6\u4e0a\u6b21\u6240\u9009\u529f\u80fd", None))
        self.pushButton_homepage.setText(QCoreApplication.translate("MainWindow", u"\u9879\u76ee\u4e3b\u9875", None))
        self.pushButton_helpdoc.setText(QCoreApplication.translate("MainWindow", u"\u4f7f\u7528\u6587\u6863", None))
        self.button_restart.setText(QCoreApplication.translate("MainWindow", u"\u91cd\u542f", None))
        self.button_update_record.setText(QCoreApplication.translate("MainWindow", u"\u66f4\u65b0\u8bb0\u5f55", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_setting), QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e", None))
    # retranslateUi

