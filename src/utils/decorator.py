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

from .log import logger
from .mysignal import global_ms as ms
from .mythread import WorkThread
from .toast import toast


def log_function_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("{}() calling".format(func.__qualname__))
        if len(args) > 1:
            logger.info("*args: {}".format(args))
        if kwargs:
            logger.info("**kwargs: {}".format(kwargs))
        result = func(*args, **kwargs)
        logger.info("{}() finish".format(func.__qualname__))
        return result
    return wrapper


def time_count(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 禁用按钮
        ms.is_fighting_update.emit(True)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        try:
            if end - start >= 60:
                logger.ui(f"耗时{int((end - start) // 60)}分{int((end - start) % 60)}秒")
            else:
                logger.ui(f"耗时{int(end - start)}秒")
        except Exception:
            logger.error("耗时统计计算失败")
        # 启用按钮
        ms.is_fighting_update.emit(False)
        # 系统通知
        # 5s结束，保留至通知中心
        toast("任务已完成")
        return result
    return wrapper


def run_in_thread(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t = WorkThread(func=func, args=args, kwargs=kwargs)
        t.start()
        return t.get_result()
    return wrapper
