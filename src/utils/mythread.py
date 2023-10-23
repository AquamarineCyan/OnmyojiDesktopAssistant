import time
from threading import Thread, Timer


class WorkThread(Thread):
    """
    目前只能用事件类 `Event` 实现停止，需要在每个循环里插入

    用法:
    ```python
    from ..utils.event import event_thread
    if event_thread.is_set():
        return
    ```
    """

    def __init__(self, func, args=None, kwargs=None):
        super().__init__()
        self.func = func
        self.name = func.__qualname__
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.daemon = True
        self.result = None

    def run(self):
        time.sleep(0.5)
        self.result = self.func(*self.args, **self.kwargs)

    def get_result(self):  # TODO 在不阻塞主线程的情况下无法实现返回值，使用Thread.join()会阻塞ui
        try:
            return self.result
        except Exception:
            return None


class WorkTimer(Timer):
    def __init__(self, interval, function, args=None, kwargs=None):
        super().__init__(interval, function, args, kwargs)
        self.daemon = True


"""
class WorkThread(Thread):
    
    def __init__(self, func, args=None, kwargs=None):
        super().__init__()
        self.func = func
        self.args = args
        self.name = func.__qualname__
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.daemon = False
        self.result = None
        logger.debug("WorkThread")
        logger.debug(f"线程事件状态{event_thread.is_set()}")

    def run(self):
        def thread_b():
            logger.info("thread_b()")
            self.func(*self.args, **self.kwargs)
        # self.func(*self.args, **self.kwargs)
        #  创建子线程 B，并指定为子线程 A 的守护线程
        b = threading.Thread(target=thread_b, daemon=True)
        b.start()

        # 循环检查停止信号
        # while not event_thread.is_set():
            # pass
        logger.debug("waiting")
        event_thread.clear()
        event_thread.wait()

        # 如果停止信号为 True，则退出子线程 A
        logger.debug("线程异常结束")
        return

        # while True:
        #     if event_thread.is_set():
        #         print("线程异常结束")
        #         return

    def thread_stop(self):
        logger.ui("stopping, please waiting...")
    def get_result(self):
        try:
            return self.result
        except Exception:
            return None
"""
