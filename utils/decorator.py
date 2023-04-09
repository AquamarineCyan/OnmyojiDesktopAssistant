#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# decorator.py
"""装饰器
    
    用法:
        ```python
        @run_in_thread
        @time_count
        @log_function_call
        ```
"""

import functools
import time

from .log import log
from .mythread import MyThread
from .toast import toast


def log_function_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        log.info("{} calling".format(func.__qualname__))
        result =  func(*args, **kwargs)
        log.info("{} finish".format(func.__qualname__))
        return result
    return wrapper


def time_count(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 禁用按钮
        log.is_fighting(True)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        try:
            if end - start >= 60:
                log.ui(f"耗时{int((end - start) // 60)}分{int((end - start) % 60)}秒")
            else:
                log.ui(f"耗时{int(end - start)}秒")
        except:
            log.error("耗时统计计算失败")
        # 启用按钮
        log.is_fighting(False)
        # 系统通知
        # 5s结束，保留至通知中心
        toast("任务已完成")
        return result
    return wrapper


def run_in_thread(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t = MyThread(func=func, args=args, kwargs=kwargs)
        t.start()
        return t.get_result()
    return wrapper
