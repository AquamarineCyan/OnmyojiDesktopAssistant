from .log import logger


class CustomException(Exception):
    """自定义异常"""


class GUIStopException(CustomException):
    """GUI停止按钮"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("手动停止")


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


class DailyLimitException(CustomException):
    """该玩法次数已达本日上限"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：该玩法次数已达本日上限")


class ScreenshotFailedException(CustomException):
    """截图失败

    重试耗尽后仍然拿不到像素时抛出。此前该情况会让 `get_image()` 返回 None，
    再经 `np.array(None)` / `cv2.cvtColor` 变成看不懂的 `cv2.error`，
    真实原因（游戏窗口失效、最小化、句柄销毁）被完全埋掉。
    """

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：截图失败，请检查游戏窗口是否正常运行")
