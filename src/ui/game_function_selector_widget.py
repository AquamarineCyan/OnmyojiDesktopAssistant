from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import CardWidget, CheckBox, PushButton

from ..package.types import GameFunction
from ..utils.application import ICO_RESOURCE_PATH
from ..utils.config import config


class GameFunctionSelectorWidget(QWidget):
    """游戏功能选择器窗口"""

    applied = Signal()
    """点击应用后发射，通知外部刷新"""

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(ICO_RESOURCE_PATH))
        self.setWindowTitle("功能排序与选择")
        self.resize(400, 500)
        self.setObjectName("GameFunctionSelector")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 10, 10)
        self.main_layout.setSpacing(10)

        self.function_list_card = FunctionListCard()

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)
        self.reset_button = PushButton("恢复默认")
        self.reset_button.clicked.connect(self._on_reset_clicked)
        self.apply_button = PushButton("应用修改")
        self.apply_button.clicked.connect(self._on_apply_clicked)

        self.button_layout.addWidget(self.reset_button)
        self.button_layout.addWidget(self.apply_button)

        self.main_layout.addWidget(self.function_list_card)
        self.main_layout.addLayout(self.button_layout)

    def _on_apply_clicked(self):
        """处理应用按钮点击，仅保存选中的功能名与顺序到配置"""
        selected_functions = self.function_list_card.get_selected_functions()
        function_order = [func.name for func, checked in selected_functions if checked]

        # 更新配置
        config.update("function_order", function_order)

        # 通知外部刷新
        self.applied.emit()

    def _on_reset_clicked(self):
        """处理恢复默认按钮点击，清空配置并重置列表"""
        # 清空配置
        config.update("function_order", [func.name for func in GameFunction])

        # 重置列表为默认顺序（全部勾选）
        self.function_list_card.reset_to_default()

        # 通知外部刷新
        self.applied.emit()


class FunctionListCard(CardWidget):
    """功能选择列表卡片"""

    checkbox_toggled = Signal(GameFunction, bool)
    all_toggled = Signal(bool)
    order_changed = Signal(list)

    def __init__(self):
        super().__init__()

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.vBoxLayout.setSpacing(10)

        self.list_widget = QListWidget()
        self.list_widget.setFixedHeight(400)

        self._function_items = []
        self._create_function_list()

        self.vBoxLayout.addWidget(self.list_widget)

    def _create_item_widget(self, func: GameFunction, checked: bool, index: int, total: int):
        """创建单个功能列表项的控件

        Args:
            func: 游戏功能枚举
            checked: 是否勾选
            index: 当前序号
            total: 总项数

        Returns:
            (widget, checkbox, up_btn, down_btn)
        """

        widget = QWidget()
        h_layout = QHBoxLayout(widget)
        h_layout.setContentsMargins(5, 0, 0, 0)
        h_layout.setSpacing(8)

        checkbox = CheckBox(func.value)
        checkbox.setChecked(checked)
        checkbox.toggled.connect(lambda checked, f=func: self._on_checkbox_toggled(f, checked))
        checkbox.setFixedHeight(24)

        up_btn = QPushButton("↑")
        up_btn.setFixedSize(24, 24)
        up_btn.clicked.connect(lambda checked, f=func: self._on_move_up(f))
        up_btn.setEnabled(index > 0)

        down_btn = QPushButton("↓")
        down_btn.setFixedSize(24, 24)
        down_btn.clicked.connect(lambda checked, f=func: self._on_move_down(f))
        down_btn.setEnabled(index < total - 1)

        h_layout.addWidget(checkbox)
        h_layout.addStretch(1)
        h_layout.addWidget(up_btn)
        h_layout.addWidget(down_btn)

        return widget, checkbox, up_btn, down_btn

    def _create_function_list(self):
        """创建功能列表项"""
        saved_order = config.user.function_order
        saved_set = set(saved_order)
        # 已保存的功能按原顺序在前，未保存的按 GameFunction 定义顺序在后
        ordered_names = list(saved_order) + [func.name for func in GameFunction if func.name not in saved_set]
        func_list = [func for func in GameFunction if func.name in ordered_names]
        func_list.sort(key=lambda f: ordered_names.index(f.name))

        for i, func in enumerate(func_list):
            widget, checkbox, up_btn, down_btn = self._create_item_widget(
                func, not saved_order or func.name in saved_set, i, len(func_list)
            )
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            self._function_items.append((func, checkbox, up_btn, down_btn))

    def _on_checkbox_toggled(self, func: GameFunction, checked: bool):
        """
        处理复选框状态变化，发射信号

        Args:
            func: 游戏功能枚举
            checked: 是否选中
        """
        self.checkbox_toggled.emit(func, checked)

    def _on_move_up(self, func: GameFunction):
        """
        向上移动功能项

        Args:
            func: 要移动的游戏功能枚举
        """
        index = next((i for i, (f, _, _, _) in enumerate(self._function_items) if f == func), -1)
        if index > 0:
            self._function_items[index], self._function_items[index - 1] = (
                self._function_items[index - 1],
                self._function_items[index],
            )
            self._refresh_list()
            func_order = [f for f, _, _, _ in self._function_items]
            self.order_changed.emit(func_order)

    def _on_move_down(self, func: GameFunction):
        """
        向下移动功能项

        Args:
            func: 要移动的游戏功能枚举
        """
        index = next((i for i, (f, _, _, _) in enumerate(self._function_items) if f == func), -1)
        if index < len(self._function_items) - 1:
            self._function_items[index], self._function_items[index + 1] = (
                self._function_items[index + 1],
                self._function_items[index],
            )
            self._refresh_list()
            func_order = [f for f, _, _, _ in self._function_items]
            self.order_changed.emit(func_order)

    def _refresh_list(self):
        """刷新列表显示"""
        self.list_widget.clear()
        for i, (func, old_checkbox, _, _) in enumerate(self._function_items):
            widget, checkbox, up_btn, down_btn = self._create_item_widget(
                func, old_checkbox.isChecked(), i, len(self._function_items)
            )
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            self._function_items[i] = (func, checkbox, up_btn, down_btn)

    def get_selected_functions(self) -> list[tuple[GameFunction, bool]]:
        """
        获取所有功能及其选中状态

        Returns:
            功能及其选中状态的列表，每个元素为(GameFunction, bool)元组
        """
        return [(func, checkbox.isChecked()) for func, checkbox, _, _ in self._function_items]

    def set_function_selected(self, func: GameFunction, selected: bool):
        """
        设置功能的选中状态

        Args:
            func: 游戏功能枚举
            selected: 是否选中
        """
        for f, checkbox, _, _ in self._function_items:
            if f == func:
                checkbox.setChecked(selected)
                break

    def select_all(self):
        """全选所有功能"""
        for _, checkbox, _, _ in self._function_items:
            checkbox.setChecked(True)
        self.all_toggled.emit(True)

    def deselect_all(self):
        """取消全选所有功能"""
        for _, checkbox, _, _ in self._function_items:
            checkbox.setChecked(False)
        self.all_toggled.emit(False)

    def get_function_order(self) -> list[GameFunction]:
        """
        获取当前功能顺序

        Returns:
            当前功能顺序列表
        """
        return [func for func, _, _, _ in self._function_items]

    def reset_to_default(self):
        """重置为默认顺序（GameFunction定义顺序），全部勾选"""
        self._function_items.clear()
        self.list_widget.clear()
        for i, func in enumerate(GameFunction):
            widget, checkbox, up_btn, down_btn = self._create_item_widget(func, True, i, len(GameFunction))
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            self._function_items.append((func, checkbox, up_btn, down_btn))
