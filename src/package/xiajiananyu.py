from ..utils.function import finish_random_left_right, sleep
from ..utils.image import AssetImage
from ..utils.log import logger
from .base_package import BasePackage
from .types import XiaJianAnYuMode


class XiaJianAnYu(BasePackage):
    """狭间暗域"""

    scene_name = "狭间暗域"
    resource_path = "xiajiananyu"
    resource_list = [
        "baizangzhu_fujiang_left",  # 白藏主-副将左
        "baizangzhu_fujiang_right",  # 白藏主-副将右
        "baizangzhu_jingying_left",  # 白藏主-精英左
        "baizangzhu_jingying_middle",  # 白藏主-精英中
        "baizangzhu_jingying_right",  # 白藏主-精英右
        "baizangzhu_shouling",  # 白藏主-首领
        "goto",  # 前往
        "heibao_fujiang_left",  # 黑豹-副将左
        "heibao_fujiang_right",  # 黑豹-副将右
        "heibao_jingying_left",  # 黑豹-精英左
        "heibao_jingying_middle",  # 黑豹-精英中
        "heibao_jingying_right",  # 黑豹-精英右
        "heibao_shouling",  # 黑豹-首领
        "kongque_fujiang_left",  # 孔雀-副将左
        "kongque_fujiang_right",  # 孔雀-副将右
        "kongque_jingying_left",  # 孔雀-精英左
        "kongque_jingying_middle",  # 孔雀-精英中
        "kongque_jingying_right",  # 孔雀-精英右
        "kongque_shouling",  # 孔雀-首领
        "shenlong_fujiang_left",  # 神龙-副将左
        "shenlong_fujiang_right",  # 神龙-副将右
        "shenlong_jingying_left",  # 神龙-精英左
        "shenlong_jingying_middle",  # 神龙-精英中
        "shenlong_jingying_right",  # 神龙-精英右
        "shenlong_shouling",  # 神龙-首领
        "zhanbao",  # 战报
    ]

    def __init__(self, n: int = 0, mode: XiaJianAnYuMode = XiaJianAnYuMode.KONGQUE):
        super().__init__(n)
        self.mode: XiaJianAnYuMode = mode

    @staticmethod
    def description():
        logger.ui("按顺序点击首领-副将左-副将右-精英左-精英中-精英右。请提前锁定阵容，不支持自动退出战斗。")

    def load_asset(self):
        # 白藏主
        self.IMAGE_BAIZANGZHU_FUJIANG_LEFT = self.get_image_asset("baizangzhu_fujiang_left")
        self.IMAGE_BAIZANGZHU_FUJIANG_RIGHT = self.get_image_asset("baizangzhu_fujiang_right")
        self.IMAGE_BAIZANGZHU_JINGYING_LEFT = self.get_image_asset("baizangzhu_jingying_left")
        self.IMAGE_BAIZANGZHU_JINGYING_MIDDLE = self.get_image_asset("baizangzhu_jingying_middle")
        self.IMAGE_BAIZANGZHU_JINGYING_RIGHT = self.get_image_asset("baizangzhu_jingying_right")
        self.IMAGE_BAIZANGZHU_SHOULING = self.get_image_asset("baizangzhu_shouling")
        # 黑豹
        self.IMAGE_HEIBAO_FUJIANG_LEFT = self.get_image_asset("heibao_fujiang_left")
        self.IMAGE_HEIBAO_FUJIANG_RIGHT = self.get_image_asset("heibao_fujiang_right")
        self.IMAGE_HEIBAO_JINGYING_LEFT = self.get_image_asset("heibao_jingying_left")
        self.IMAGE_HEIBAO_JINGYING_MIDDLE = self.get_image_asset("heibao_jingying_middle")
        self.IMAGE_HEIBAO_JINGYING_RIGHT = self.get_image_asset("heibao_jingying_right")
        self.IMAGE_HEIBAO_SHOULING = self.get_image_asset("heibao_shouling")
        # 孔雀
        self.IMAGE_KONGQUE_FUJIANG_LEFT = self.get_image_asset("kongque_fujiang_left")
        self.IMAGE_KONGQUE_FUJIANG_RIGHT = self.get_image_asset("kongque_fujiang_right")
        self.IMAGE_KONGQUE_JINGYING_LEFT = self.get_image_asset("kongque_jingying_left")
        self.IMAGE_KONGQUE_JINGYING_MIDDLE = self.get_image_asset("kongque_jingying_middle")
        self.IMAGE_KONGQUE_JINGYING_RIGHT = self.get_image_asset("kongque_jingying_right")
        self.IMAGE_KONGQUE_SHOULING = self.get_image_asset("kongque_shouling")
        # 神龙
        self.IMAGE_SHENLONG_FUJIANG_LEFT = self.get_image_asset("shenlong_fujiang_left")
        self.IMAGE_SHENLONG_FUJIANG_RIGHT = self.get_image_asset("shenlong_fujiang_right")
        self.IMAGE_SHENLONG_JINGYING_LEFT = self.get_image_asset("shenlong_jingying_left")
        self.IMAGE_SHENLONG_JINGYING_MIDDLE = self.get_image_asset("shenlong_jingying_middle")
        self.IMAGE_SHENLONG_JINGYING_RIGHT = self.get_image_asset("shenlong_jingying_right")
        self.IMAGE_SHENLONG_SHOULING = self.get_image_asset("shenlong_shouling")
        # 通用
        self.IMAGE_ZHANBAO = self.get_image_asset("zhanbao")

        self.OCR_GOTO = self.get_ocr_asset("goto")

    def _targets(self) -> list[tuple[str, AssetImage]]:
        """按点击顺序返回所选暗域的 6 个目标"""
        parts = (
            ("shouling", "首领"),
            ("fujiang_left", "副将-左"),
            ("fujiang_right", "副将-右"),
            ("jingying_left", "精英-左"),
            ("jingying_middle", "精英-中"),
            ("jingying_right", "精英-右"),
        )
        return [
            (f"{self.mode.value}-{label}", getattr(self, f"IMAGE_{self.mode.name}_{part.upper()}"))
            for part, label in parts
        ]

    def fight_once(self, name: str, asset: AssetImage):
        logger.ui("正在打开战报")
        sleep()
        if not self.check_click(self.IMAGE_ZHANBAO, timeout=5):
            logger.ui_error("打开战报失败")
        sleep(2)

        logger.ui(f"正在点击{name}")
        if not self.check_click(asset, timeout=5):
            logger.ui_error(f"点击{name}失败")
            return
        sleep(2)

        logger.ui("正在前往")
        if not self.check_click(self.OCR_GOTO, timeout=5):
            logger.ui_warn("点击前往失败，可能已在当前暗域")
        sleep(2)

        logger.ui("正在弹窗确定")
        if not self.check_click(self.global_assets.OCR_CONFIRM, timeout=5):
            logger.ui_warn("点击确定超时，可能已在当前暗域")
        sleep(2)

        for i in range(3):
            if self.check_click(self.global_assets.OCR_START, timeout=5):
                logger.ui("点击挑战成功")
                break
            logger.ui_warn(f"点击挑战超时，重试第{i + 1}次")
            sleep(2)

        logger.ui("战斗中，等待结算")
        self.check_result()
        sleep(2)
        finish_random_left_right()
        sleep(2)

    def run(self):
        for name, asset in self._targets():
            self.fight_once(name, asset)
