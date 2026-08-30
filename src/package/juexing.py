from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import check_image_once
from ..utils.log import logger
from .base_package import BasePackage


class JueXing(BasePackage):
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

    def load_asset(self):
        self.IMAGE_TITLE = self.get_image_asset("title")

    @log_function_call
    def start(self):
        """挑战开始"""
        self.check_click(self.global_assets.IMAGE_START_SINGLE)

    def run(self):
        self.current_asset_list = [
            self.IMAGE_TITLE,
            self.global_assets.IMAGE_START_SINGLE,
            self.global_assets.IMAGE_FINISH,
        ]
        self.current_asset_list.extend(self.global_assets.ALL_VICTORY_IMAGES)
        self.current_asset_list.extend(self.global_assets.ALL_FAIL_IMAGES)
        msg_title: bool = True
        self.log_current_asset_list()

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            match result.name:
                case "title":
                    logger.ui_hint(self.scene_name)
                    msg_title = False
                    self.start()
                case "start_single":
                    Mouse.click(result.center_point())
                case name if name in self.global_assets.ALL_FAIL_NAMES:
                    logger.ui_warn(
                        f"失败{('（' + result.description + '）') if result.description else ''}，需要手动处理"
                    )
                    break
                case name if name in self.global_assets.ALL_VICTORY_NAMES:
                    logger.ui(f"胜利{('（' + result.description + '）') if result.description else ''}")
                case "finish":
                    finish_random_left_right()
                    self.done()
                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False
            sleep()
