from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CheckBox,
    ComboBox,
    FluentIcon,
    HeaderCardWidget,
    LineEdit,
    PushButton,
    RadioButton,
    SpinBox,
    TextBrowser,
)

from ..package.types import QiLing, Yingjie

GroupHeaderCardWidgetHeaderViewHeight: int = 36

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


class HomeWidget(QWidget):
    """主页"""

    class StatusButton(PushButton):
        """状态按钮"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self._status: bool = False
            self.setFixedSize(120, 50)
            font = self.font()
            font.setPointSize(16)
            self.setFont(font)

            self.stop()
            self.setEnabled(False)

        def start(self):
            self._status = True
            self.setIcon(FluentIcon.POWER_BUTTON)
            self.setText("停止")

        def stop(self):
            self._status = False
            self.setIcon(FluentIcon.PLAY)
            self.setText("开始")

        def is_start(self) -> bool:
            return self._status

    class StatusButtonWidget(QWidget):
        """状态按钮"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setFixedHeight(80)
            self.button = PushButton()
            self.button.setFixedSize(120, 50)
            font = self.button.font()
            font.setPointSize(16)
            self.button.setFont(font)
            self.stop()
            self.button.setEnabled(False)

            self.hBoxLayout = QHBoxLayout()
            self.hBoxLayout.addWidget(self.button)
            self.setLayout(self.hBoxLayout)

        def start(self):
            self.button.setIcon(FluentIcon.POWER_BUTTON)
            self.button.setText("停止")

        def stop(self):
            self.button.setIcon(FluentIcon.PLAY)
            self.button.setText("开始")

    class BasicFunctionCard(HeaderCardWidget):
        """基本功能"""

        def __init__(self, parent=None):
            super().__init__(parent)

            self.setTitle("基本功能")
            self.setBorderRadius(8)
            self.headerView.setFixedHeight(GroupHeaderCardWidgetHeaderViewHeight)

            self.func_label = BodyLabel("选择功能")
            self.func_label.setFixedWidth(60)

            self.func_combobox = ComboBox()
            self.func_combobox.addItems(_list_function)
            self.func_combobox.setCurrentIndex(-1)

            self.number_label = BodyLabel("选择次数")
            self.number_label.setFixedWidth(60)

            self.number_spinbox = SpinBox()
            self.number_spinbox.setRange(0, 100)
            self.number_spinbox.setValue(0)

            self.hBoxLayout1 = QHBoxLayout()
            self.hBoxLayout1.addWidget(self.func_label)
            self.hBoxLayout1.addWidget(self.func_combobox)

            self.hBoxLayout2 = QHBoxLayout()
            self.hBoxLayout2.addWidget(self.number_label)
            self.hBoxLayout2.addWidget(self.number_spinbox)

            self.vBoxLayout = QVBoxLayout()
            self.vBoxLayout.setSpacing(20)
            self.vBoxLayout.addLayout(self.hBoxLayout1)
            self.vBoxLayout.addLayout(self.hBoxLayout2)

            self.viewLayout.addLayout(self.vBoxLayout)

        def set_number_spinbox_value(self, current: int = 1, min: int = 0, max: int = 99):
            self.number_spinbox.setValue(current)
            self.number_spinbox.setMinimum(min)
            self.number_spinbox.setMaximum(max)

    class AdvanceStack(QStackedWidget):
        """高级设置"""

        class AdvancedYuHunCard(HeaderCardWidget):
            """高级设置-御魂副本"""

            def __init__(self, parent=None):
                super().__init__(parent)
                self.setTitle("高级设置")
                self.setBorderRadius(8)
                self.headerView.setFixedHeight(GroupHeaderCardWidgetHeaderViewHeight)

                self.mode_label = BodyLabel("模式")
                self.mode_team_button = RadioButton("组队")
                self.mode_single_button = RadioButton("单人")
                self.mode_group = QButtonGroup(self)
                self.mode_group.addButton(self.mode_team_button)
                self.mode_group.addButton(self.mode_single_button)
                self.mode_team_button.setChecked(True)

                self.hBoxLayout1 = QHBoxLayout()
                self.hBoxLayout1.setSpacing(10)
                self.hBoxLayout1.addWidget(self.mode_label)
                self.hBoxLayout1.addWidget(self.mode_team_button)
                self.hBoxLayout1.addWidget(self.mode_single_button)

                self.driver_label = BodyLabel("是否司机")
                self.driver_no_button = RadioButton("否")
                self.driver_yes_button = RadioButton("是")
                self.driver_group = QButtonGroup(self)
                self.driver_group.addButton(self.driver_no_button)
                self.driver_group.addButton(self.driver_yes_button)
                self.driver_no_button.setChecked(True)

                self.hBoxLayout2 = QHBoxLayout()
                self.hBoxLayout2.setSpacing(10)
                self.hBoxLayout2.addWidget(self.driver_label)
                self.hBoxLayout2.addWidget(self.driver_no_button)
                self.hBoxLayout2.addWidget(self.driver_yes_button)

                self.passengers_label = BodyLabel("组队人数")
                self.passengers_2_button = RadioButton("2")
                self.passengers_3_button = RadioButton("3")
                self.passengers_group = QButtonGroup(self)
                self.passengers_group.addButton(self.passengers_2_button)
                self.passengers_group.addButton(self.passengers_3_button)
                self.passengers_2_button.setChecked(True)

                self.hBoxLayout3 = QHBoxLayout()
                self.hBoxLayout3.setSpacing(10)
                self.hBoxLayout3.addWidget(self.passengers_label)
                self.hBoxLayout3.addWidget(self.passengers_2_button)
                self.hBoxLayout3.addWidget(self.passengers_3_button)

                self.vBoxLayout = QVBoxLayout()
                self.vBoxLayout.setSpacing(20)
                self.vBoxLayout.addLayout(self.hBoxLayout1)
                self.vBoxLayout.addLayout(self.hBoxLayout2)
                self.vBoxLayout.addLayout(self.hBoxLayout3)
                self.vBoxLayout.addStretch()

                self.viewLayout.addLayout(self.vBoxLayout)

        class AdvancedJieJieTuPoCard(HeaderCardWidget):
            """高级设置-结界突破"""

            def __init__(self, parent=None):
                super().__init__(parent)
                self.setTitle("高级设置")
                self.setBorderRadius(8)
                self.headerView.setFixedHeight(GroupHeaderCardWidgetHeaderViewHeight)

                self.mode_level = RadioButton("卡级")
                self.mode_refresh = RadioButton("3胜刷新")
                self.mode_group = QButtonGroup(self)
                self.mode_group.addButton(self.mode_level)
                self.mode_group.addButton(self.mode_refresh)
                self.mode_group.buttonToggled.connect(self._mode_group_buttontoggled_handle)

                self.fail_checkbox = CheckBox("首轮退级")

                self.current_level_label = BodyLabel("当前等级")
                self.current_combobox = ComboBox()
                self.current_combobox.addItems(["57", "58", "59", "60"])

                self.hBoxLayout1 = QHBoxLayout()
                self.hBoxLayout1.setSpacing(10)
                self.hBoxLayout1.addWidget(self.current_level_label)
                self.hBoxLayout1.addWidget(self.current_combobox)

                self.target_level_label = BodyLabel("目标等级")
                self.target_combobox = ComboBox()
                self.target_combobox.addItems(["57", "58", "59", "60"])

                self.hBoxLayout2 = QHBoxLayout()
                self.hBoxLayout2.setSpacing(10)
                self.hBoxLayout2.addWidget(self.target_level_label)
                self.hBoxLayout2.addWidget(self.target_combobox)

                self.vBoxLayout = QVBoxLayout()
                self.vBoxLayout.setSpacing(10)
                self.vBoxLayout.addWidget(self.mode_level)
                self.vBoxLayout.addWidget(self.fail_checkbox)
                self.vBoxLayout.addLayout(self.hBoxLayout1)
                self.vBoxLayout.addLayout(self.hBoxLayout2)
                self.vBoxLayout.addWidget(self.mode_refresh)
                self.vBoxLayout.addStretch()

                self.viewLayout.addLayout(self.vBoxLayout)

                self.mode_level.setChecked(True)

            def _mode_group_buttontoggled_handle(self, button: RadioButton, checked: bool):
                if checked:
                    if button.text() == self.mode_level.text():
                        self.fail_checkbox.setDisabled(False)
                        self.current_combobox.setDisabled(False)
                        self.target_combobox.setDisabled(False)
                    else:
                        self.fail_checkbox.setDisabled(True)
                        self.current_combobox.setDisabled(True)
                        self.target_combobox.setDisabled(True)

        class AdvancedDaoGuanTuPoCard(HeaderCardWidget):
            """高级设置-道馆突破"""

            def __init__(self, parent=None):
                super().__init__(parent)
                self.setTitle("高级设置")
                self.setBorderRadius(8)
                self.headerView.setFixedHeight(GroupHeaderCardWidgetHeaderViewHeight)

                self.checkbox = CheckBox("观战")

                self.vBoxLayout = QVBoxLayout()
                self.vBoxLayout.setSpacing(10)
                self.vBoxLayout.addWidget(self.checkbox)
                self.vBoxLayout.addStretch()

                self.viewLayout.addLayout(self.vBoxLayout)

        class AdvancedQiLingCard(HeaderCardWidget):
            """高级设置-契灵"""

            def __init__(self, parent=None):
                super().__init__(parent)
                self.setTitle("高级设置")
                self.setBorderRadius(8)
                self.headerView.setFixedHeight(GroupHeaderCardWidgetHeaderViewHeight)

                self.tancha_checkbox = CheckBox("探查次数")
                self.tancha_checkbox.toggled.connect(self._tancha_checkbox_toggled_handle)
                self.tancha_spinbox = SpinBox()
                self.tancha_spinbox.setDisabled(True)

                self.hBoxLayout1 = QHBoxLayout()
                self.hBoxLayout1.setSpacing(10)
                self.hBoxLayout1.addWidget(self.tancha_checkbox)
                self.hBoxLayout1.addWidget(self.tancha_spinbox)

                self.line = QFrame()
                self.line.setFrameShape(QFrame.Shape.HLine)
                self.line.setFrameShadow(QFrame.Shadow.Sunken)
                self.line.setFixedHeight(10)

                self.jieqi_checkbox = CheckBox("结契-鸣契石")
                self.jieqi_checkbox.toggled.connect(self._jieqi_checkbox_toggled_handle)

                self.hBoxLayout2 = QHBoxLayout()
                self.hBoxLayout2.setSpacing(10)
                self.hBoxLayout2.addWidget(self.jieqi_checkbox)

                self.jieqi_stone_combobox = ComboBox()
                self.jieqi_stone_combobox.addItems([item.value for item in QiLing])
                self.jieqi_stone_combobox.setDisabled(True)

                self.jieqi_stone_spinbox = SpinBox()
                self.jieqi_stone_spinbox.setDisabled(True)

                self.hBoxLayout3 = QHBoxLayout()
                self.hBoxLayout3.setSpacing(10)
                self.hBoxLayout3.addWidget(self.jieqi_stone_combobox)
                self.hBoxLayout3.addWidget(self.jieqi_stone_spinbox)

                self.vBoxLayout = QVBoxLayout()
                self.vBoxLayout.setSpacing(10)
                self.vBoxLayout.addLayout(self.hBoxLayout1)
                self.vBoxLayout.addWidget(self.line)
                self.vBoxLayout.addLayout(self.hBoxLayout2)
                self.vBoxLayout.addLayout(self.hBoxLayout3)
                self.vBoxLayout.addStretch()

                self.viewLayout.addLayout(self.vBoxLayout)

            def _tancha_checkbox_toggled_handle(self, checked: bool):
                self.tancha_spinbox.setDisabled(not checked)

            def _jieqi_checkbox_toggled_handle(self, checked: bool):
                self.jieqi_stone_combobox.setDisabled(not checked)
                self.jieqi_stone_spinbox.setDisabled(not checked)

        class AdvancedYingJieShiLianCard(HeaderCardWidget):
            """高级设置-英杰试炼"""

            def __init__(self, parent=None):
                super().__init__(parent)
                self.setTitle("高级设置")
                self.setBorderRadius(8)
                self.headerView.setFixedHeight(GroupHeaderCardWidgetHeaderViewHeight)

                self.combobox = ComboBox()
                self.combobox.addItems([item.value for item in Yingjie])

                self.exp_button = RadioButton("经验本")
                self.skill_button = RadioButton("技能本")
                self.skill_button.setChecked(True)
                self.button_group = QButtonGroup()
                self.button_group.addButton(self.exp_button)
                self.button_group.addButton(self.skill_button)

                self.vBoxLayout = QVBoxLayout()
                self.vBoxLayout.setSpacing(10)
                self.vBoxLayout.addWidget(self.combobox)
                self.vBoxLayout.addWidget(self.exp_button)
                self.vBoxLayout.addWidget(self.skill_button)
                self.vBoxLayout.addStretch()

                self.viewLayout.addLayout(self.vBoxLayout)

        class AdvancedHuiJuanCard(HeaderCardWidget):
            """高级设置-绘卷"""

            def __init__(self, parent=None):
                super().__init__(parent)
                self.setTitle("高级设置")
                self.setBorderRadius(8)
                self.headerView.setFixedHeight(GroupHeaderCardWidgetHeaderViewHeight)

                # self.tansuo_label = BodyLabel("探索总次数（打完BOSS算一次）")
                self.tansuo_label = BodyLabel("探索次数")
                self.tansuo_count_spinbox = SpinBox()
                # self.tansuo_hBoxLayout = QHBoxLayout()
                # # self.tansuo_hBoxLayout.setSpacing(10)
                # self.tansuo_hBoxLayout.addWidget(self.tansuo_label)
                # self.tansuo_hBoxLayout.addWidget(self.tansuo_count_spinbox)

                # self.tansuo_interval_label = BodyLabel("每隔多少次探索清理突破券")
                # self.tansuo_interval_spinbox = SpinBox()
                # self.tansuo_interval_spinbox.setValue(1)

                # self.tansuo_interval_hBoxLayout = QHBoxLayout()
                # self.tansuo_interval_hBoxLayout.setSpacing(10)
                # self.tansuo_interval_hBoxLayout.addWidget(self.tansuo_interval_label)
                # self.tansuo_interval_hBoxLayout.addWidget(self.tansuo_interval_spinbox)

                self.tansuo_hBoxLayout = QHBoxLayout()
                self.tansuo_hBoxLayout.setSpacing(10)
                self.tansuo_hBoxLayout.addWidget(self.tansuo_label)
                self.tansuo_hBoxLayout.addWidget(self.tansuo_count_spinbox)
                # self.tansuo_hBoxLayout.addWidget(self.tansuo_interval_label)
                # self.tansuo_hBoxLayout.addWidget(self.tansuo_interval_spinbox)

                self.line = QFrame()
                self.line.setFrameShape(QFrame.Shape.HLine)
                self.line.setFrameShadow(QFrame.Shadow.Sunken)
                self.line.setFixedHeight(10)

                self.mode_level = RadioButton("卡级")
                self.mode_refresh = RadioButton("3胜刷新")
                self.mode_group = QButtonGroup(self)
                self.mode_group.addButton(self.mode_level)
                self.mode_group.addButton(self.mode_refresh)
                self.mode_group.buttonToggled.connect(self._mode_group_buttontoggled_handle)

                self.fail_checkbox = CheckBox("首轮退级")

                self.current_level_label = BodyLabel("当前等级")
                self.current_combobox = ComboBox()
                self.current_combobox.addItems(["57", "58", "59", "60"])

                self.hBoxLayout1 = QHBoxLayout()
                self.hBoxLayout1.setSpacing(10)
                self.hBoxLayout1.addWidget(self.current_level_label)
                self.hBoxLayout1.addWidget(self.current_combobox)

                self.target_level_label = BodyLabel("目标等级")
                self.target_combobox = ComboBox()
                self.target_combobox.addItems(["57", "58", "59", "60"])

                self.hBoxLayout2 = QHBoxLayout()
                self.hBoxLayout2.setSpacing(10)
                self.hBoxLayout2.addWidget(self.target_level_label)
                self.hBoxLayout2.addWidget(self.target_combobox)

                self.tupo_groupbox_hBoxLayout1 = QHBoxLayout()
                self.tupo_groupbox_hBoxLayout1.setSpacing(10)
                self.tupo_groupbox_hBoxLayout1.addWidget(self.mode_level)
                self.tupo_groupbox_hBoxLayout1.addWidget(self.fail_checkbox)

                self.vBoxLayout = QVBoxLayout()
                # 不需要间隔
                self.vBoxLayout.addLayout(self.tansuo_hBoxLayout)
                self.vBoxLayout.addWidget(self.line)
                self.vBoxLayout.addLayout(self.tupo_groupbox_hBoxLayout1)
                self.vBoxLayout.addLayout(self.hBoxLayout1)
                self.vBoxLayout.addLayout(self.hBoxLayout2)
                self.vBoxLayout.addWidget(self.mode_refresh)

                self.viewLayout.addLayout(self.vBoxLayout)

                self.mode_level.setChecked(True)

            def _mode_group_buttontoggled_handle(self, button: RadioButton, checked: bool):
                if checked:
                    if button.text() == self.mode_level.text():
                        self.fail_checkbox.setDisabled(False)
                        self.current_combobox.setDisabled(False)
                        self.target_combobox.setDisabled(False)
                    else:
                        self.fail_checkbox.setDisabled(True)
                        self.current_combobox.setDisabled(True)
                        self.target_combobox.setDisabled(True)

        def __init__(self, parent=None):
            super().__init__(parent=parent)

            self.yuhun_card = self.AdvancedYuHunCard()
            self.jiejietupo_card = self.AdvancedJieJieTuPoCard()
            self.daoguantupo_card = self.AdvancedDaoGuanTuPoCard()
            self.qiling_card = self.AdvancedQiLingCard()
            self.yingjieshilian_card = self.AdvancedYingJieShiLianCard()
            self.huijuan_card = self.AdvancedHuiJuanCard()

            self.addWidget(QWidget())
            self.addWidget(self.yuhun_card)
            self.addWidget(self.jiejietupo_card)
            self.addWidget(self.daoguantupo_card)
            self.addWidget(self.qiling_card)
            self.addWidget(self.yingjieshilian_card)
            self.addWidget(self.huijuan_card)

            self.setCurrentIndex(0)

    class OutputInfoCard(HeaderCardWidget):
        """输出信息卡片"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setTitle("输出信息")
            self.setBorderRadius(8)
            self.headerView.setFixedHeight(GroupHeaderCardWidgetHeaderViewHeight)
            self.viewLayout.setContentsMargins(12, 8, 12, 12)

            self.progress_label = BodyLabel("当前进度")
            self.progress_text = LineEdit()
            self.progress_text.setMaximumHeight(20)
            self.progress_text.setReadOnly(True)

            self.text_info = TextBrowser()
            self.text_info.setReadOnly(True)

            self.vBoxLayout = QVBoxLayout()
            self.hBoxLayout = QHBoxLayout()
            self.hBoxLayout.setSpacing(10)

            self.hBoxLayout.addWidget(self.progress_label)
            self.hBoxLayout.addWidget(self.progress_text)

            self.vBoxLayout.addLayout(self.hBoxLayout)
            self.vBoxLayout.addWidget(self.text_info, 1)
            self.vBoxLayout.setSpacing(15)
            self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

            self.viewLayout.addLayout(self.vBoxLayout)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("Home")

        self.hBoxLayout = QHBoxLayout(self)

        # 左侧栏 - 基本设置和高级设置
        self.leftWidget = QWidget()
        self.leftWidget.setMaximumWidth(300)
        self.leftLayout = QVBoxLayout(self.leftWidget)
        self.leftLayout.setContentsMargins(0, 0, 0, 0)
        self.leftLayout.setSpacing(10)

        self.basic_group = self.BasicFunctionCard(self)
        self.leftLayout.addWidget(self.basic_group, 0, Qt.AlignmentFlag.AlignTop)

        self.advanced_stack = self.AdvanceStack(self)
        self.leftLayout.addWidget(self.advanced_stack, 0, Qt.AlignmentFlag.AlignTop)

        # 左侧栏底部 - 状态按钮
        self.button_status = self.StatusButton(self)
        # 使用QWidget包裹状态按钮，外部调用时只能改变button_status的属性
        button_status_widget = QWidget()
        button_status_widget.setFixedHeight(80)
        button_status_widget_vBoxLayout = QVBoxLayout(button_status_widget)
        button_status_widget_vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐
        button_status_widget_vBoxLayout.addWidget(self.button_status)
        self.leftLayout.addWidget(button_status_widget, 0, Qt.AlignmentFlag.AlignBottom)  # 底部顶格

        # 右侧栏 - 输出信息卡片
        self.rightWidget = QWidget()
        self.rightLayout = QVBoxLayout(self.rightWidget)
        self.rightLayout.setContentsMargins(0, 0, 0, 0)

        self.output_info_group = self.OutputInfoCard(self)

        self.rightLayout.addWidget(self.output_info_group, 1)

        self.hBoxLayout.addWidget(self.leftWidget, 4)
        self.hBoxLayout.addWidget(self.rightWidget, 6)
        self.hBoxLayout.setSpacing(20)
