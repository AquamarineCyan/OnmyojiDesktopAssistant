"""`run_in_thread` 装饰器的线程命名测试。"""

import threading

from src.utils.decorator import run_in_thread


def test_custom_thread_name():
    names = []
    done = threading.Event()

    @run_in_thread(name="custom-worker")
    def _work():
        names.append(threading.current_thread().name)
        done.set()

    _work()

    assert done.wait(2)
    assert names == ["custom-worker"]


def test_default_thread_name_is_qualname():
    names = []
    done = threading.Event()

    @run_in_thread
    def _work():
        names.append(threading.current_thread().name)
        done.set()

    _work()

    assert done.wait(2)
    assert names[0].endswith("._work")
