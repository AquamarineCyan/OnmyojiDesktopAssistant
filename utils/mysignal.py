"""自定义信号"""

from PySide6.QtCore import QObject, Signal


class MySignals(QObject):
    """自定义信号类"""
    # 弹窗更新
    qmessagbox_update = Signal(str, str)
    # 主界面信息文本更新
    text_print_update = Signal(str)
    # 运行状态更新
    is_fighting_update = Signal(bool)
    # 完成情况文本更新
    text_num_update = Signal(str)
    # 配置项同步gui
    setting_to_ui_update = Signal(str, str)


global_ms = MySignals()
