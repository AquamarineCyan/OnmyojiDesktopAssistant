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
        logger.ui("请提前在游戏内配置「结契设置」，鸣契石数量0表示不消耗石头，直接挑战场上的契灵")

    def load_asset(self):
        self.IMAGE_MINGQIZHAOHUAN = self.get_image_asset("mingqizhaohuan")
        self.IMAGE_STONE_ADD = self.get_image_asset("stone_add")
        self.IMAGE_STONE_MAX = self.get_image_asset("stone_max")
        self.IMAGE_ZHENMUSHOU = self.get_image_asset("zhenmushou")

        self.OCR_TANCHA_START = self.get_ocr_asset("tancha_start")
        self.OCR_TITLE = self.get_ocr_asset("title")
        self.OCR_ZHENMUSHOU = self.get_ocr_asset("zhenmushou")

    def done(self):
        self.stone_count += 1
        logger.ui(f"已使用鸣契石数量: {self.stone_count}")
        logger.progress(f"{self.stone_count}/{self.stone_numbers}")

    def check_jieqi_ready(self):
        result = RuleOcr().get_raw_result()
        for item in result:
            if item.text in ["契灵结契", "结契情报", "结契设置"]:
                logger.ui("结契准备就绪")
                return True
            if item.text in ["契灵之境", "鸣契召唤", "探查", "契忆商店"]:
                logger.ui("契灵地图")
                return False
        return None

    @log_function_call
    def fight_until_finish(self):
        """战斗，直到战胜当前契灵"""
        count = 0
        error = 0
        while True:
            if bool(event_thread):
                raise GUIStopException

            result = self.check_jieqi_ready()
            if result is False:
                return
            elif result is None:
                continue

            self.check_click(self.global_assets.OCR_START, timeout=3)
            sleep(2)
            for i in range(3):
                if self.check_click(self.global_assets.OCR_START, timeout=3):
                    error += 1
                    logger.ui_error(f"进入失败，重试第{i + 1}次")
                else:
                    break
            if error > 2:
                raise PokemonOverflowException("进入失败，可能契灵数量上限")

            error = 0
            if not self.check_finish(timeout=2 * 60):  # 排除阵容问题，只有成功或者超时
                # TODO 自动选其他罗盘
                raise LuopanEmptyException()
            sleep(3)
            finish_random_left_right()
            sleep(3)
            count += 1
            logger.ui(f"[镇墓兽]，第{count}次")

    @log_function_call
    def check_pokemon_remain(self):
        image = RuleImage(self.IMAGE_ZHENMUSHOU)
        if not image.match():
            logger.ui("未检测到剩余[镇墓兽]")
            return False

        logger.ui("剩余契灵[镇墓兽]")
        Mouse.click(image.center_point())
        sleep(2)
        self.fight_until_finish()

    @log_function_call
    def choose_stone_queding(self):
        result = RuleOcr().get_raw_result()
        for item in result:
            if item.text[-2:] == "鸣契":
                logger.ui("确定")
                Mouse.click(item.center)
                return True
        return False

    def choose_stone(self, number: int = 1):
        """选择鸣契石"""
        logger.ui("选择鸣契石[镇墓兽]")

        if not self.check_click(self.IMAGE_MINGQIZHAOHUAN, timeout=5, point_type="center"):
            logger.ui_warn("超时，未检测到鸣契石")
        sleep(2)

        if not self.check_click(self.OCR_ZHENMUSHOU, timeout=5):
            logger.ui_warn("超时，未检测到镇墓兽")
        sleep(2)

        if number == 99:
            if not self.check_click(self.IMAGE_STONE_MAX, timeout=5):
                logger.ui_warn("超时，未检测到最大值按钮")
                sleep(2)
        else:
            for _ in range(number - 1):
                if not self.check_click(self.IMAGE_STONE_ADD, timeout=5):
                    logger.ui_warn("超时，未检测到加号按钮")
                sleep()
        if not self.choose_stone_queding():
            logger.ui_warn("超时，未检测到鸣契按钮")
        sleep()

        # 2个以上的鸣契石，需要确认
        if number > 1 and not self.check_click(self.global_assets.OCR_CONFIRM, timeout=5):
            logger.ui_warn("超时，未检测到确认按钮")

        logger.ui("选择鸣契石[镇墓兽]成功")
        return True

    @log_function_call
    def tancha_task(self):
        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            self.check_click(self.OCR_TANCHA_START, timeout=3)
            sleep(3)  # 等待动画
            logger.ui("进入探查")
            for i in range(3):
                if not self.check_click(self.OCR_TANCHA_START, timeout=1):
                    break
                logger.ui_warn(f"尝试第{i + 1}次进入探查")
                sleep(3)  # 等待动画
            if i == 2:
                logger.ui_error("进入失败")
                return

            self.check_finish()
            sleep()
            finish_random_left_right()
            super().done()
            sleep(4)

    def jieqi_get_stone_numbers(self):
        """鸣契石数量"""
        result = RuleOcr().get_raw_result()
        for item in result:
            if "/30" in item.text:
                logger.ui(f"当前鸣契石：{item.text}")
                break

    def jieqi_task(self):
        """结契"""
        self.jieqi_get_stone_numbers()
        sleep(2)
        if self.stone_numbers == 0:
            logger.ui("没有鸣契石，跳过鸣契召唤任务")
        else:
            self.choose_stone(self.stone_numbers)
            sleep(4, 7)
        self.check_pokemon_remain()

    def run(self):
        self.check_title()
        if self.if_tancha:
            self.tancha_task()
        if self.if_jieqi:
            self.jieqi_task()
