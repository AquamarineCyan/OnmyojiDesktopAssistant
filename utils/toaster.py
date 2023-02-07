"""系统通知"""
from win10toast import ToastNotifier


def toaster(title: str, msg: str) -> None:
    """系统通知

    Args:
        title (str): 标题
        msg (str): 消息内容
    """
    _toaster = ToastNotifier()
    try:
        _toaster.show_toast(title=title, msg=msg, icon_path="buzhihuo.ico", duration=None, threaded=True)
    except TypeError:
        pass
