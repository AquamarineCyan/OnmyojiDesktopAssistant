from ..utils.adapter import Mouse
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import sleep
from ..utils.log import logger
from ..utils.paddleocr import RuleOcr
from ..utils.point import Point
from .base_package import BasePackage
from .jiejietupo import JieJieTuPoGeRen
from .tansuo import TanSuo


class HuiJuan(BasePackage):
    """绘卷"""

    scene_name = "绘卷刷分"

    def __init__(
        self,
        n: int = 0,
        loop_count: int = 1,
        flag_refresh_rule: int = 3,
        flag_current_level: int = 57,
        flag_target_level: int = 57,
        flag_first_round_failure: bool = True,
    ) -> None:
        """
        Args:
            n (int): 次数
            loop_count (int): 单次循环轮数
            flag_refresh_rule (int): 刷新规则
            flag_current_level (int): 当前等级
            flag_target_level (int): 目标等级
            flag_first_round_failure (bool):  首轮失败标志
        """
        super().__init__(n)
        self.loop_count: int = loop_count
        self.flag_refresh_rule: int = flag_refresh_rule
        self.flag_current_level: int = flag_current_level
        self.flag_target_level: int = flag_target_level
        self.flag_first_round_failure: bool = flag_first_round_failure

    @staticmethod
    def description() -> None:
        logger.ui("提前准备好自动轮换和加成，独立预设御魂，采取探索 + 个人突破的方式")

    def load_asset_list(self):
        pass

    def get_current_number(self):
        result = RuleOcr(region=(650, 0, 100, 55)).get_raw_result()
        try:
            for item in result:
                if "/30" == item.text[-3:]:
                    number = int(item.text[:-3])
                    logger.ui(f"突破券: {number}")
        except ValueError:
            number = -1
            logger.ui_error("突破券识别失败")
        return number

    def get_current_scene(self) -> Point | None:
        result = RuleOcr(region=(200, 550, 100, 90)).get_raw_result()
        for item in result:
            if "结界突破" in item.text:
                return Point(
                    item.center.client_x + 200, item.center.client_y + 550
                )  # TODO 底层解决相对截图时的坐标问题

        return None

    def run(self):
        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            logger.ui(f"第{self.n + 1}轮")
            sleep(2)

            tansuo_count = self.loop_count
            logger.ui(f"探索{tansuo_count}次")
            TanSuo(tansuo_count).run()
            self.close_current_scene()

            sleep(2)
            number = self.get_current_number()

            sleep(2)
            logger.ui("正在前往 结界突破")
            sleep(2)

            point = self.get_current_scene()
            if point:
                Mouse.click(point)
            else:
                logger.ui_error("未识别到结界突破")
                return

            sleep(4)

            # TODO 判断机制
            logger.ui(f"个人突破{number}次")
            JieJieTuPoGeRen(
                number,
                flag_refresh_rule=self.flag_refresh_rule,
                flag_current_level=self.flag_current_level,
                flag_target_level=self.flag_target_level,
                flag_first_round_failure=self.flag_first_round_failure,
            ).run()
            self.close_current_scene()

            self.n += 1
