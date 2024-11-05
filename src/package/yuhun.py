from ..utils.adapter import KeyBoard, Mouse
from ..utils.assets import AssetImage
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import check_image_once
from ..utils.log import logger
from .utils import Package, get_asset


class YuHun(Package):
    """御魂副本"""

    scene_name = "御魂副本"
    resource_path = "yuhun"
    resource_list = [
        "title_10",  # 魂十
        "title_11",  # 魂土
        "title_12",  # 神罚
        "xiezhanduiwu",  # 组队界面
        # "passenger_2",  # 队员2
        # "passenger_3",  # 队员3
        "start_team",  # 组队挑战
        "start_single",  # 单人挑战
        # "fighting",  # 魂土进行中
        "fighting_linshuanghanxue",  # 凛霜寒雪战斗主题
        "fighting_shenfa",  # 神罚战斗场景
        "finish_damage",  # 结束特征图像
        # "finish_damage_2000",  # 结束特征图像-鎏金圣域
        "finish_damage_shenfa",  # 结束特征图像-神罚
    ]
    description = "已适配组队/单人 魂十、魂土、神罚副本\
                    司机请在组队界面等待\
                    新设备第一次接受邀请会有弹窗，需手动勾选“不再提醒”"
    fast_time = 13 - 2
    ASSET = True

    @log_function_call
    def __init__(self, n) -> None:
        super().__init__(n)

    def load_asset(self):
        self.IMAGE_FIGHTING_LINSHUANGHANXUE = AssetImage(
            **get_asset(self.asset_image_list, "fighting_linshuanghanxue")
        )
        self.IMAGE_FIGHTING_SHENFA = AssetImage(
            **get_asset(self.asset_image_list, "fighting_shenfa")
        )
        self.IMAGE_FINISH_DAMAGE = AssetImage(
            **get_asset(self.asset_image_list, "finish_damage")
        )
        self.IMAGE_FINISH_DAMAGE_2000 = AssetImage(
            **get_asset(self.asset_image_list, "finish_damage_2000")
        )
        self.IMAGE_FINISH_DAMAGE_SHENFA = AssetImage(
            **get_asset(self.asset_image_list, "finish_damage_shenfa")
        )
        self.IMAGE_TITLE_10 = AssetImage(**get_asset(self.asset_image_list, "title_10"))
        self.IMAGE_TITLE_11 = AssetImage(**get_asset(self.asset_image_list, "title_11"))
        self.IMAGE_TITLE_12 = AssetImage(**get_asset(self.asset_image_list, "title_12"))

    @log_function_call
    def start(self) -> None:
        """挑战"""
        if isinstance(self, YuHunTeam):
            self.check_click(self.global_image.IMAGE_START_TEAM)
        elif isinstance(self, YuHunSingle):
            self.check_click(self.global_image.IMAGE_START_SINGLE)


class YuHunTeam(YuHun):
    """组队御魂副本"""

    scene_name = "组队御魂副本"
    resource_list = [  # 资源列表
        "xiezhanduiwu",  # 组队界面
        # "passenger_2",  # 队员2
        # "passenger_3",  # 队员3
        "start_team",  # 组队挑战
        "fighting",  # 魂土进行中
        "fighting_linshuanghanxue",  # 凛霜寒雪战斗主题
        "fighting_shenfa",  # 神罚战斗场景
        "finish_damage",  # 结束特征图像
        "finish_damage_2000",  # 结束特征图像-鎏金圣域
        "finish_damage_shenfa",  # 结束特征图像-神罚
        "accept_invitation",  # 接受邀请
    ]

    @log_function_call
    def __init__(
        self,
        n: int = 0,
        flag_driver: bool = False,
        flag_passengers: int = 2,
        flag_drop_statistics: bool = False,
    ) -> None:
        super().__init__(n)
        """组队御魂副本

        参数:
            n (int): 次数，默认0次
            flag_driver (bool): 是否司机，默认否
            flag_passengers (int): 组队人数，默认2人
            flag_drop_statistics (bool): 是否开启掉落统计，默认否
        """
        self.flag_driver: bool = flag_driver  # 是否为司机（默认否）
        self.flag_passengers: int = flag_passengers  # 组队人数
        self.flag_drop_statistics: bool = flag_drop_statistics  # 是否开启掉落统计

    @log_function_call
    def finish(self):
        """结束

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
                return
            # 检测到任一图像
            result = check_image_once(
                [
                    self.global_image.IMAGE_FINISH,
                    self.IMAGE_FINISH_DAMAGE_2000,
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
        self.current_asset_list = [
            self.global_image.IMAGE_XIEZHANDUIWU,
            self.global_image.IMAGE_FIGHTING,
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
                        self.is_passengers_on_position(self.flag_passengers)
                        self.start()
                    sleep()
                    msg_title = False
                case "fighting":
                    logger.ui("对局进行中")
                    self.finish()
                    self.done()
                    msg_title = False
                    sleep()
                    KeyBoard.enter()
                case "accept_invitation":
                    # TODO 新设备第一次接受邀请会有弹窗，需手动勾选“不再提醒”
                    logger.ui("接受邀请")
                    Mouse.click(result.center_point())
                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False


class YuHunSingle(YuHun):
    """单人御魂副本"""

    scene_name = "单人御魂副本"
    resource_list = [
        "title_10",  # 魂十
        "title_11",  # 魂土
        "title_12",  # 神罚
        "start_single",  # 单人挑战
        "fighting",  # 魂土进行中
        "fighting_linshuanghanxue",  # 凛霜寒雪战斗主题
        "fighting_shenfa",  # 神罚战斗场景
        # "finish_damage",  # 结束特征图像
        # "finish_damage_2000",  # 结束特征图像-鎏金圣域
        # "finish_damage_shenfa",  # 结束特征图像-神罚
    ]

    @log_function_call
    def __init__(self, n: int = 0, flag_drop_statistics: bool = False):
        super().__init__(n)
        """单人御魂副本

        参数:
            n (int): 次数，默认0次
            flag_drop_statistics (bool): 是否开启掉落统计，默认否
        """
        self.flag_drop_statistics: bool = flag_drop_statistics  # 是否开启掉落统计

    def run(self):
        msg_title: bool = True
        msg_fighting: bool = True
        self.current_asset_list = [
            self.IMAGE_TITLE_10,
            self.IMAGE_TITLE_11,
            self.IMAGE_TITLE_12,
            self.IMAGE_FIGHTING_LINSHUANGHANXUE,
            self.IMAGE_FIGHTING_SHENFA,
            self.global_image.IMAGE_START_SINGLE,
            self.global_image.IMAGE_FIGHTING,
            self.global_image.IMAGE_FAIL,
            self.global_image.IMAGE_FINISH,
            self.global_image.IMAGE_VICTORY,
            self.global_image.IMAGE_SOUL_OVERFLOW,
        ]

        while self.n < self.max:
            if bool(event_thread):
                return
            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            match result.name:
                case "title_10" | "title_11" | "title_12":
                    self.start()
                    sleep(self.fast_time)
                    msg_title = False
                case "start_single":
                    Mouse.click(result.center_point())
                    sleep(self.fast_time)
                    msg_title = False
                case "fighting" | "fighting_linshuanghanxue" | "fighting_shenfa":
                    if msg_fighting:
                        logger.ui("对局进行中")
                        msg_fighting = False
                    msg_title = False
                case "fail":
                    logger.ui_warn("失败，需要手动处理")
                    break
                case "victory":
                    logger.ui("胜利")
                    sleep()
                case "finish":
                    logger.ui("结束")
                    if self.check_click(
                        self.global_image.IMAGE_SOUL_OVERFLOW, timeout=2
                    ):
                        logger.ui_warn("御魂上限")  # TODO 测试
                    finish_random_left_right()
                    self.done()
                    msg_fighting = False
                    sleep(2)
                case "soul_overflow":  # 正常情况下会在结束界面点击，这是备用方案
                    logger.ui_warn("御魂上限")
                    Mouse.click(result.random_point())
                case _:
                    if msg_title:
                        self.title_error_msg()
                        msg_title = False
