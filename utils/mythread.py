import threading
import time
import ctypes
import win32con

from PySide6.QtCore import QThread

from .event import event_thread


class MyThread(threading.Thread):

    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.result = []

    def run(self):
        time.sleep(1)
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


class WorkThread(threading.Thread):  # TODO stop thread

    def __init__(self, func, args=()):
        super(WorkThread, self).__init__()
        self.func = func
        self.args = args
        # self.result = []
        print("WorkThread")
        # print("线程事件状态",event_thread.is_set())

    def run(self):
        time.sleep(1)
        # self.result = self.func(*self.args)

        def thread_b():
            print("***************************************")
            self.func(*self.args)

        #  创建子线程 B，并指定为子线程 A 的守护线程
        b = threading.Thread(target=thread_b)
        b.daemon = True
        b.start()

        # 循环检查停止信号
        while not event_thread.is_set():
            pass

        # 如果停止信号为 True，则退出子线程 A
        print("线程异常结束")
        return

        # while True:
        #     if event_thread.is_set():
        #         print("线程异常结束")
        #         return

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


class MyThread_QTread(QThread):
    handle = -1

    def __init__(self, func, args=()):
        super(MyThread_QTread, self).__init__()
        self.func = func
        self.args = args
        print("MyThread_QTread")

    def run(self):
        time.sleep(1)
        try:
            self.handle = ctypes.windll.kernel32.OpenThread(
                win32con.PROCESS_ALL_ACCESS,
                False,
                int(QThread.currentThreadId())
            )
        except Exception as e:
            print('get thread handle failed', e)
        print('thread id', int(QThread.currentThreadId()))

        self.func(*self.args)
