from ..utils.assets import AssetOcr
from ..utils.image import AssetImage
from ..utils.log import logger
from .utils import get_image_asset, get_ocr_asset, load_asset


class GlobalResource:
    """通用资源"""

    resource_path: str = "global"  # 路径
    resource_list: list = [
        "accept_invitation",  # 接受邀请
        "fail",  # 失败
        "finish",  # 结束
        "passenger_2",  # 队员2
        "passenger_3",  # 队员3
        "ready_new",  # 准备-简约主题
        "ready_old",  # 准备-怀旧主题
        "start_single",  # 单人挑战
        "start_team",  # 组队挑战
        "tanchigui",  # 贪吃鬼
        "victory",  # 成功
    ]

    def __init__(self):
        self.init: bool = False
        self.load_asset_list()
        try:
            self.load_asset()
            self.init = True
        except Exception as e:
            logger.error(f"{self.resource_path}/assets.json 资源加载失败：{e}")
            logger.ui_error(f"{self.resource_path}/assets.json 资源加载失败，请检查资源文件")

    def load_asset_list(self):
        self.asset_image_list = load_asset(self.resource_path, "image")
        self.asset_ocr_list = load_asset(self.resource_path, "ocr")

    def get_image_asset(self, name: str) -> AssetImage:
        return get_image_asset(self.asset_image_list, name)

    def get_ocr_asset(self, name: str) -> AssetOcr:
        return get_ocr_asset(self.asset_ocr_list, name)

    def load_asset(self):
        self.IMAGE_ACCEPT_INVITATION = self.get_image_asset("accept_invitation")
        self.IMAGE_CLOSE = self.get_image_asset("close")
        self.IMAGE_FAIL = self.get_image_asset("fail")
        self.IMAGE_FINISH = self.get_image_asset("finish")
        self.IMAGE_PASSENGER_2 = self.get_image_asset("passenger_2")
        self.IMAGE_PASSENGER_3 = self.get_image_asset("passenger_3")
        self.IMAGE_READY_NEW = self.get_image_asset("ready_new")
        self.IMAGE_READY_OLD = self.get_image_asset("ready_old")
        self.IMAGE_START_SINGLE = self.get_image_asset("start_single")
        self.IMAGE_START_TEAM = self.get_image_asset("start_team")
        self.IMAGE_SOUL_OVERFLOW = self.get_image_asset("soul_overflow")
        self.IMAGE_TANCHIGUI = self.get_image_asset("tanchigui")
        self.IMAGE_VICTORY = self.get_image_asset("victory")
        self.IMAGE_XIEZHANDUIWU = self.get_image_asset("xiezhanduiwu")

        self.OCR_AUTO_FIGHT = self.get_ocr_asset("auto_fight")
        self.OCR_CANCEL = self.get_ocr_asset("cancel")
        self.OCR_CONFIRM = self.get_ocr_asset("confirm")
        self.OCR_CLICK_AND_CONTINUE = self.get_ocr_asset("click_and_continue")
        self.OCR_START = self.get_ocr_asset("start")
