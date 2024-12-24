from .log import logger


class GUIStopException(Exception):
    """GUI停止按钮"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：GUI停止按钮")


class TimesNotEnoughException(Exception):
    """次数不足"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：次数不足")
