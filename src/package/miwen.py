from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import check_image_once
from ..utils.log import logger
from .base_package import BasePackage


class MiWen(BasePackage):
    """每周秘闻"""

    scene_name = "每周秘闻"
    resource_path = "miwen"

    @log_function_call
    def __init__(self, n: int = 0):
        super().__init__(n)

    @staticmethod
    def description():
        logger.ui("每周秘闻，请锁定阵容，并打开金币加成。战斗胜利后游戏会自动跳转下一层。")

    def load_asset(self):
        self.IMAGE_PAIMING = self.get_image_asset("paiming")
        self.IMAGE_START = self.get_image_asset("start")
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_TONGGUANZHENRONG = self.get_image_asset("tongguanzhenrong")

    def start(self):
        self.check_click(self.IMAGE_START)

    def run(self):
        self.current_asset_list = [
            self.IMAGE_TITLE,
            self.IMAGE_START,
            self.IMAGE_PAIMING,
            self.IMAGE_TONGGUANZHENRONG,
            self.global_assets.IMAGE_FINISH,
            self.global_assets.IMAGE_FAIL,
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

            match result.name:
                case "title":
                    logger.scene(self.scene_name)
                    msg_title = False
                    self.start()
                case "start":
                    Mouse.click(result.center_point())
                case "fail":
                    logger.ui_warn("失败，需要手动处理")
                    break
                case "victory":
                    logger.ui("胜利")
                case "finish":
                    logger.ui("结算中")
                    sleep(2)  # 等待掉落物动画
                    finish_random_left_right()
                    self.done()
                case self.IMAGE_PAIMING.name | self.IMAGE_TONGGUANZHENRONG.name:
                    logger.info(f"最后一层：{result.name}")
                    logger.scene("已通关本周秘闻，请手动前往分享。")
                    self.done()
                    break  # 强制退出

                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False
            sleep()
