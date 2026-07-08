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
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        Thread(target=func, name=func.__qualname__, args=args, kwargs=kwargs, daemon=True).start()

    return wrapper


def log_caller(func):
    def wrapper(*args, **kwargs):
        caller_frame = inspect.currentframe().f_back
        short_filename = os.path.basename(caller_frame.f_code.co_filename)
        caller_name = f"{short_filename}:{caller_frame.f_lineno}:{caller_frame.f_code.co_name}"
        return func(caller_name, *args, **kwargs)

    return wrapper
