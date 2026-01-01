from ..utils.config import config
from ..utils.event import event_xuanshang
from ..utils.image import RuleImage
from ..utils.log import logger
from ..utils.screenshot import ScreenShot
from ..utils.toast import toast
from ..utils.window import window_manager
from .base_package import BasePackage
from .global_parameter import xuanshangfengyin_count


class XuanShangFengYin(BasePackage):
    """悬赏封印"""

    scene_name = "悬赏封印"
    resource_path = "xuanshangfengyin"
    resource_list: list = [
        "title",  # 特征图像
        "xuanshang_accept",  # 接受
        "xuanshang_refuse",  # 拒绝
        "xuanshang_ignore",  # 忽略
    ]

    def __init__(self) -> None:
        super().__init__()
        self._flag_is_first: bool = True
        self._flag_msg: bool = False
        event_xuanshang.set()

    def load_asset(self):
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_ACCEPT = self.get_image_asset("accept")
        self.IMAGE_IGNORE = self.get_image_asset("ignore")
        self.IMAGE_REFUSE = self.get_image_asset("refuse")

    def check_task(self):
        if not window_manager.is_alive:
            return

        if config.user.xuanshangfengyin == "关闭":
            return

        image = RuleImage(self.IMAGE_TITLE)
        _screenshot = ScreenShot()  # FIXME (0,0,0,0)
        if not image.match(_screenshot, normal=False):
            event_xuanshang.set()
            if self._flag_msg:
                self._flag_msg = False
                logger.ui("悬赏封印已消失，恢复线程")
            return

        # 检测到悬赏封印
        event_xuanshang.clear()
        logger.scene(self.scene_name)
        logger.ui_warn("已暂停后台线程，等待处理")
        toast("悬赏封印", "检测到悬赏封印")
        self._flag_msg = True
        match config.user.xuanshangfengyin:
            case "接受":
                _msg = "接受协作"
                _asset = self.IMAGE_ACCEPT
            case "拒绝":
                _msg = "拒绝协作"
                _asset = self.IMAGE_REFUSE
            case "忽略":
                _msg = "忽略协作"
                _asset = self.IMAGE_IGNORE
            case _:
                _msg = "用户配置出错，自动接受协作"
                _asset = self.IMAGE_ACCEPT
        logger.ui(_msg)
        event_xuanshang.set()
        self.check_click(_asset, 5, "center")

        xuanshangfengyin_count.add()
