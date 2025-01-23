from .log import logger


class CustomException(Exception):
    """自定义异常"""


class GUIStopException(CustomException):
    """GUI停止按钮"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：GUI停止按钮")


class TimesNotEnoughException(CustomException):
    """次数不足"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：次数不足")


class TimeoutException(CustomException):
    """超时"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：超时")
