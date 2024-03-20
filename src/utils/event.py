from threading import Event


class MyEvent(Event):
    def __bool__(self):
        return self.is_set()


event_thread = MyEvent()
"""主界面停止按钮事件

    用法:
```python
from ..utils.event import event_thread
if bool(event_thread):
    return
```
"""
event_xuanshang = MyEvent()
"""悬赏封印"""
event_ocr_init = MyEvent()
"""OCR（文字识别）初始化"""
