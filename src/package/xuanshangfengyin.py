from ..utils.config import XuanShangFengYin as XuanShangFengYinMode
from ..utils.config import config
from ..utils.event import event_xuanshang
from ..utils.image import RuleImage
from ..utils.log import logger
from ..utils.mysignal import global_ms as ms
from ..utils.screenshot import ScreenShot
from ..utils.toast import toast
from ..utils.window import window_manager
from .base_package import BasePackage


class XuanShangFengYin(BasePackage):
    """悬赏封印"""

    scene_name = "悬赏封印"
    resource_path = "xuanshangfengyin"
    resource_list: list = [
        "title",  # 标题
        "xuanshang_accept",  # 接受
        "xuanshang_ignore",  # 忽略
        "xuanshang_refuse",  # 拒绝
    ]

    def __init__(self) -> None:
        super().__init__()
        self._flag_is_first: bool = True
        self._flag_msg: bool = False
        self._flag_notify: bool = False
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

        image = RuleImage(self.IMAGE_TITLE)
        _screenshot = ScreenShot()  # FIXME (0,0,0,0)
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
            ms.main.ui_xuanshangfengyin_update.emit("悬赏封印", "检测到悬赏封印，请及时处理")
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
