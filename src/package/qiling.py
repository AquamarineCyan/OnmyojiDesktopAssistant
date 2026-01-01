from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import CustomException, GUIStopException, TimesNotEnoughException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage
from ..utils.log import logger
from ..utils.paddleocr import RuleOcr
from ..utils.point import Point
from .base_package import BasePackage


class LuopanEmptyException(CustomException):
    """指定罗盘不足"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：指定罗盘不足")


class QiLing(BasePackage):
    """契灵"""

    scene_name = "契灵"
    resource_path = "qiling"

    pockmon_mapping = {
        "镇墓兽": (220, 450),
        "火灵": (400, 480),
        "茨球": (620, 440),
        "小黑": (850, 450),
        "针女": (220, 450),
        "薙魂": (400, 480),
        "月魔兔": (620, 440),
        "狐火": (850, 450),
    }

    @classmethod
    def get_pockmon_list(cls) -> list[str]:
        """返回契灵列表"""
        return list(cls.pockmon_mapping.keys())

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
        self.if_jieqi_give_up: bool = True  # 手动放弃结契
        self.stone_pokemon = stone_pokemon  # 指定鸣契石
        self.stone_numbers = stone_numbers  # 使用鸣契石数量

    @staticmethod
    def description() -> None:
        logger.ui("请提前配置「结契设置」，鸣契石数量0表示不消耗石头，直接挑战场上的契灵，取消勾选「连续结契」")
        # TODO 连续10次结契失败只能手动放弃

    def load_asset(self):
        self.IMAGE_STONE_ADD = self.get_image_asset("stone_add")
        self.IMAGE_STONE_MAX = self.get_image_asset("stone_max")
        self.IMAGE_ZHAOHUAN = self.get_image_asset("zhaohuan")

        self.OCR_TANCHA_START = self.get_ocr_asset("tancha_start")
        self.OCR_TITLE = self.get_ocr_asset("title")
        self.OCR_JIEQI_GIVE_UP = self.get_ocr_asset("jieqi_give_up")

    def check_jieqi_ready(self) -> bool | None:
        result = RuleOcr().get_raw_result()
        for item in result:
            if item.text in ["契灵结契", "结契情报", "结契设置"]:
                logger.ui("结契准备就绪")
                return True
            if item.text in ["契灵之境", "鸣契召唤", "探查", "契忆商店"]:
                logger.ui("契灵地图")
                return False
        return None

    def check_result(self, times: int = 30) -> bool:
        for _ in range(times):
            if bool(event_thread):
                raise GUIStopException

            result = RuleOcr().get_raw_result()
            for item in result:
                if item.text == self.OCR_JIEQI_GIVE_UP.keyword:
                    logger.ui("放弃结契")
                    Mouse.click(item.center)
                    return
            # 只检测，不点击
            if RuleImage(self.global_assets.IMAGE_FINISH).match():
                logger.ui("战斗结束")
                return

            sleep(3)

        raise LuopanEmptyException()

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
            logger.ui("开始挑战")
            sleep(2)
            for i in range(3):
                if self.check_click(self.global_assets.OCR_START, timeout=3):
                    error += 1
                    logger.ui_error(f"进入失败，重试第{i + 1}次")
                else:
                    break
            if error > 2:
                raise TimesNotEnoughException()

            error = 0

            if self.if_jieqi_give_up:  # 手动放弃结契
                self.check_result(3 * 60)
                sleep(3)

            if not self.check_finish(timeout=3 * 60):  # 排除阵容问题，只有成功或者超时
                raise Exception()

            sleep(3)
            finish_random_left_right()
            count += 1
            logger.ui(f"[{self.stone_pokemon}] 第{count}次")
            sleep(3)

    def check_pokemon_remain(self, need_click: bool) -> bool:
        """检查当前契灵是否还有剩余

        Returns:
            bool: 是否剩余
        """

        point = Point(
            self.pockmon_mapping[self.stone_pokemon][0],
            self.pockmon_mapping[self.stone_pokemon][1],
        )
        if need_click:
            Mouse.click(point)
            sleep(2)

            if self.stone_numbers == 0:
                logger.ui("鸣契石数量为0，跳过鸣契召唤")
                return True  # 不使用鸣契石，直接挑战

            if self.check_click(self.IMAGE_ZHAOHUAN, timeout=3, point_type="center"):
                logger.ui("召唤")
                return True

        result = RuleOcr().get_raw_result()
        for item in result:
            if item.text == "请选择鸣契的契灵数量":
                logger.ui("请选择鸣契的契灵数量")
                if self.stone_numbers == 0:
                    logger.ui("鸣契石数量为0，跳过鸣契召唤")
                    raise Exception("鸣契石数量为0，跳过鸣契召唤")
                self.choose_stone(self.stone_numbers)
                if need_click:
                    sleep(7)
                    Mouse.click(point)
                return False

    def choose_stone_confirm(self) -> bool:
        result = RuleOcr().get_raw_result()
        for item in result:
            if item.text[-2:] == "鸣契":
                logger.ui("确定")
                Mouse.click(item.center)
                return True
        return False

    def choose_stone(self, number: int = 1) -> bool:
        """选择鸣契石"""
        logger.ui(f"选择鸣契石[{self.stone_pokemon}]")

        if number == 99:
            if not self.check_click(self.IMAGE_STONE_MAX, timeout=5):
                logger.ui_warn("超时，未检测到最大值按钮")
                sleep(2)
        else:
            for _ in range(number - 1):
                if not self.check_click(self.IMAGE_STONE_ADD, timeout=5):
                    logger.ui_warn("超时，未检测到加号按钮")
                sleep()
        if not self.choose_stone_confirm():
            logger.ui_warn("超时，未检测到鸣契按钮")
        sleep()

        # 2个以上的鸣契石，需要确认
        if number > 1 and not self.check_click(self.global_assets.OCR_CONFIRM, timeout=5):
            logger.ui_warn("超时，未检测到确认按钮")

        logger.ui(f"选择鸣契石[{self.stone_pokemon}]成功")
        return True

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
            self.done()
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
        if self.check_pokemon_remain(need_click=True):  # 第一次如果使用鸣契石
            sleep(5)
            self.check_pokemon_remain(need_click=False)
        self.fight_until_finish()

    def run(self):
        self.check_title()
        if self.if_tancha:
            self.tancha_task()
        if self.if_jieqi:
            self.jieqi_task()
