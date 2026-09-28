from dataclasses import dataclass
from enum import StrEnum


@dataclass
class MessageBoxPayload:
    """弹窗载荷

    用法:
    ```python
    from .message import MessageBoxPayload
    from .signals import signal_manager
    signal_manager.main.message_box_requested.emit(MessageBoxPayload.error("未选中窗口"))
    ```
    """

    class Level(StrEnum):
        """弹窗级别"""

        ERROR = "ERROR"
        QUESTION = "QUESTION"

    class Action(StrEnum):
        """弹窗操作内容

        值即界面文案（与 `src/package/types.py` 的枚举约定一致）

        逻辑判断必须使用枚举成员，禁止与字面量比较
        """

        FORCE_ZOOM = "强制缩放"
        UPDATE_RESTART = "更新重启"

    level: Level
    content: str = ""  # 弹窗正文（`Level.ERROR` 使用）
    action: Action | None = None  # 动作标识（`Level.QUESTION` 使用）

    @classmethod
    def error(cls, content: str) -> "MessageBoxPayload":
        """构造错误弹窗载荷"""
        return cls(level=cls.Level.ERROR, content=content)

    @classmethod
    def question(cls, action: Action) -> "MessageBoxPayload":
        """构造询问弹窗载荷"""
        return cls(level=cls.Level.QUESTION, action=action)
