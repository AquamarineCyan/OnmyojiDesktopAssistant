from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import sleep
from ..utils.log import logger
from ..utils.paddleocr import RuleOcr
from .base_package import BasePackage


class ZhaoHuan(BasePackage):
    """普通召唤"""

    scene_name = "普通召唤"
    resource_path = "zhaohuan"
    resource_list = [
        "putongzhaohuan",  # 普通召唤
        "queding",  # 确定
        "title",  # 标题
        "zaicizhaohuan",  # 再次召唤
    ]

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    @staticmethod
    def description() -> None:
        logger.ui("普通召唤，请选择十连次数，请选择合适的召唤屋")

    def load_asset(self):
        self.OCR_TITLE = self.get_ocr_asset("title")
        self.OCR_ZHAOHUAN = self.get_ocr_asset("zhaohuan")
        self.OCR_QUEDING = self.get_ocr_asset("queding")
        self.OCR_AGAIN = self.get_ocr_asset("again")

    def check_first_times(self):
        ocr = RuleOcr(self.OCR_ZHAOHUAN)
        while True:
            if bool(event_thread):
                raise GUIStopException

            if result := ocr.match():
                point = result.center
                point.set_y(-50)
                Mouse.click(point)
                return

    def run(self) -> None:
        self.check_title()
        self.check_first_times()
        self.done()
        sleep(4, 6)
        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            if self.max == 1:
                break
            self.check_click(self.OCR_AGAIN)
            self.done()
            sleep(4, 6)
        self.check_click(self.OCR_QUEDING)
