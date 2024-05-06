from ..utils.assets import AssetImage
from ..utils.config import config
from ..utils.decorator import run_in_thread
from ..utils.event import event_xuanshang
from ..utils.image import RuleImage
from ..utils.log import logger
from ..utils.myschedule import global_scheduler
from ..utils.screenshot import ScreenShot
from ..utils.toast import toast
from .utils import Package, get_asset


class XuanShangFengYin(Package):
    """悬赏封印"""

    scene_name = "悬赏封印"
    resource_path = "xuanshangfengyin"
    resource_list: list = [
        "title",  # 特征图像
        "xuanshang_accept",  # 接受
        "xuanshang_refuse",  # 拒绝
        "xuanshang_ignore",  # 忽略
    ]
    STATE_STOP = 1
    STATE_START = 2

    def __init__(self) -> None:
        self._flag_is_first: bool = True
        self._flag_msg: bool = False
        self.state = self.STATE_STOP
        event_xuanshang.set()
        self.load_asset_list()
        try:
            self.IMAGE_TITLE = AssetImage(**get_asset(self.asset_image_list, "title"))
            self.IMAGE_ACCEPT = AssetImage(**get_asset(self.asset_image_list, "accept"))
            self.IMAGE_IGNORE = AssetImage(**get_asset(self.asset_image_list, "ignore"))
            self.IMAGE_REFUSE = AssetImage(**get_asset(self.asset_image_list, "refuse"))
        except Exception as e:
            logger.error(f"{self.resource_path}/assets.json 资源加载失败：{e}")
            logger.ui_error(
                f"{self.resource_path}/assets.json 资源加载失败，请检查资源文件"
            )

    def scheduler_check(self):
        if config.config_user.xuanshangfengyin == "关闭":
            return

        image = RuleImage(self.IMAGE_TITLE)
        _screenshot = ScreenShot()
        if not image.match(_screenshot):
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
        match config.config_user.xuanshangfengyin:
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

    @run_in_thread
    def task_start(self):
        if config.config_user.xuanshangfengyin == "关闭":
            if global_scheduler.get_job(self.resource_path):
                logger.ui("检测到悬赏封印已关闭，停止定时任务")
                global_scheduler.remove_job(self.resource_path)
                self.state = self.STATE_STOP
        elif self.state == self.STATE_STOP:
            # 添加定时任务，间隔1分钟，同一时间只有一个实例在运行
            global_scheduler.add_job(
                self.scheduler_check,
                "interval",
                seconds=1,
                id=self.resource_path,
                coalesce=True,
            )
            self.state = self.STATE_START


task_xuanshangfengyin = XuanShangFengYin()
