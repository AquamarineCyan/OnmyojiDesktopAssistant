from ..utils.adapter import Mouse
from ..utils.assets import AssetImage
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import check_image_once
from ..utils.log import logger
from .utils import Package, get_asset


class JueXing(Package):
    """觉醒副本"""

    scene_name = "觉醒副本"
    resource_path = "juexing"
    resource_list = [
        "title",  # 标题
    ]

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)
    
    @staticmethod
    def description() -> None:
        logger.ui("单人觉醒副本")

    @log_function_call
    def start(self):
        """挑战开始"""
        self.check_click(self.global_image.IMAGE_START_SINGLE)

    def load_asset(self):
        self.IMAGE_TITLE = AssetImage(**get_asset(self.asset_image_list, "title"))

    def run(self):
        self.current_asset_list = [
            self.IMAGE_TITLE,
            self.global_image.IMAGE_START_SINGLE,
            self.global_image.IMAGE_FINISH,
            self.global_image.IMAGE_FAIL,
            self.global_image.IMAGE_VICTORY,
        ]
        msg_title: bool = True
        self.log_current_asset_list()

        while self.n < self.max:
            if bool(event_thread):
                return
            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            match result.name:
                case "title":
                    logger.scene(self.scene_name)
                    msg_title = False
                    self.start()
                case "start_single":
                    Mouse.click(result.center_point())
                case "fail":
                    logger.ui_warn("失败，需要手动处理")
                    break
                case "victory":
                    logger.ui("胜利")
                case "finish":
                    finish_random_left_right()
                    self.done()
                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False
            sleep()
