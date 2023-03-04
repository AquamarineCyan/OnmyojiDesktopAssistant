from threading import Thread
from win11toast import toast as win_toast


def toast(*args, **kwargs):
    Thread(
        target=win_toast,
        name="thread_toast",
        args=args,
        kwargs=kwargs,
        daemon=True
    ).start()
