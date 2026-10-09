import time

from ..utils.config import XuanShangFengYin as XuanShangFengYinMode
from ..utils.config import config
from ..utils.event import event_xuanshang
from ..utils.image import RuleImage
from ..utils.log import logger
from ..utils.screenshot import ScreenShot
from ..utils.signals import signal_manager
from ..utils.toast import toast
from ..utils.window import window_manager
from .base_package import BasePackage


class XuanShangFengYin(BasePackage):
    """悬赏封印"""

    scene_name = "悬赏封印"
    resource_path = "xuanshangfengyin"
    resource_list = (
        "title",  # 标题
        "xuanshang_accept",  # 接受
        "xuanshang_ignore",  # 忽略
        "xuanshang_refuse",  # 拒绝
    )

    check_interval: float = 1.0
    """检测间隔（秒）"""

    def __init__(self) -> None:
        super().__init__()
        self._flag_is_first: bool = True
        self._flag_msg: bool = False
        self._flag_notify: bool = False
        self._last_check_timestamp: float = 0.0  # 上次检测时间戳
        event_xuanshang.set()

    def load_asset(self):
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_ACCEPT = self.get_image_asset("accept")
        self.IMAGE_IGNORE = self.get_image_asset("ignore")
        self.IMAGE_REFUSE = self.get_image_asset("refuse")

    def check_task(self):
        if not window_manager.is_alive:
            return

        if config.user.xuanshangfengyin == XuanShangFengYinMode.CLOSE:
            return

        now = time.monotonic()
        if now - self._last_check_timestamp < self.check_interval:
            return
        self._last_check_timestamp = now

        image = RuleImage(self.IMAGE_TITLE)
        _screenshot = ScreenShot()  # FIXME (0,0,0,0)
        if _screenshot.get_image() is None:
            # 截图失败（窗口最小化/句柄失效等），本轮跳过，等待下一轮检测
            logger.warning("悬赏封印检测跳过：截图失败")
            return
        if not image.match(_screenshot, normal=False):
            event_xuanshang.set()
            self._flag_notify = False
            if self._flag_msg:
                self._flag_msg = False
                logger.ui("悬赏封印已消失，恢复线程")
            return

        # 检测到悬赏封印
        event_xuanshang.clear()
        logger.ui_hint(self.scene_name)
        logger.ui_warn("已暂停后台线程，等待处理")
        toast("悬赏封印", "检测到悬赏封印")
        if not self._flag_notify:
            self._flag_notify = True
            signal_manager.main.xuanshangfengyin_detected.emit("悬赏封印", "检测到悬赏封印，请及时处理")
        self._flag_msg = True
        match config.user.xuanshangfengyin:
            case XuanShangFengYinMode.ACCEPT:
                _msg = "接受协作"
                _asset = self.IMAGE_ACCEPT
            case XuanShangFengYinMode.REJECT:
                _msg = "拒绝协作"
                _asset = self.IMAGE_REFUSE
            case XuanShangFengYinMode.IGNORE:
                _msg = "忽略协作"
                _asset = self.IMAGE_IGNORE
            case _:
                _msg = "用户配置出错，自动接受协作"
                _asset = self.IMAGE_ACCEPT
        logger.ui(_msg)
        event_xuanshang.set()  # 优先于点击事件
        self.check_click(_asset, 5, "center")

        config.runtime.xuanshangfengyin.add()
