from threading import Thread

from win11toast import toast as win_toast

from .application import APP_NAME
from .config import config
from .log import logger


def toast(*args, **kwargs):
    if config.user.win_toast:
        logger.info("Toast is enabled.")
        kwargs.setdefault("app_id", APP_NAME)
        Thread(target=win_toast, name="thread_toast", args=args, kwargs=kwargs, daemon=True).start()
    else:
        logger.info("Toast is disabled.")
