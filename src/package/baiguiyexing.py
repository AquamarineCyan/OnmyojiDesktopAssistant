from ..utils.adapter import Mouse
from ..utils.application import SCREENSHOT_DIR_PATH
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import random_num, random_point, sleep
from ..utils.image import RuleImage
from ..utils.log import logger
from ..utils.point import Point
from ..utils.window import window_manager
from .base_package import BasePackage


class BaiGuiYeXing(BasePackage):
    """百鬼夜行"""

    scene_name = "百鬼夜行"
    resource_path = "baiguiyexing"
    resource_list = [
        "baiguiqiyueshu",  # 「百鬼契约书」
        "choose",  # 押选
        "jinru",  # 进入
        "kaishi",  # 开始
        "title",  # 标题
        "xingchongju_refresh",  # 星重聚刷新
        "yaoqing",  # 邀请好友
        "yaoqing_prompt",  # 邀请提示
    ]

    def __init__(self, n: int = 0, flag_screenshot: bool = False):
        super().__init__(n)
        self.flag_screenshot: bool = flag_screenshot

        logger.info(f"当前任务：{self.scene_name}")
        logger.info(f"任务总次数：{self.max}")
        logger.info(f"是否截图：{self.flag_screenshot}")

    @staticmethod
    def description():
        logger.ui("仅适用于快速清票。支持自动检测并邀请好友，自动押选鬼王（随机）。建议在开始前手动确认门票充足。")

    def load_asset(self):
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_JINRU = self.get_image_asset("jinru")
        self.IMAGE_CHOOSE = self.get_image_asset("choose")
        self.IMAGE_START = self.get_image_asset("kaishi")
        self.IMAGE_FINISH = self.get_image_asset("baiguiqiyueshu")
        self.IMAGE_XINGCHONGJU_REFRESH = self.get_image_asset("xingchongju_refresh")
        self.IMAGE_YAOQING = self.get_image_asset("yaoqing")
        self.IMAGE_YAOQING_PROMPT = self.get_image_asset("yaoqing_prompt")

    def start(self):
        """开始"""
        self.check_click(self.IMAGE_JINRU, timeout=3)

    def yaoqing(self):
        """邀请好友"""
        # 检查是否已经邀请过
        rule_image = RuleImage(self.IMAGE_YAOQING)
        result = rule_image.match(logger_lever="ERROR")

        if not result:
            logger.ui_error("未发现邀请按钮")
            return

        logger.ui("点击邀请好友")
        Mouse.click(rule_image.center_point())
        sleep(2)

        # 在好友列表中选择好友
        friend_slots = [
            Point(300, 250),  # 第一个
            Point(650, 250),  # 第二个
        ]

        # 邀请星重聚对象
        image_prompt = RuleImage(self.IMAGE_YAOQING_PROMPT)
        image_xingchongju = RuleImage(self.IMAGE_XINGCHONGJU_REFRESH)
        if image_xingchongju.match():
            x1, y1, x2, y2 = image_xingchongju.match_result
            logger.ui("点击确认邀请星重聚对象")
            target_point = Point(int((x1 + x2) / 2), int((y1 + y2) / 2))
            Mouse.click(target_point)
            target_point2 = Point(int((x1 + x2) / 2 + 25), int((y1 + y2) / 2 + 50))
            Mouse.click(target_point2)
            sleep(1)
        elif image_prompt.match():
            x1, y1, x2, y2 = image_prompt.match_result
            logger.ui("点击确认邀请好友")
            target_point = Point(int((x1 + x2) / 2) + 60, int((y1 + y2) / 2) + 55)
            Mouse.click(target_point)
            sleep(1)
        else:
            for i, slot in enumerate(friend_slots):
                logger.ui(f"尝试邀请第 {i + 1} 个位置的好友")
                Mouse.click(slot)

    @log_function_call
    def choose(self):
        """鬼王选择"""
        _x1_left, _x1_right = 230, 260
        _x2_left, _x2_right = 560, 590
        _x3_left, _x3_right = 880, 910
        _y1, _y2 = 300, 550
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
                logger.ui("已随机选择鬼王")
                break

        self.check_click(self.IMAGE_START, timeout=3)

    @log_function_call
    def fighting(self):
        """砸豆子"""
        sleep(4)  # 等待进入
        i = 1
        for beans_left in range(600, 0, -5):
            if bool(event_thread):
                raise GUIStopException

            sleep_max = max(0.3, (beans_left - 4 * i) / 600.0)
            i += 1
            sleep(0.15, sleep_max)
            # 屏幕中心区域
            point = random_point(
                60,
                window_manager.current.client_width - 120,
                300,
                window_manager.current.client_height - 100,
            )
            Mouse.click(point, duration=0.25)
            result = RuleImage(self.IMAGE_FINISH)
            if result.match():
                logger.ui("豆子已砸完")
                break
            result2 = RuleImage(self.IMAGE_JINRU)
            if result2.match():
                logger.ui("结束")
                break

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
                sleep(2)
                if self.flag_screenshot:
                    self.screenshot()
                    logger.ui("「百鬼契约书」已截图")
                Mouse.click(point)
                return

            result2 = RuleImage(self.IMAGE_JINRU)
            if result2.match():
                logger.ui("结束")
                return

    def task_finish_info(self):
        if self.flag_screenshot:
            logger.ui(f"截图保存在\n{SCREENSHOT_DIR_PATH / self.resource_path}")

    @log_function_call
    def run(self):
        self.check_title()
        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException
            self.yaoqing()
            self.start()
            sleep(2)
            self.choose()
            self.fighting()
            self.done()
            sleep(2)
            self.finish()
