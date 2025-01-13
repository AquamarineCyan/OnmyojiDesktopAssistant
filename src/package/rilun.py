from ..utils.adapter import Mouse
from ..utils.assets import AssetImage
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from .utils import Package, get_asset


class RiLun(Package):
    """日轮副本"""

    scene_name = "日轮副本"
    resource_path = "rilun"
    resource_list: list = [
        "fighting",  # 对局进行中
    ]
    STATE_READY = 1
    STATE_RUNNING = 2

    @log_function_call
    def __init__(
        self, n: int = 0, flag_driver: bool = False, flag_passengers: int = 2
    ) -> None:
        super().__init__(n)
        self.flag_driver: bool = flag_driver  # 是否为司机（默认否）
        self.flag_passengers: bool = flag_passengers  # 组队人数
        self.flag_driver_start: bool = False  # 司机待机
        self.flag_fighting: bool = False  # 是否进行中对局（默认否）

    @staticmethod
    def description() -> None:
        logger.ui("日轮副本")

    def load_asset(self):
        self.IMAGE_FIGHTING = AssetImage(**get_asset(self.asset_image_list, "fighting"))

    def check_title(self) -> bool:
        """场景"""
        msg_title = True
        while True:
            if bool(event_thread):
                return
            if RuleImage(self.global_image.IMAGE_XIEZHANDUIWU).match():
                self.flag_driver_start = True
                return
            elif RuleImage(self.IMAGE_FIGHTING).match():
                self.flag_fighting = True
                return
            elif msg_title:
                self.title_error_msg()
                msg_title = False

    def finish(self) -> None:  # TODO 重构
        """结束"""
        self.check_result()
        sleep(1.5, 3)
        finish_random_left_right()
        while True:
            if bool(event_thread):
                return
            Mouse.click(wait=0.5)
            if self.check_result():
                while True:
                    if bool(event_thread):
                        return
                    sleep()
                    Mouse.click()
                    sleep()
                    if not RuleImage(self.global_image.IMAGE_FINISH).match():
                        break
                break
            sleep(0.4, 0.8)

    def run(self) -> None:
        # self.check_title()
        self.current_asset_list = [
            self.global_image.IMAGE_XIEZHANDUIWU,
            self.IMAGE_FIGHTING,
            self.global_image.IMAGE_ACCEPT_INVITATION,
        ]
        if self.flag_driver:
            self.current_asset_list.append(self.global_image.IMAGE_START_TEAM)
        msg_title: bool = True

        while self.n < self.max:
            if bool(event_thread):
                return

            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            match result.name:
                case "xiezhanduiwu":
                    logger.ui("组队界面准备中")
                    if self.flag_driver:
                        self.wait_passengers_on_position(self.flag_passengers)
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
