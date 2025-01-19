from ..utils.adapter import Mouse
from ..utils.application import SCREENSHOT_DIR_PATH
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import random_num, random_point, sleep
from ..utils.image import RuleImage
from ..utils.log import logger
from ..utils.window import window
from .utils import Package


class BaiGuiYeXing(Package):
    """百鬼夜行"""

    scene_name = "百鬼夜行"
    resource_path = "baiguiyexing"
    resource_list = [
        "title",  # 标题
        "jinru",  # 进入
        "choose",  # 押选
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
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_JINRU = self.get_image_asset("jinru")
        self.IMAGE_CHOOSE = self.get_image_asset("choose")
        self.IMAGE_START = self.get_image_asset("kaishi")
        self.IMAGE_FINISH = self.get_image_asset("baiguiqiyueshu")

    def start(self):
        """开始"""
        self.check_click(self.IMAGE_JINRU, timeout=3)

    @log_function_call
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
                raise GUIStopException

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

            point = random_point(x1, x2, _y1, _y2)
            Mouse.click(point)
            sleep()
            if RuleImage(self.IMAGE_CHOOSE).match():
                logger.ui("已选择鬼王")
                break

        self.check_click(self.IMAGE_START, timeout=3)

    @log_function_call
    def fighting(self):
        """砸豆子"""
        sleep(4)  # 等待进入
        for _ in range(250, 0, -5):
            if bool(event_thread):
                raise GUIStopException

            sleep(0.2, 1)
            # 屏幕中心区域
            point = random_point(
                60,
                window.window_width - 120,
                300,
                window.window_height - 100,
            )
            Mouse.click(point, duration=0.25)

    @log_function_call
    def finish(self):
        """结束"""
        while True:
            if bool(event_thread):
                raise GUIStopException

            result = RuleImage(self.IMAGE_FINISH)
            if result.match():
                logger.ui("结束")
                point = result.random_point()
                sleep()
                if 1:  # TODO 可选
                    self.screenshot()
                    logger.ui("「百鬼契约书」已截图")
                Mouse.click(point)
                return

    def task_finish_info(self):
        logger.ui(f"截图保存在\n{SCREENSHOT_DIR_PATH / self.resource_path}")

    @log_function_call
    def run(self):
        self.check_title()
        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            self.start()
            sleep(2)
            self.choose()
            self.fighting()
            self.finish()
            self.done()
            sleep(3)
