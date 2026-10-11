import functools
import inspect
import os
from threading import Thread

from .log import logger


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


def run_in_thread(func):
    """把调用放到守护线程执行。

    必须捕获异常：工作线程里的 traceback 默认只打到 stderr，而打包产物
    没有控制台（stderr 虽被 `log.redirect_third_party_output` 重定向，
    但重定向本身也可能失效），异常会彻底静默——调用方拿不到返回值，
    日志里也查不到，只会看到「功能没反应」。
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        def _run():
            try:
                func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{func.__qualname__} 线程内异常: {e}", exc_info=True)

        Thread(target=_run, name=func.__qualname__, daemon=True).start()

    return wrapper


def log_caller(func):
    def wrapper(*args, **kwargs):
        caller_frame = inspect.currentframe().f_back
        short_filename = os.path.basename(caller_frame.f_code.co_filename)
        caller_name = f"{short_filename}:{caller_frame.f_lineno}:{caller_frame.f_code.co_name}"
        return func(caller_name, *args, **kwargs)

    return wrapper
