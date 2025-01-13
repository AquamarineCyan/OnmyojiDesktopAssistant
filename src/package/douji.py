from ..utils.adapter import Mouse
from ..utils.assets import AssetOcr
from ..utils.event import event_thread
from ..utils.function import finish_random_left_right, sleep
from ..utils.log import logger
from ..utils.paddleocr import OcrData, check_raw_result_once, ocr, ocr_match_once
from .utils import Package, get_asset


class DouJi(Package):
    scene_name = "斗技"
    resource_path = "douji"

    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    def description() -> None:
        logger.ui("支持五段至名士之间的固定翻牌上阵")

    def load_asset(self):
        self.OCR_TITLE = AssetOcr(**get_asset(self.asset_ocr_list, "title"))
        self.OCR_FIGHT = AssetOcr(**get_asset(self.asset_ocr_list, "fight"))
        self.OCR_UPDATE_TEAM = AssetOcr(**get_asset(self.asset_ocr_list, "update_team"))
        self.OCR_INTENTIONAL = AssetOcr(**get_asset(self.asset_ocr_list, "intentional"))
        self.OCR_CONTINUE = AssetOcr(**get_asset(self.asset_ocr_list, "continue"))
        self.OCR_VICTORY = AssetOcr(**get_asset(self.asset_ocr_list, "victory"))
        self.OCR_FAIL = AssetOcr(**get_asset(self.asset_ocr_list, "fail"))

    def fight_once(self):
        _flag = False

        while True:
            if bool(event_thread):
                return

            sleep()
            result = ocr.get_raw_result()
            for item in result:
                ocr_data = OcrData(item)
                if ocr_data.score >= 0.8:
                    match ocr_data.text:
                        case "斗技" | "斗技赛":
                            _coor = ocr_data.rect.get_rela_center()
                            logger.ui(f"{ocr_data.text} {_coor.coor}")
                        case "战":
                            if _flag:
                                continue
                            _coor = ocr_data.rect.get_rela_center()
                            logger.ui(f"{ocr_data.text} {_coor.coor}")
                            Mouse.click(_coor)
                            _flag = True
                            break
                        case "上阵":
                            _coor = ocr_data.rect.get_rela_center()
                            logger.ui(f"{ocr_data.text} {_coor.coor}")
                            Mouse.click(_coor)
                            break
                        case "手动":
                            _coor = ocr_data.rect.get_rela_center()
                            logger.ui(f"{ocr_data.text} {_coor.coor}")
                            Mouse.click(_coor)
                            break
                        case "点击屏幕继续" | "胜利" | "失败":
                            _coor = ocr_data.rect.get_rela_center()
                            logger.ui(f"{ocr_data.text} {_coor.coor}")
                            Mouse.click(_coor)
                            self.done()
                            return

        while True:
            _ocr_data = check_raw_result_once("斗技")
            if _ocr_data:
                break
            _ocr_data = check_raw_result_once("斗技赛")
            if _ocr_data:
                break
            sleep()
        _coor = _ocr_data.rect.get_rela_center()
        logger.ui(f"斗技 {_coor.coor}")

        _ocr_data = check_raw_result_once("战")
        _coor = _ocr_data.rect.get_rela_center()
        logger.ui(f"战 {_coor.coor}")
        Mouse.click(_coor)

        sleep(3)

        # choice
        while True:
            _ocr_data = check_raw_result_once("自动")
            if _ocr_data:
                break
        _coor = _ocr_data.rect.get_rela_center()
        logger.ui(f"自动 {_coor.coor}")
        Mouse.click(_coor)

        sleep(3)

        # fighting
        while True:
            _ocr_data = check_raw_result_once("手动")
            if _ocr_data:
                break
        _coor = _ocr_data.rect.get_rela_center()
        logger.ui(f"手动 {_coor.coor}")
        Mouse.click(_coor)

        sleep(3)

        # wait finish
        while True:
            _ocr_data = check_raw_result_once("自动")
            if _ocr_data:
                sleep()
            else:
                break

        self.screenshot()
        # finish_random_left_right()
        while True:
            _ocr_data = check_raw_result_once("点击屏幕继续")
            if _ocr_data:
                break

        sleep()
        _coor = _ocr_data.rect.get_rela_center()
        logger.ui(f"点击屏幕继续 {_coor.coor}")
        Mouse.click(_coor)
        self.done()

    def fight_once_new(self):
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
                return
            sleep()
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
                return
            self.fight_once_new()
            sleep(2, 4)
            _ocr_data = check_raw_result_once("段位上升")
            if _ocr_data:
                _coor = _ocr_data.rect.get_rela_center()
                logger.ui(f"段位上升 {_coor.coor}")
                _coor.y += 200
                Mouse.click(_coor)
            self.check_click(self.OCR_CONTINUE, timeout=5)  # TODO need test
