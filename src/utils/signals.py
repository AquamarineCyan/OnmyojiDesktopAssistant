from PySide6.QtCore import QObject, Signal


class CustomSignal(QObject):
    """自定义信号类

    用法:
    ```python
    from .signals import signal_manager
    ```
    """

    def __init__(self) -> None:
        self.main = self.Main()
        self.announcement = self.Announcement()
        self.update_new_version = self.UpdateNewVersion()

    class Main(QObject):
        """主界面"""

        message_box_requested = Signal(object)
        """请求弹窗

        Args:
            payload (MessageBoxPayload): 弹窗载荷，定义见 `src/utils/message.py`
        """

        ui_text_info_appended = Signal(str, str)
        """追加文本

        Args:
            msg (str): 文本内容
            color (str): 文本颜色
        """

        is_fighting_changed = Signal(bool)
        """运行状态更新

        Args:
            flag (bool): 运行状态，`True` 表示任务开始运行，`False` 表示任务结束
        """

        ui_text_progress_changed = Signal(str)
        """完成情况更新

        Args:
            msg (str): 完成情况文本，如 `3/50`（已完成次数/总次数）
        """

        key_pressed = Signal(str)
        """按键按下

        Args:
            key (str): 按键名称，如 `f1`，用于与设置的快捷键比较
        """

        window_status_changed = Signal(int, str)
        """窗口状态更新

        Args:
            count (int): 已检测到的游戏窗口数量，`0` 表示无窗口
            current_text (str): 当前窗口描述文本，格式为 `标题 - 句柄`，无窗口时为空字符串
        """

        window_list_changed = Signal(object)
        """游戏窗口列表变化

        由 `GlobalTask` 守护线程中的 `WindowManager.update_window_task` 发出，
        必须走信号：Qt 控件只能在 GUI 主线程操作，直接跨线程调用会崩溃。

        Args:
            game_window_list (list[GameWindow]): 当前检测到的游戏窗口列表，可能为空
        """

        window_button_enabled = Signal()
        """首次检测到游戏窗口，通知界面启用主功能控件"""

        xuanshangfengyin_detected = Signal(str, str)
        """悬赏封印通知

        Args:
            title (str): 标题
            content (str): 内容
        """

        sys_exit = Signal()
        """退出程序"""

    class Announcement(QObject):
        """公告"""

        show_ui = Signal(list)
        """显示公告窗口

        Args:
            announcements (list): 公告列表
        """

    class UpdateNewVersion(QObject):
        """更新新版本"""

        progress_text_changed = Signal(str)
        """更新文件进度文本

        Args:
            text (str): 下载进度文本，如 `1.00MB/10.00MB (速度: 1.00 MB/s)`
        """

        progress_bar_changed = Signal(int)
        """更新进度条

        Args:
            progress (int): 下载进度百分比，取值范围 `0-100`
        """

        show_ui = Signal()
        """显示窗口"""

        close_ui = Signal()
        """关闭窗口"""


signal_manager = CustomSignal()
