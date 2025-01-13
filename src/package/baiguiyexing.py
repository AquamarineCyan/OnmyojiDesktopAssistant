from ..utils.adapter import Mouse
from ..utils.assets import AssetImage
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import random_num, random_point, sleep
from ..utils.image import RuleImage
from ..utils.log import logger
from ..utils.point import RelativePoint
from ..utils.window import window
from .utils import Package, get_asset


class BaiGuiYeXing(Package):
    """百鬼夜行"""

    scene_name = "百鬼夜行"
    resource_path = "baiguiyexing"
    resource_list = [
        "title",  # 标题
        "jinru",  # 进入
        "ya",  # 押选
        "kaishi",  # 开始
        "baiguiqiyueshu",  # 百鬼契约书
    ]

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    @staticmethod
    def description() -> None:
        logger.ui("仅适用于清票，无法指定鬼王")

    def load_asset(self):
        self.IMAGE_TITLE = AssetImage(**get_asset(self.asset_image_list, "title"))
        self.IMAGE_JINRU = AssetImage(**get_asset(self.asset_image_list, "jinru"))
        self.IMAGE_CHOOSE = AssetImage(**get_asset(self.asset_image_list, "choose"))
        self.IMAGE_START = AssetImage(**get_asset(self.asset_image_list, "kaishi"))
        self.IMAGE_FINISH = AssetImage(
            **get_asset(self.asset_image_list, "baiguiqiyueshu")
        )

    def start(self):
        """开始"""
        self.check_click(self.IMAGE_JINRU)

    def choose(self):
        """鬼王选择"""
        _x1_left = 230
        _x1_right = 260
        _x2_left = 560
        _x2_right = 590
        _x3_left = 880
        _x3_right = 910
        _y1 = 300
        _y2 = 550
        while True:
            if bool(event_thread):
                return
            m = random_num(1, 4)
            if m < 2:
                x1 = _x1_left
                x2 = _x1_right
            elif m < 3:
                x1 = _x2_left
                x2 = _x2_right
            else:
                x1 = _x3_left
                x2 = _x3_right

            point: RelativePoint = random_point(x1, x2, _y1, _y2)
            Mouse.click(point)
            sleep()
            if RuleImage(self.IMAGE_CHOOSE).match():
                logger.ui("已选择鬼王")
                break

        self.check_click(self.IMAGE_START)

    def fighting(self):
        """砸豆子"""
        sleep()
        for _ in range(250, 0, -5):
            if bool(event_thread):
                return
            sleep(0.2, 1)
            point: RelativePoint = random_point(
                60,
                window.window_width - 120,
                300,
                window.window_height - 100,
            )
            Mouse.click(point, duration=0.25)

    def finish(self):
        """结束"""
        while True:
            if bool(event_thread):
                return
            result = RuleImage(self.IMAGE_FINISH)
            if result.match():
                point = result.random_point()
                sleep()
                self.screenshot()
                Mouse.click(point)

    def finish_info(self):
        logger.ui(f"截图保存在{SCREENSHOT_DIR_PATH / self.resource_path}")

    def run(self):
        self.check_title()
        while self.n < self.max:
            if bool(event_thread):
                return
            sleep()
            self.start()
            sleep(2)
            self.choose()
            sleep(2, 4)
            self.fighting()
            sleep(2, 4)
            self.finish()
            self.done()
            sleep(3)

            # TODO 更新随机判断
            if self.n in {12, 25, 39}:
                sleep(10, 20)
