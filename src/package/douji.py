from ..utils.adapter import Mouse
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import sleep
from ..utils.log import logger
from ..utils.paddleocr import OcrData, check_raw_result_once, ocr, ocr_match_once
from .utils import Package


class DouJi(Package):
    scene_name = "斗技"
    resource_path = "douji"

    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    def description() -> None:
        logger.ui("支持五段至名士之间的固定翻牌上阵")

    def load_asset(self):
        self.OCR_TITLE = self.get_ocr_asset("title")
        self.OCR_FIGHT = self.get_ocr_asset("fight")
        self.OCR_UPDATE_TEAM = self.get_ocr_asset("update_team")
        self.OCR_INTENTIONAL = self.get_ocr_asset("intentional")
        self.OCR_CONTINUE = self.get_ocr_asset("continue")
        self.OCR_VICTORY = self.get_ocr_asset("victory")
        self.OCR_FAIL = self.get_ocr_asset("fail")
        self.OCR_LEVEL_UP = self.get_ocr_asset("level_up")

    def fighting_once(self):
        _flag = False
        self.current_asset_list = [
            self.OCR_TITLE,
            self.OCR_FIGHT,
            self.OCR_UPDATE_TEAM,
            self.OCR_INTENTIONAL,
            self.OCR_CONTINUE,
            self.OCR_VICTORY,
            self.OCR_FAIL,
        ]
        self.log_current_asset_list()

        while True:
            if bool(event_thread):
                raise GUIStopException

            result = ocr_match_once(self.current_asset_list)
            if result is None:
                continue

            logger.info(f"current result name: {result.name}")
            match result.name:
                case "title":
                    logger.scene(self.scene_name)
                    msg_title = False
                    # self.check_click(self.OCR_FIGHT, timeout=5)
                    self.current_asset_list.remove(self.OCR_TITLE)
                case "fight":
                    logger.ui("开始战斗")
                    if _flag:
                        continue
                    Mouse.click(result.match_result.center)
                    _flag = True
                    self.current_asset_list.remove(self.OCR_FIGHT)
                case "update_team":
                    logger.ui("自动上阵")
                    Mouse.click(result.match_result.center)
                case "intentional":
                    logger.ui("手动技能")
                    Mouse.click(result.match_result.center)

                case "continue":
                    logger.ui("点击屏幕继续")
                    Mouse.click(result.match_result.center)
                    self.done()
                    return
                case "victory":
                    logger.ui("胜利")
                    Mouse.click(result.match_result.center)
                    self.done()
                    return
                case "fail":
                    logger.ui_warn("失败")
                    Mouse.click(result.match_result.center)
                    self.done()
                    return
                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False

    def run(self):
        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            self.fight_once_new()
            sleep(2, 4)
            _ocr_data = check_raw_result_once("段位上升")
            if _ocr_data:
                _coor = _ocr_data.rect.get_rela_center()
                logger.ui(f"段位上升 {_coor.coor}")
                _coor.y += 200
                Mouse.click(_coor)
            self.check_click(self.OCR_CONTINUE, timeout=5)  # TODO need test
