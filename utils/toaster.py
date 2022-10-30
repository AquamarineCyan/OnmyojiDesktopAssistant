"""系统通知"""
from win10toast import ToastNotifier


def toaster(title: str, msg: str, duration: int = 5) -> None:
    """
    系统通知

    :param title: 标题
    :param msg: 消息内容
    :param duration: 持续时间
    :return: None
    """
    _toaster = ToastNotifier()
    _toaster.show_toast(title=title, msg=msg, icon_path="buzhihuo.ico", duration=duration, threaded=True)
