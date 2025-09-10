from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException, TimesNotEnoughException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from ..utils.paddleocr import RuleOcr
from .utils import Package


class HuoDong(Package):
    """限时活动"""

    scene_name = "限时活动"
    resource_path = "huodong"

    # 两种结算方式
    STATE_NORMAL = 1  # 「达摩蛋」弹出
    STATE_RESULT = 2  # 「获得奖励」弹窗

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)
        self.flag_soul_overflow: bool = False
        self.state = None

    @staticmethod
    def description() -> None:
        logger.ui("限时活动，适配通用爬塔活动")

    def load_asset(self) -> None:
        self.IMAGE_RESULT = self.get_image_asset("result")

    def check_start(self) -> None:
        ruleocr = RuleOcr(self.global_assets.OCR_START)
        result = ruleocr.match()
        if result is None:
            return

        # 第一次检测到
        logger.ui("检测到挑战按钮")
        Mouse.click(result.center)
        sleep()
        for i in range(3):
            result = ruleocr.match()
            if result:
                logger.ui_warn(f"未进入，重试第{i + 1}次")
                Mouse.click(result.center)
                sleep()
            else:
                return
        logger.ui_error("重试3次后仍未进入，请检查")
        raise TimesNotEnoughException

    def run(self) -> None:
        self.current_asset_list = [
            self.IMAGE_RESULT,
            self.global_assets.IMAGE_FINISH,
            self.global_assets.IMAGE_FAIL,
            self.global_assets.IMAGE_VICTORY,
            self.global_assets.IMAGE_SOUL_OVERFLOW,
        ]
        _flag_title_msg: bool = True
        _flag_result_click: bool = False  # 部分活动会有“获得奖励”弹窗
        self.log_current_asset_list()
        _flag_done: bool = False

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            result = check_image_once(self.current_asset_list)
            if result is None:
                self.check_start()
                sleep()
                continue

            logger.info(f"current result name: {result.name}")
            match result.name:
                case self.IMAGE_RESULT.name:
                    self.state = self.STATE_RESULT
                    logger.ui("获得奖励")
                    finish_random_left_right(is_multiple_drops_x=True, is_multiple_drops_y=True)
                    self.done()
                    _flag_result_click = True
                    sleep(0.4, 0.8)

                case self.global_assets.IMAGE_FAIL.name:
                    logger.ui_error("失败")
                    break

                case self.global_assets.IMAGE_VICTORY.name:
                    logger.ui("胜利")
                    if _flag_result_click:
                        Mouse.click()
                        if not _flag_done:
                            self.done()
                            _flag_done = True
                        continue
                    sleep()

                case self.global_assets.IMAGE_FINISH.name:
                    logger.ui("结束")
                    sleep(0.4, 0.8)
                    _point = finish_random_left_right(is_multiple_drops_x=True, is_multiple_drops_y=True)
                    sleep()
                    if self.flag_soul_overflow:
                        sleep()

                    while True:
                        if bool(event_thread):
                            raise GUIStopException

                        # 先判断御魂上限提醒
                        result = RuleImage(self.global_assets.IMAGE_SOUL_OVERFLOW)
                        if result.match():
                            self.soul_overflow_warn_msg()
                            self.flag_soul_overflow = True
                            Mouse.click(result.center_point())
                            sleep()
                            continue

                        # 未重复检测到，表示成功点击
                        if not RuleImage(self.global_assets.IMAGE_FINISH).match():
                            break
                        Mouse.click(_point)

                    self.done()
                    sleep(3)

                case self.global_assets.IMAGE_SOUL_OVERFLOW.name:
                    self.soul_overflow_warn_msg()
                    self.flag_soul_overflow = True
                    Mouse.click(result.center_point())
                    sleep()

                case _:
                    if _flag_title_msg:
                        self.title_error_msg()
                        _flag_title_msg = False
