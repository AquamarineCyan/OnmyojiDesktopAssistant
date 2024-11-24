from ..utils.adapter import Mouse
from ..utils.assets import AssetImage
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from ..utils.mythread import WorkTimer
from ..utils.point import RelativePoint
from .utils import Package, get_asset


class QiLing(Package):
    """契灵"""

    scene_name = "契灵"
    resource_path = "qiling"
    resource_list: list = [
        "title",
        "start_tancha",
        "start_jieqi",
        "mingqizhaohuan",
        "queding",
    ]
    description = "次数为探查次数，选中“结契”按钮将在探查结束后自动挑战场上所有，地图最多支持刷出5只契灵，请提前在游戏内配置“结契设置”"

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
        self._stone_pokemon = _stone_pokemon
        self._stone_numbers = _stone_numbers
        self._flag_finish: bool = False
        self._flag_timer_jieqi_finish: bool = True
        self._pokemon_address_count: int = 0
        self._stone_count: int = 0

    def load_asset(self):
        self.IMAGE_MINGQIZHAOHUAN = AssetImage(
            **get_asset(self.asset_image_list, "mingqizhaohuan")
        )
        self.IMAGE_QUEDING = AssetImage(**get_asset(self.asset_image_list, "queding"))
        self.IMAGE_START_TANCHA = AssetImage(
            **get_asset(self.asset_image_list, "start_tancha")
        )
        self.IMAGE_START_JIEQI = AssetImage(
            **get_asset(self.asset_image_list, "start_jieqi")
        )
        self.IMAGE_TITLE = AssetImage(**get_asset(self.asset_image_list, "title"))

    @log_function_call
    def fighting(self):
        _flag_first: bool = False
        while True:
            if bool(event_thread):
                return
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

    @log_function_call
    def timer_start(self):
        if RuleImage(self.IMAGE_START_TANCHA).match():
            self._flag_finish = True

    @log_function_call
    def summon_pokemon(self):
        pokemon_list = [
            RelativePoint(160, 360),
            RelativePoint(400, 360),
            RelativePoint(650, 360),
            RelativePoint(880, 360),
        ]
        if self._stone_pokemon == "镇墓兽":
            pokemon_point = pokemon_list[3]
        for _ in range(self._stone_numbers - self._stone_count):
            self.check_click(self.IMAGE_MINGQIZHAOHUAN)
            sleep()
            if RuleImage(self.IMAGE_MINGQIZHAOHUAN).match():
                logger.ui_warn("场上最多5只契灵")
                return
            Mouse.click(pokemon_point)
            sleep(0.4, 0.8)
            self.check_click(self.IMAGE_QUEDING)
            self._stone_count += 1
            logger.ui(f"已使用鸣契石数量: {self._stone_count}")
            sleep(3)

    @log_function_call
    def check_pokemon(self) -> bool:
        """判断5个契灵小图标的固定点位"""
        pokemon_list = [
            RelativePoint(220, 528),
            RelativePoint(378, 485),
            RelativePoint(635, 505),
            RelativePoint(815, 484),
            RelativePoint(935, 490),
        ]
        # 遍历5个固定点位
        for i in range(self._pokemon_address_count, 5):
            logger.info(f"_pokemon_address_count: {self._pokemon_address_count}")
            Mouse.click(pokemon_list[i])
            self._pokemon_address_count += 1
            sleep(2)
            if RuleImage(self.IMAGE_START_JIEQI).match():
                return True
            else:
                continue
        return False

    @log_function_call
    def timer_jieqi_finish(self):
        if not RuleImage(self.global_image.IMAGE_FINISH).match():
            self._flag_timer_jieqi_finish = False

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

    @log_function_call
    def catch_pokemon(self):
        _n: int = 0
        self.current_asset_list = [
            self.IMAGE_TITLE,
            self.IMAGE_START_JIEQI,
        ]
        _flag_done_once: bool = False

        while _n <= 5:
            if bool(event_thread):
                return
            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            match result:
                # 确保在探查界面点击契灵小图标
                case "title":
                    logger.scene("契灵之境")
                    if _flag_done_once:
                        _flag_done_once = False
                        _n += 1
                        logger.ui(f"结契第{_n}只成功")
                    if not self.check_pokemon():
                        break
                    sleep()
                    continue
                case "start_jieqi":
                    logger.scene("结契")
                    Mouse.click(result.center_point())
                    sleep(10)
                    _flag_first: bool = False
                    _timer = WorkTimer(2 * 60, self.timer_jieqi_finish)
                    _timer.start()

                    while True:
                        if not self._flag_timer_jieqi_finish:
                            # TODO 需要识别其他罗盘点击
                            logger.ui_warn("没有足够的指定的罗盘")

                        if self.check_finish():
                            _flag_first = True
                            _timer.cancel()
                            sleep(0.5, 0.8)
                            finish_random_left_right()
                        elif _flag_first:
                            _flag_done_once = True
                            sleep(2)
                            break

    def run_jieqi(self):
        """结契"""
        while self._stone_count <= self._stone_numbers:
            self.summon_pokemon()
            self.catch_pokemon()

    def run(self):
        if self._flag_tancha:
            self.run_tancha()
        if self._flag_jieqi:
            self.run_jieqi()
