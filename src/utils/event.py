from threading import Event

event_thread = Event()
"""主界面停止按钮事件

    用法:
```python
from ..utils.event import event_thread
if event_thread.is_set():
    return
```
"""
event_xuanshang = Event()
"""悬赏封印"""
event_xuanshang_enable = Event()
"""悬赏封印启用状态"""
event_ocr_init = Event()
"""OCR（文字识别）初始化"""
