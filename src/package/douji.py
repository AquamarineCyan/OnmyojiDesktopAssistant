from ..utils.adapter import Mouse
from ..utils.event import event_thread
from ..utils.exception import CustomException, GUIStopException
from ..utils.function import sleep
from ..utils.image import RuleImage
from ..utils.log import logger
from ..utils.paddleocr import RuleOcr, ocr_match_once
from .base_package import BasePackage


class DouJiScoreFullException(CustomException):
    """斗技分数已达名士"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_warn("异常捕获：斗技分数已达名士")


class DouJi(BasePackage):
    scene_name = "斗技"
    resource_path = "douji"

    def __init__(self, n: int = 0):
        super().__init__(n)
        self.current_score: int = 1000  # 当前分数

    @staticmethod
    def description():
        logger.ui("支持五段至名士之间的固定翻牌上阵")

    def load_asset(self):
        self.OCR_TITLE = self.get_ocr_asset("title")
        self.OCR_FIGHT = self.get_ocr_asset("fight")
        self.OCR_UPDATE_TEAM = self.get_ocr_asset("update_team")
        self.OCR_INTENTIONAL = self.get_ocr_asset("intentional")
        self.OCR_VICTORY = self.get_ocr_asset("victory")
        self.OCR_FAIL = self.get_ocr_asset("fail")
        self.OCR_LEVEL_UP = self.get_ocr_asset("level_up")

    def get_current_score(self):
        try:
            result = RuleOcr(region=(480, 370, 160, 100)).get_raw_result()
            for item in result:
                if "名士" in item.text:
                    self.current_score = 3000
                    break

                if "/" in item.text.strip():
                    current = item.text.split("/")[0]
                    self.current_score = int(current)
                    break

            logger.ui(f"当前分数: {self.current_score}")

        except Exception as e:
            logger.error(f"获取当前分数失败: {str(e)}")

        if self.current_score >= 3000:
            raise DouJiScoreFullException

    def fighting_once(self):
        _flag = False
        self.current_asset_list = [
            self.OCR_TITLE,
            self.OCR_FIGHT,
            self.OCR_UPDATE_TEAM,
            self.OCR_INTENTIONAL,
            self.OCR_VICTORY,
            self.OCR_FAIL,
        ]
        self.log_current_asset_list()

        while True:
            if bool(event_thread):
                raise GUIStopException

            sleep()
            result = ocr_match_once(self.current_asset_list)
            if result is None:
                ruleimage = RuleImage(self.global_assets.IMAGE_FAIL)
                if ruleimage.match():
                    logger.ui_warn("失败")
                    Mouse.click(ruleimage.center_point())
                    self.done()
                    return
                continue

            logger.info(f"current result name: {result.name}")
            match result.name:
                case self.OCR_TITLE.name:
                    logger.scene(self.scene_name)
                    msg_title = False
                    self.current_asset_list.remove(self.OCR_TITLE)

                    self.get_current_score()

                case self.OCR_FIGHT.name:
                    logger.ui("开始战斗")
                    if _flag:
                        continue
                    Mouse.click(result.match_result.center)
                    _flag = True
                    self.current_asset_list.remove(self.OCR_FIGHT)

                case self.OCR_UPDATE_TEAM.name:
                    logger.ui("自动上阵")
                    Mouse.click(result.match_result.center)
                    sleep(4)

                case self.OCR_INTENTIONAL.name:
                    logger.ui("手动技能")
                    Mouse.click(result.match_result.center)
                    sleep(4)

                # 万一对面直接退了呢
                case self.global_assets.OCR_CLICK_AND_CONTINUE.name:
                    logger.ui("点击屏幕继续")
                    Mouse.click(result.match_result.center)
                    self.done()
                    return

                case self.OCR_VICTORY.name:
                    logger.ui("胜利")
                    Mouse.click(result.match_result.center)
                    self.done()
                    return

                case self.OCR_FAIL.name:
                    logger.ui_warn("失败")
                    Mouse.click(result.match_result.center)
                    self.done()
                    return

                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False

    def run(self):
        weekly_rewards: int = 0
        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            self.fighting_once()
            sleep(4)

            # 周奖励
            if weekly_rewards < 3 and self.check_click(self.global_assets.IMAGE_FINISH, timeout=5):
                logger.ui("周奖励")
                weekly_rewards += 1

            if self.check_click(self.global_assets.IMAGE_CLOSE, timeout=5):
                logger.ui("段位上升")
