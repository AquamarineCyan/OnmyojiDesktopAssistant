import functools
import inspect
import os
from threading import Thread

from .log import logger


def log_function_call(func):
    """记录被装饰函数的调用日志

    在调用前后分别输出函数限定名，并打印实际传入的位置参数与关键字参数。
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"func[{func.__qualname__}] calling")
        if len(args) > 1:
            logger.info(f"*args: {args}")
        if kwargs:
            logger.info(f"**kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"func[{func.__qualname__}] finish")
        return result

    return wrapper


def run_in_thread(func=None, *, name: str | None = None):
    """在后台线程中运行被装饰函数

    Args:
        name: 线程名称，缺省时使用函数限定名。
    """

    def decorator(_func):
        @functools.wraps(_func)
        def wrapper(*args, **kwargs):
            Thread(
                target=_func,
                name=name or _func.__qualname__,
                args=args,
                kwargs=kwargs,
                daemon=True,
            ).start()

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def log_caller(func):
    """将调用方信息作为首个参数传给被装饰函数

    Args:
        func: 需要接收调用方信息的函数，其第一个参数为
            ``文件名:行号:函数名`` 形式的字符串。
    """

    def wrapper(*args, **kwargs):
        caller_frame = inspect.currentframe().f_back
        short_filename = os.path.basename(caller_frame.f_code.co_filename)
        caller_name = f"{short_filename}:{caller_frame.f_lineno}:{caller_frame.f_code.co_name}"
        return func(caller_name, *args, **kwargs)

    return wrapper
