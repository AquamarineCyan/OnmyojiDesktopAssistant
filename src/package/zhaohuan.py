from ..utils.adapter import Mouse
from ..utils.assets import AssetOcr
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import sleep
from ..utils.log import logger
from ..utils.paddleocr import RuleOcr
from .utils import Package, get_asset


class ZhaoHuan(Package):
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
        try:
            self.OCR_TITLE = AssetOcr(**get_asset(self.asset_ocr_list, "title"))
            self.OCR_ZHAOHUAN = AssetOcr(**get_asset(self.asset_ocr_list, "zhaohuan"))
            self.OCR_QUEDING = AssetOcr(**get_asset(self.asset_ocr_list, "queding"))
            self.OCR_AGAIN = AssetOcr(**get_asset(self.asset_ocr_list, "again"))
        except Exception as e:
            logger.error(f"{self.resource_path}/assets.json 资源加载失败：{e}")
            logger.ui_error(
                f"{self.resource_path}/assets.json 资源加载失败，请检查资源文件"
            )
            return

    @staticmethod
    def description() -> None:
        logger.ui("普通召唤，请选择十连次数，请选择合适的召唤屋")

    def check_first_times(self):
        ocr = RuleOcr(self.OCR_ZHAOHUAN)
        while True:
            if bool(event_thread):
                return
            if result := ocr.match():
                point = result.center
                point.y -= 50
                Mouse.click(point)
                return

    def run(self) -> None:
        self.check_title()
        logger.num(f"0/{self.max}")
        self.check_first_times()
        self.done() 
        sleep(4, 6)
        while self.n < self.max:
            if bool(event_thread):
                return
            if self.max == 1:
                break
            self.check_click(self.OCR_AGAIN)
            self.done()
            sleep(4, 6)
        self.check_click(self.OCR_QUEDING)
