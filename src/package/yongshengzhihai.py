from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from ..utils.paddleocr import RuleOcr
from .utils import Package


class YongShengZhiHai(Package):
    """永生之海副本"""

    scene_name = "永生之海副本"
    resource_path = "yongshengzhihai"
    resource_list = [
        "title_team",  # 组队界面
        "passenger",  # 队员
        "start_team",  # 组队挑战
    ]

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    @staticmethod
    def description() -> None:
        logger.ui("组队永生之海，默认30次")

    def load_asset(self):
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_PASSENGER = self.get_image_asset("passenger")
        self.IMAGE_START_TEAM = self.get_image_asset("start_team")

    @log_function_call
    def start(self) -> None:
        """挑战"""
        logger.ui("开始挑战")
        if isinstance(self, YongShengZhiHaiTeam):
            self.check_click(self.IMAGE_START_TEAM, timeout=3)
        else:
            self.check_click(self.global_assets.IMAGE_START_SINGLE, timeout=3)


class YongShengZhiHaiTeam(YongShengZhiHai):
    """组队永生之海副本"""

    scene_name = "组队永生之海副本"
    resource_list = [
        "title_team",  # 组队界面
        "start_team",  # 组队挑战
    ]

    @log_function_call
    def __init__(
        self,
        n: int = 0,
        flag_driver: bool = False,
        flag_drop_statistics: bool = False,
    ) -> None:
        """
        组队永生之海副本

        参数:
            n (int): 次数，默认0次

            flag_driver (bool): 是否司机，默认否

            flag_drop_statistics (bool): 是否开启掉落统计，默认否
        """
        super().__init__(n)
        self.flag_driver: bool = flag_driver  # 是否为司机（默认否）
        self.flag_drop_statistics: bool = flag_drop_statistics  # 是否开启掉落统计

    @log_function_call
    def wait_passengers_on_position(self) -> bool:
        """队员就位"""
        logger.ui("等待队员")
        while True:
            if bool(event_thread):
                raise GUIStopException

            if not RuleImage(self.IMAGE_PASSENGER).match():
                logger.ui("队员就位")
                return True

    @log_function_call
    def check_fighting(self):
        """判断是否在战斗中"""
        flag: bool = False
        result = RuleOcr().get_raw_result()
        for item in result:
            # 点击屏幕继续 是兜底方案
            if item.text in ["自动", "特殊机制", "点击屏幕继续"]:
                logger.info(f"keyword: {item.text}")
                flag = True
                break

        if flag:
            if self.msg_fighting:
                logger.ui("自动战斗中")
                self.msg_fighting = False

            self.wait_finish()
            self.done()
            self.msg_title = False
            sleep()

        if self.msg_title:
            self.title_error_msg()
            self.msg_title = False

    @log_function_call
    def wait_finish(self):
        """
        结束

        掉落物大体分为2种情况：

        1.正常情况，达摩蛋能被识别

        2.掉落过多情况（指神罚一排紫蛇皮），达摩蛋被遮挡，此时贪吃鬼必定（可能）出现
        """
        _flag_screenshot = True
        _flag_first = True
        self.check_result()
        sleep(0.4, 0.8)
        # 结算
        finish_random_left_right(is_multiple_drops_x=True)
        Mouse.click(wait=0.5)

        while True:
            if bool(event_thread):
                raise GUIStopException

            # 检测到任一图像
            result = check_image_once(
                [
                    self.global_assets.IMAGE_FINISH,
                    self.global_assets.IMAGE_TANCHIGUI,
                ]
            )

            # 直到第一次识别到
            if _flag_first and result is None:
                continue

            if result:
                logger.info(f"current scene: {result.name}")
                if _flag_screenshot and self.flag_drop_statistics:
                    self.screenshot()
                    _flag_screenshot = False
                Mouse.click()
                _flag_first = False
                sleep(0.6, 1)

            # 所有图像都未检测到，退出循环
            else:
                logger.ui("结束")
                return

    def run(self):
        self.msg_title: bool = True  # 标题消息
        self.msg_fighting: bool = True  # 自动战斗中消息

        self.current_asset_list = [
            self.IMAGE_TITLE,
            self.global_assets.IMAGE_ACCEPT_INVITATION,
        ]

        if self.flag_driver:
            self.current_asset_list.append(self.global_assets.IMAGE_START_TEAM)

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            self.msg_fighting = True
            result = check_image_once(self.current_asset_list)
            if result is None:
                self.check_fighting()
                continue

            match result.name:
                case self.IMAGE_TITLE.name:
                    logger.ui("组队界面准备中")
                    if self.flag_driver:
                        self.wait_passengers_on_position()
                        sleep(1.5)
                        self.start()
                    sleep()
                    self.msg_title = False

                case self.global_assets.IMAGE_ACCEPT_INVITATION.name:
                    logger.ui("接受邀请")
                    Mouse.click(result.center_point())
                    sleep()

                case _:
                    if self.msg_title:
                        self.title_error_msg()
                        self.msg_title = False
