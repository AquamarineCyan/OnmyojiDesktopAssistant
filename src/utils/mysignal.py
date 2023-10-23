"""自定义信号"""
from PySide6.QtCore import QObject, Signal


class MySignals(QObject):
    """自定义信号类"""

    def __init__(self) -> None:
        self.main = self.Main()
        self.upgrade_new_version = self.UpgradeNewVersion()
        self.update_record = self.UpdateRecord()

    class Main(QObject):
        """主界面"""
        qmessagbox_update = Signal(str, str)
        """弹窗更新
        
        参数:
        
        (str): 弹窗类型:
        `ERROR`: 警告
        `question`: 提示

        (str): 文本内容
        """
        text_print_update = Signal(str, str)
        """更新文本

        参数：

        (str): 文本内容
        
        (str): 文本颜色
        """
        text_print_insert_update = Signal(str)
        """覆盖文本"""
        is_fighting_update = Signal(bool)
        """运行状态更新"""
        text_num_update = Signal(str)
        """完成情况文本更新"""
        sys_exit = Signal()
        """退出程序"""

    class UpdateRecord(QObject):
        """更新记录"""
        text_update = Signal(str)
        """更新文本"""

    class UpgradeNewVersion(QObject):
        """更新新版本"""
        text_update = Signal(str)
        """更新文本"""
        text_insert = Signal(str)
        """覆盖文本"""
        progressBar_update = Signal(int)
        """更新进度条"""
        show_ui = Signal()
        """显示窗口"""
        close_ui = Signal()
        """关闭窗口"""


global_ms = MySignals()
