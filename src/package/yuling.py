from ..utils.assets import AssetImage
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.log import logger
from .utils import Package, get_asset


class YuLing(Package):
    """御灵副本"""

    scene_name = "御灵副本"
    resource_path = "yuling"
    resource_list = [
        "title",  # 限时活动特征图像
        "start",  # 挑战
    ]

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    @staticmethod
    def description() -> None:
        logger.ui("""绘卷期间请减少使用""")

    def load_asset(self):
        self.IMAGE_TITLE = AssetImage(**get_asset(self.asset_image_list, "title"))
        self.IMAGE_START = AssetImage(**get_asset(self.asset_image_list, "start"))

    def run(self) -> None:
        self.check_title()
        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException
            
            sleep()
            # 开始
            self.check_click(self.IMAGE_START)
            # 结束
            self.check_finish()
            sleep()
            # 结算
            finish_random_left_right(is_multiple_drops_y=True)
            sleep()
            self.done()
            # TODO 强制等待，后续优化
            if self.n in {12, 25, 39, 59, 73}:
                logger.info("强制等待中，请稍等...")
                sleep(10, 20)
