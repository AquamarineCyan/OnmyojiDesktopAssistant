from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import CustomException, GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage
from ..utils.log import logger
from ..utils.paddleocr import RuleOcr
from .utils import Package


class LuopanEmptyException(CustomException):
    """指定罗盘不足"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：指定罗盘不足")


class PokemonOverflowException(CustomException):
    """契灵数量上限"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：契灵数量上限")


class QiLing(Package):
    """契灵"""

    scene_name = "契灵"
    resource_path = "qiling"
    resource_list: list = [
        "mingqizhaohuan",
        "queding",
        "start_jieqi",
        "start_tancha",
        "title",
        "zhenmushou",
        "zhenmushou_mingqishi",
    ]

    map_pockmon_max: int = 5

    @log_function_call
    def __init__(
        self,
        n: int = 0,
        if_tancha: bool = False,
        if_jieqi: bool = True,
        stone_pokemon: str = None,
        stone_numbers: int = 0,
    ) -> None:
        super().__init__(n)
        self.if_tancha = if_tancha
        self.if_jieqi = if_jieqi
        self.stone_pokemon = stone_pokemon  # 指定鸣契石，目前仅支持镇墓兽
        self.stone_numbers = stone_numbers  # 使用鸣契石数量
        self.stone_count: int = 0  # 已使用鸣契石数量

    def description() -> None:
        logger.ui("选中“结契”按钮将自动挑战场上剩余契灵，请提前在游戏内配置“结契设置”")

    def load_asset(self):
        self.IMAGE_MINGQIZHAOHUAN = self.get_image_asset("mingqizhaohuan")
        self.IMAGE_QUEDING = self.get_image_asset("queding")
        self.IMAGE_START_JIEQI = self.get_image_asset("start_jieqi")
        self.IMAGE_START_TANCHA = self.get_image_asset("start_tancha")
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_ZHENMUSHOU = self.get_image_asset("zhenmushou")
        self.IMAGE_ZHENMUSHOU_MINGQISHI = self.get_image_asset("zhenmushou_mingqishi")

    def done(self):
        self.stone_count += 1
        logger.ui(f"已使用鸣契石数量: {self.stone_count}")
        logger.num(f"{self.stone_count}/{self.stone_numbers}")

    @log_function_call
    def fight_tancha(self):
        _flag_first: bool = False
        while True:
            if bool(event_thread):
                raise GUIStopException

            if self.check_finish():
                _flag_first = True
                sleep(0.5, 0.8)
                finish_random_left_right()
            elif _flag_first:
                sleep(0.3, 0.5)
                return
            sleep(0.3, 0.5)

    def fight_until_finish(self, _done: bool = True):
        """战斗，直到战胜当前契灵"""
        _n = 0
        _error = 0
        while True:
            self.check_click(self.IMAGE_START_JIEQI, timeout=5)
            sleep(3)
            if RuleImage(self.IMAGE_START_JIEQI).match():
                logger.ui_error(f"进入失败，重试第{_error}次")
                if _error > 2:
                    raise PokemonOverflowException("进入失败，可能契灵数量上限")
                _error += 1
                continue

            _error = 0
            if not self.check_finish(timeout=2 * 60):  # 排除阵容问题，只有成功或者超时
                # TODO 自动选其他罗盘
                raise LuopanEmptyException()
            sleep(3)
            finish_random_left_right()
            sleep(3)
            if not RuleImage(self.IMAGE_START_JIEQI).match():
                logger.ui("[镇墓兽]结束")
                if _done:
                    self.done()
                return True
            _n += 1
            logger.ui(f"[镇墓兽]继续，第{_n}次")

    @log_function_call
    def check_pokemon_remain(self, _done: bool = True):
        image = RuleImage(self.IMAGE_ZHENMUSHOU)
        if not image.match():
            logger.ui("未检测到剩余契灵")
            return False

        logger.ui("剩余契灵[镇墓兽]")
        Mouse.click(image.center_point())
        sleep(2)
        return self.fight_until_finish(_done)

    def choose_stone(self):
        """选择鸣契石"""
        logger.ui("选择鸣契石[镇墓兽]")
        if not self.check_click(self.IMAGE_MINGQIZHAOHUAN, timeout=5, point_type="center"):
            logger.ui_warn("超时，未检测到鸣契石")
        if not self.check_click(self.IMAGE_ZHENMUSHOU_MINGQISHI, timeout=5):
            logger.ui_warn("超时，未检测到镇墓兽")
        if not self.check_click(self.IMAGE_QUEDING, timeout=5):
            logger.ui_warn("超时，未检测到确认按钮")
            return False

        logger.ui("选择鸣契石[镇墓兽]成功")
        return True

    @log_function_call
    def run_tancha(self):
        self.check_title()

        self.current_asset_list = [
            self.IMAGE_TITLE,
            self.IMAGE_START_TANCHA,
        ]
        self.log_current_asset_list()

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            self.check_click(self.IMAGE_START_TANCHA, timeout=3)
            sleep(3)  # 等待动画
            logger.ui("进入探查")
            for i in range(3):
                if not self.check_click(self.IMAGE_START_TANCHA, timeout=1):
                    break
                logger.ui_warn(f"尝试第{i + 1}次进入探查")
                sleep(3)  # 等待动画
            if i == 2:
                logger.ui_error("进入失败，可能原因是场上最多存在5只契灵，请及时清理")
                return

            self.check_finish()
            sleep()
            finish_random_left_right()
            super().done()
            sleep(4)

    def run_jieqi(self):
        """结契"""
        self.check_title()

        result = RuleOcr().get_raw_result()
        for item in result:
            logger.info(item.text)
            if "/30" in item.text:
                logger.ui(f"鸣契石：{item.text}")

        while True:
            if bool(event_thread):
                raise GUIStopException

            if not self.check_pokemon_remain(False):
                break

        while self.stone_count < self.stone_numbers:
            if bool(event_thread):
                raise GUIStopException

            self.choose_stone()
            sleep(4, 7)
            self.check_pokemon_remain()
            continue

    def run(self):
        if self.if_tancha:
            self.run_tancha()
        if self.if_jieqi:
            self.run_jieqi()
