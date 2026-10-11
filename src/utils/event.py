from threading import Event

WAIT_EVENT_TIMEOUT: float = 5.0
"""`event_xuanshang.wait()` 的超时时间（秒）

`event_xuanshang` 由 `XuanShangFengYin.check_task` 成对 clear/set，
一旦 clear 之后抛出异常（异常会被 GlobalTask 吞掉），事件就永远不会
被 set。此时无超时的 `wait()` 会让主任务线程永久阻塞，连停止按钮都
失效。所有等待都必须带超时。
"""


class MyEvent(Event):
    def __bool__(self):
        return self.is_set()


event_thread = MyEvent()
"""主界面停止按钮事件

    用法:
```python
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
if bool(event_thread):
    raise GUIStopException
```
"""
event_xuanshang = MyEvent()
"""悬赏封印"""
