"""自定义信号"""
from PySide6.QtCore import QObject, Signal


class MySignals(QObject):
    """自定义信号类"""
    # 弹窗更新
    qmessagbox_update = Signal(str, str)
    # 主界面信息文本更新
    text_print_update = Signal(str, str)
    """主界面信息文本更新

    参数：

    文本内容
    
    文本颜色
    """
    # 运行状态更新
    is_fighting_update = Signal(bool)
    # 完成情况文本更新
    text_num_update = Signal(str)
    # 更新日志文本更新
    ui_update_record_textBrowser_update = Signal(str)
    # 退出程序
    sys_exit_update = Signal(bool)
    # 主界面信息文本覆盖
    text_print_insert_update = Signal(str)


global_ms = MySignals()
