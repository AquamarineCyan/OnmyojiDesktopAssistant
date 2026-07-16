import time

from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import check_image_once
from ..utils.log import logger
from .base_package import BasePackage
from .types import MiWenMode


class MiWen(BasePackage):
    """每周秘闻"""

    scene_name = "每周秘闻"
    resource_path = "miwen"
    mode: MiWenMode

    @log_function_call
    def __init__(self, n: int = 0, mode: MiWenMode = MiWenMode.BAI_ZHAN):
        super().__init__(n)
        self.mode = mode

    @staticmethod
    def description():
        logger.ui("每周秘闻，请锁定阵容，并打开金币加成。战斗胜利后游戏会自动跳转下一层。")
        logger.ui_error("百战模式等待测试。")

    def load_asset(self):
        self.IMAGE_PAIMING = self.get_image_asset("paiming")
        self.IMAGE_START = self.get_image_asset("start")
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_TONGGUANZHENRONG = self.get_image_asset("tongguanzhenrong")

    def start(self):
        logger.ui("挑战")
        self.check_click(self.IMAGE_START)

    def ready(self):
        start_time = time.time()
        timeout = 10  # 累计超时10秒
        while time.time() - start_time < timeout:
            if bool(event_thread):
                raise GUIStopException
            if self.check_click(self.global_assets.IMAGE_READY_OLD, timeout=1):
                logger.ui("准备（怀旧主题）")
                return
            if self.check_click(self.global_assets.IMAGE_READY_NEW, timeout=1):
                logger.ui("准备（简约主题）")
                return
            sleep(0.5)
        logger.warning("未找到准备按钮")

    def run(self):
        self.current_asset_list = [
            self.IMAGE_TITLE,
            # self.IMAGE_START,
            # self.IMAGE_PAIMING,
            # self.IMAGE_TONGGUANZHENRONG,
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
                case self.IMAGE_TITLE.name:
                    logger.scene(self.scene_name)
                    msg_title = False
                    self.start()
                    sleep(2)
                    self.ready()
                # case self.IMAGE_START.name:
                #     Mouse.click(result.center_point())
                case self.global_assets.IMAGE_FAIL.name:
                    logger.ui_error("失败，需要手动处理")
                    break
                case self.global_assets.IMAGE_VICTORY.name:
                    logger.ui("胜利")
                    sleep(3)
                    if self.mode == MiWenMode.JING_SU:
                        Mouse.click(result.center_point())
                        self.done()
                case self.global_assets.IMAGE_FINISH.name:
                    logger.ui("结算中")
                    sleep(2)  # 等待掉落物动画
                    finish_random_left_right()
                    self.done()
                # case self.IMAGE_PAIMING.name | self.IMAGE_TONGGUANZHENRONG.name:
                #     logger.info(f"最后一层：{result.name}")
                #     logger.scene("已通关本周秘闻，请手动前往分享。")
                #     self.done()
                #     break  # 强制退出
                case _:
                    if msg_title:
                        self.title_error_msg()

                        msg_title = False
            sleep()

        logger.scene("已通关本周秘闻，请手动前往分享。")
