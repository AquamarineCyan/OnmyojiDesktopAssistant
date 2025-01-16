from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import check_image_once
from ..utils.log import logger
from .utils import Package


class YeYuanHuo(Package):
    """业原火副本"""

    scene_name = "业原火副本"
    resource_path = "yeyuanhuo"
    resource_list = [
        "title",  # 标题
        "start",  # 挑战
    ]

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    @staticmethod
    def description() -> None:
        logger.ui("默认为“痴”，可在/data/myresource/yeyuanhuo路径下添加自定义素材")

    def load_asset(self):
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_START = self.get_image_asset("start")

    def run(self):
        self.current_asset_list = [
            self.IMAGE_TITLE,
            self.IMAGE_START,
            self.global_assets.IMAGE_FINISH,
            self.global_assets.IMAGE_VICTORY,
        ]
        msg_title: bool = True
        self.log_current_asset_list()

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException
            
            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            logger.info(f"current result name: {result.name}")
            match result.name:
                case "title":
                    logger.scene(self.scene_name)
                    msg_title = False
                    self.start(timeout=10)
                    sleep(self.fast_time)
                case "start":
                    Mouse.click(result.random_point())
                    sleep(self.fast_time)
                case "fail":
                    logger.ui_warn("失败，需要手动处理")
                    break
                case "victory":
                    logger.ui("胜利")
                    sleep()
                case "finish":
                    logger.ui("结束")
                    if self.check_click(
                        self.global_image.IMAGE_SOUL_OVERFLOW, timeout=2
                    ):
                        logger.ui_warn("御魂上限")
                    finish_random_left_right()
                    self.done()
                    sleep(2)
                case "soul_overflow":  # 正常情况下会在结束界面点击，这是备用方案
                    logger.ui_warn("御魂上限")
                    Mouse.click(result.random_point())
                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False
