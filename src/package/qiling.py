from ..utils.adapter import Mouse
from ..utils.assets import AssetImage
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from ..utils.mythread import WorkTimer
from ..utils.paddleocr import RuleOcr
from .utils import Package, get_asset


class LuopanEmptyException(Exception):
    """指定罗盘不足"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：指定罗盘不足")


class PokemonOverflowException(Exception):
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
    image_keys = {
        "mingqizhaohuan": "IMAGE_MINGQIZHAOHUAN",
        "queding": "IMAGE_QUEDING",
        "start_jieqi": "IMAGE_START_JIEQI",
        "start_tancha": "IMAGE_START_TANCHA",
        "title": "IMAGE_TITLE",
        "zhenmushou": "IMAGE_ZHENMUSHOU",
        "zhenmushou_mingqishi": "IMAGE_ZHENMUSHOU_MINGQISHI",
    }

    map_pockmon_max: int = 5

    @log_function_call
    def __init__(
        self,
        n: int = 0,
        _flag_tancha: bool = True,
        _flag_jieqi: bool = False,
        _stone_pokemon: str = None,
        _stone_numbers: int = 0,
    ) -> None:
        super().__init__(n)
        self._flag_tancha = _flag_tancha
        self._flag_jieqi = _flag_jieqi
        self._stone_pokemon = _stone_pokemon  # 指定鸣契石，目前仅支持镇墓兽
        self._stone_numbers = _stone_numbers  # 使用鸣契石数量
        self._flag_finish: bool = False
        self._stone_count: int = 0  # 已使用鸣契石数量

    def description() -> None:
        logger.ui("次数为探查次数，选中“结契”按钮将在探查结束后自动挑战场上所有，请提前在游戏内配置“结契设置”")

    def load_asset(self):
        if self.asset_image_list is None:
            logger.ui_error("发生错误，请先加载资源")
            return
        for key, sttr_name in self.image_keys.items():
            setattr(
                self, sttr_name, AssetImage(**get_asset(self.asset_image_list, key))
            )
        return

    def done(self):
        self._stone_count += 1
        logger.ui(f"已使用鸣契石数量: {self._stone_count}")
        logger.num(f"{self._stone_count}/{self._stone_numbers}")

    @log_function_call
    def fighting(self):
        _flag_first: bool = False
        while True:
            if bool(event_thread):
                raise GUIStopException
            
            if self._flag_finish:
                return
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
                logger.ui_error("指定罗盘不足")  # TODO 自动选其他罗盘
                raise LuopanEmptyException("指定罗盘不足")
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
    def timer_start(self):
        if RuleImage(self.IMAGE_START_TANCHA).match():
            self._flag_finish = True

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

    def choose_stoen(self):
        """选择鸣契石"""
        logger.ui("选择鸣契石[镇墓兽]")
        if not self.check_click(
            self.IMAGE_MINGQIZHAOHUAN, timeout=5, point_type="center"
        ):
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
        self.current_asset_list = [
            self.IMAGE_TITLE,
            self.IMAGE_START_TANCHA,
        ]
        self.log_current_asset_list()

        while self.n < self.max:
            if bool(event_thread):
                return
            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            match result.name:
                case "title":
                    logger.scene("契灵之境")
                case "start_tancha":
                    WorkTimer(5, self.timer_start).start()
                    Mouse.click(result.center_point())
                    sleep()
                    self.fighting()
                    self.done()
                    sleep(2, 4)
            if self._flag_finish:
                logger.ui("场上最多存在5只契灵，请及时清理")
                break

    def run_jieqi(self):
        """结契"""
        # TODO 需要先识别主场景
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

        while self._stone_count < self._stone_numbers:
            if bool(event_thread):
                raise GUIStopException

            self.choose_stoen()
            sleep(4, 7)
            self.check_pokemon_remain()
            continue

    def run(self):
        try:
            if self._flag_tancha:
                self.run_tancha()
            if self._flag_jieqi:
                self.run_jieqi()
        except Exception as e:
            logger.error(e)
