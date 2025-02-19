from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import check_image_once
from ..utils.log import logger
from ..utils.paddleocr import RuleOcr
from .utils import Package


class RiLun(Package):
    """日轮副本"""

    scene_name = "日轮副本"
    resource_path = "rilun"

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    @log_function_call
    def start(self) -> None:
        """挑战"""
        logger.ui("开始挑战")
        if isinstance(self, RiLunTeam):
            self.check_click(self.global_assets.IMAGE_START_TEAM, timeout=3)
        elif isinstance(self, RiLunSingle):
            self.check_click(self.global_assets.IMAGE_START_SINGLE, timeout=3)


class RiLunTeam(RiLun):
    """组队日轮副本"""

    resource_list: list = [
        "fighting",  # 对局进行中
    ]
    STATE_READY = 1
    STATE_RUNNING = 2

    @log_function_call
    def __init__(self, n: int = 0, flag_driver: bool = False, flag_passengers: int = 2) -> None:
        super().__init__(n)
        self.flag_driver: bool = flag_driver  # 是否为司机（默认否）
        self.flag_passengers: bool = flag_passengers  # 组队人数
        self.flag_driver_start: bool = False  # 司机待机
        self.flag_fighting: bool = False  # 是否进行中对局（默认否）

    @staticmethod
    def description() -> None:
        logger.ui("组队日轮副本")

    @log_function_call
    def wait_finish(self):
        """等待结束

        掉落物大体分为2种情况：

        1.正常情况，达摩蛋能被识别

        2.掉落过多情况（指神罚一排紫蛇皮），达摩蛋被遮挡，此时贪吃鬼必定（可能）出现
        """
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
                Mouse.click()
                _flag_first = False
                sleep(0.6, 1)

            # 所有图像都未检测到，退出循环
            else:
                logger.ui("结束")
                return

    def run(self) -> None:
        msg_title: bool = True
        msg_fighting: bool = True

        self.current_asset_list = [
            self.global_assets.IMAGE_XIEZHANDUIWU,
            self.global_assets.IMAGE_ACCEPT_INVITATION,
        ]

        if self.flag_driver:
            self.current_asset_list.append(self.global_assets.IMAGE_START_TEAM)

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            msg_fighting = True
            result = check_image_once(self.current_asset_list)
            if result is None:
                # 判断是否在战斗中
                result = RuleOcr(self.global_assets.OCR_AUTO_FIGHT)
                if result.match():
                    if msg_fighting:
                        logger.ui("自动战斗中")
                        msg_fighting = False

                    self.wait_finish()
                    self.done()
                    msg_title = False
                    sleep()

                if msg_title:
                    self.title_error_msg()
                    msg_title = False

                continue

            match result.name:
                case self.global_assets.IMAGE_XIEZHANDUIWU.name:
                    logger.scene("组队界面准备中")
                    if self.flag_driver:
                        self.wait_passengers_on_position(self.flag_passengers)
                        sleep(1.5)
                        self.start()
                    sleep()
                    msg_title = False

                case self.global_assets.IMAGE_ACCEPT_INVITATION.name:
                    logger.ui("接受邀请")
                    Mouse.click(result.center_point())

                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False


class RiLunSingle(RiLun):
    """单人日轮副本"""

    scene_name = "单人日轮副本"
    resource_list = [
        "title_3",  # 三层
        "title_4",  # 日蚀
    ]

    @log_function_call
    def __init__(self, n: int = 0):
        super().__init__(n)

    def load_asset(self):
        super().load_asset()
        self.IMAGE_TITLE_3 = self.get_image_asset("title_3")
        self.IMAGE_TITLE_4 = self.get_image_asset("title_4")

    def run(self):
        msg_title: bool = True  # 标题消息
        msg_fighting: bool = True  # 自动战斗中消息
        flag_soul_overflow: bool = False  # 御魂上限标志

        self.current_asset_list = [
            self.IMAGE_TITLE_3,
            self.IMAGE_TITLE_4,
            self.global_assets.IMAGE_START_SINGLE,
            self.global_assets.IMAGE_FAIL,
            self.global_assets.IMAGE_FINISH,
            self.global_assets.IMAGE_VICTORY,
            self.global_assets.IMAGE_SOUL_OVERFLOW,
        ]

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            msg_fighting = True
            result = check_image_once(self.current_asset_list)
            if result is None:
                # 判断是否在战斗中
                result = RuleOcr(self.global_assets.OCR_AUTO_FIGHT)
                if result.match() and msg_fighting:
                    logger.ui("自动战斗中")
                    msg_fighting = False

                if msg_title:
                    self.title_error_msg()
                    msg_title = False

                continue

            match result.name:
                case self.IMAGE_TITLE_3.name | self.IMAGE_TITLE_4.name:
                    match result.name:
                        case self.IMAGE_TITLE_3.name:
                            logger.scene("日轮叁层")
                        case self.IMAGE_TITLE_4.name:
                            logger.scene("日轮日蚀")
                    self.start()
                    msg_title = False
                    sleep(2)

                case self.global_assets.IMAGE_START_SINGLE.name:  # 一般在上一级case中已经处理
                    logger.ui("开始挑战")
                    Mouse.click(result.center_point())
                    msg_title = False

                case self.global_assets.IMAGE_FAIL.name:
                    logger.ui_warn("失败，需要手动处理")
                    break

                case self.global_assets.IMAGE_VICTORY.name:
                    logger.ui("胜利")
                    sleep()  # 等待结算

                case self.global_assets.IMAGE_FINISH.name:
                    logger.ui("结束")

                    if flag_soul_overflow:
                        sleep(1)
                    if self.check_click(self.global_assets.IMAGE_SOUL_OVERFLOW, timeout=2, duration=0.75):
                        logger.ui_warn("御魂上限")
                        flag_soul_overflow = True

                    finish_random_left_right()
                    self.done()
                    msg_fighting = False
                    sleep(3)  # 等待过场图

                case self.global_assets.IMAGE_SOUL_OVERFLOW.name:  # 正常情况下会在结束界面点击，这是备用方案
                    logger.ui_warn("御魂上限")
                    Mouse.click(result.center_point(), duration=0.75)
                    flag_soul_overflow = True

                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False
