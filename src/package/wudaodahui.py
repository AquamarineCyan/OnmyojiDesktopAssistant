import time

from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import check_image_once
from ..utils.log import logger
from .base_package import BasePackage


class WuDaoDaHui(BasePackage):
    """武道大会"""

    scene_name = "武道大会"
    resource_path = "wudaodahui"
    resource_list = [
        "search",  # 搜寻
        "start",  # 开始
        "title",  # 标题
    ]

    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    @staticmethod
    def description() -> None:
        logger.ui("武道大会，仅支持挂机阵容。至少每种类型的阵容试过一次，进入挑战会自动准备。")

    def load_asset(self):
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_START = self.get_image_asset("start")
        self.IMAGE_SEARCH = self.get_image_asset("search")

    @log_function_call
    def start(self):
        """挑战开始"""
        self.check_click(self.IMAGE_SEARCH)
        sleep(5)
        logger.ui("开始挑战")
        self.check_click(self.IMAGE_START)
        sleep(2)
        self.ready()

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
                case self.IMAGE_TITLE.name:
                    logger.scene(self.scene_name)
                    msg_title = False
                    self.start()

                case name if name in self.global_assets.ALL_FAIL_NAMES:
                    logger.ui_warn(
                        f"失败{('（' + result.description + '）') if result.description else ''}，需要手动处理"
                    )
                    break
                case name if name in self.global_assets.ALL_VICTORY_NAMES:
                    logger.ui(f"胜利{('（' + result.description + '）') if result.description else ''}")
                    finish_random_left_right()
                    self.done()
                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False
            sleep()
