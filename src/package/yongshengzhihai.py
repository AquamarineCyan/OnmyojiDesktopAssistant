from ..utils.adapter import Mouse
from ..utils.assets import AssetImage
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from .utils import Package, get_asset


class YongShengZhiHai(Package):
    """永生之海副本"""

    scene_name = "永生之海副本"
    resource_path = "yongshengzhihai"
    resource_list = [
        "title_team",  # 组队界面
        "passenger",  # 队员
        "start_team",  # 组队挑战
        # "start_single",  # 单人挑战
        "fighting",  # 进行中
        # "accept_invitation",  # 接受邀请
    ]
    description = "默认打手30次"
    fast_time = 13 - 2

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    def load_asset(self):
        self.IMAGE_TITLE = AssetImage(**get_asset(self.asset_image_list, "title"))
        self.IMAGE_PASSENGER = AssetImage(
            **get_asset(self.asset_image_list, "passenger")
        )
        self.IMAGE_START_TEAM = AssetImage(
            **get_asset(self.asset_image_list, "start_team")
        )
        self.IMAGE_FIGHTING = AssetImage(**get_asset(self.asset_image_list, "fighting"))

    @log_function_call
    def start(self) -> None:
        """挑战"""
        if isinstance(self, YongShengZhiHaiTeam):
            self.check_click(self.IMAGE_START_TEAM)
        else:
            self.check_click(self.global_image.IMAGE_START_SINGLE)


class YongShengZhiHaiTeam(YongShengZhiHai):
    """组队永生之海副本"""

    scene_name = "组队永生之海副本"
    resource_list = [
        "title_team",  # 组队界面
        # "passenger_2",  # 队员2
        "start_team",  # 组队挑战
        "fighting",  # 进行中
        "accept_invitation",  # 接受邀请
    ]

    @log_function_call
    def __init__(
        self,
        n: int = 0,
        flag_driver: bool = False,
        flag_drop_statistics: bool = False,  # TODO
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
                return False
            if not RuleImage(self.IMAGE_PASSENGER).match():
                logger.ui("队员就位")
                return True

    @log_function_call
    def finish(self):
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
            if event_thread.is_set():
                return
            # 检测到任一图像
            result = check_image_once(
                [
                    self.global_image.IMAGE_FINISH,
                    self.global_image.IMAGE_TANCHIGUI,
                ]
            )
            # 直到第一次识别到
            if _flag_first and result is None:
                continue
            if result:
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
        msg_title: bool = True
        self.current_asset_list = [
            self.IMAGE_TITLE,
            self.IMAGE_FIGHTING,
            self.global_image.IMAGE_ACCEPT_INVITATION,
        ]
        if self.flag_driver:
            self.current_asset_list.append(self.global_image.IMAGE_START_TEAM)

        while self.n < self.max:
            if bool(event_thread):
                return
            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            match result.name:
                case "title":
                    logger.ui("组队界面准备中")
                    if self.flag_driver:
                        self.wait_passengers_on_position()
                        self.start()
                    sleep()
                    msg_title = False
                case "fighting":
                    logger.ui("对局进行中")
                    self.finish()
                    self.done()
                    sleep()
                    msg_title = False
                case "accept_invitation":
                    # TODO 新设备第一次接受邀请会有弹窗，需手动勾选“不再提醒”
                    logger.ui("接受邀请")
                    Mouse.click(result.center_point())
                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False
