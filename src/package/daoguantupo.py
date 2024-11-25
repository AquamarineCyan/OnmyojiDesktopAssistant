from ..utils.adapter import Mouse
from ..utils.assets import AssetImage
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from .utils import Package, get_asset


class DaoGuanTuPo(Package):
    """道馆突破"""

    scene_name = "道馆突破"
    resource_path = "daoguantupo"
    resource_list = [
        "button_zhuwei",  # TODO 助威开关
        "chuzhan",  # 出战
        "daojishi",  # 倒计时
        "guanzhan",  # 观战
        # "guanzhuzhan",  # TODO 移除馆主战
        "jijie",  # 集结
        "qianwang",  # 前往-助威
        "shengyutuposhijian",  # 剩余突破时间
        "tiaozhan",  # 挑战
        "title",  # 标题
        "zhanbao",  # 战报
    ]
    description = "目前仅支持正在进行中的道馆突破，无法实现跳转道馆场景"
    STATE_IDLE = 1  # 准备界面
    STATE_WAIT_AUTO_ENTER = 2  # 等待主动进入
    STATE_WAIT_START = 3  # 等待开始
    STATE_FIGHTING = 4  # 进行中

    @log_function_call
    def __init__(self, flag_guanzhan: bool = False) -> None:
        super().__init__()
        self.flag_guanzhan = flag_guanzhan  # 是否观战
        self.flag_fighting = False  # 是否进行中
        self.state = self.STATE_IDLE

    def load_asset(self):
        self.IMAGE_BUTTON_ZHUWEI = AssetImage(
            **get_asset(self.asset_image_list, "button_zhuwei")
        )
        self.IMAGE_CHUZHAN = AssetImage(**get_asset(self.asset_image_list, "chuzhan"))
        self.IMAGE_DAOJISHI = AssetImage(**get_asset(self.asset_image_list, "daojishi"))
        self.IMAGE_GUANZHAN = AssetImage(**get_asset(self.asset_image_list, "guanzhan"))
        # self.IMAGE_GUANZHUZHAN = AssetImage(
        #     **get_asset(self.asset_image_list, "guanzhuzhan")
        # )
        # self.IMAGE_JIJIE = AssetImage(**get_asset(self.asset_image_list, "jijie"))
        self.IMAGE_QIANWANG = AssetImage(**get_asset(self.asset_image_list, "qianwang"))
        self.IMAGE_SHENYUTUPO = AssetImage(
            **get_asset(self.asset_image_list, "shengyutuposhijian")
        )
        self.IMAGE_TIAOZHAN = AssetImage(**get_asset(self.asset_image_list, "tiaozhan"))
        self.IMAGE_TITLE = AssetImage(**get_asset(self.asset_image_list, "title"))
        self.IMAGE_ZHANBAO = AssetImage(**get_asset(self.asset_image_list, "zhanbao"))
        self.IMAGE_ZHUWEI = AssetImage(**get_asset(self.asset_image_list, "zhuwei"))
        self.IMAGE_ZHUWEI_GRAY = AssetImage(
            **get_asset(self.asset_image_list, "zhuwei_gray")
        )

    @log_function_call
    def check_title(self) -> None:
        msg_title = True
        while True:
            if bool(event_thread):
                return

            if RuleImage(self.IMAGE_TITLE).match():
                logger.scene(self.scene_name)
                if RuleImage(self.IMAGE_DAOJISHI).match():
                    logger.ui("等待倒计时自动进入")
                    self.state = self.STATE_WAIT_AUTO_ENTER
                    return
                elif RuleImage(self.IMAGE_SHENYUTUPO).match():
                    logger.ui("可进攻")
                    self.state = self.STATE_WAIT_START
                    return
            elif RuleImage(self.IMAGE_BUTTON_ZHUWEI).match():
                logger.ui("道馆突破进行中")
                self.state = self.STATE_FIGHTING
                return
            elif msg_title:
                msg_title = False
                self.title_error_msg()

    def guanzhan(self):
        """观战"""
        logger.ui_warn("观战中，暂无法自动退出，可手动退出")
        # 战报按钮
        while True:
            if bool(event_thread):
                return
            if RuleImage(self.IMAGE_TITLE).match():
                self.check_click(self.IMAGE_ZHANBAO, timeout=5)
                self.check_click(self.IMAGE_QIANWANG, timeout=5)
                break
        sleep(2)

        self.current_asset_list = [
            self.IMAGE_ZHUWEI,
            self.IMAGE_ZHUWEI_GRAY,
            self.global_image.IMAGE_FINISH,
            self.global_image.IMAGE_FAIL,
        ]
        _flag_zhuwei_disable = False  # 是否能够助威

        while True:
            if bool(event_thread):
                return
            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            logger.info(f"current result name: {result.name}")
            match result.name:
                case "zhuwei":
                    Mouse.click(result.random_point())
                    logger.ui("助威成功")
                    _flag_zhuwei_disable = True
                case "zhuwei_gray":
                    if _flag_zhuwei_disable:
                        logger.ui("无法助威")
                        _flag_zhuwei_disable = False
                case "finish":
                    self.ensure_finish()
                case "fail":
                    logger.ui_warn("失败")
                    sleep(0.4, 0.8)
                    finish_random_left_right()
                    while True:
                        if bool(event_thread):
                            return
                        # 未重复检测到，表示成功点击
                        if not RuleImage(self.global_image.IMAGE_FAIL).match():
                            self.done()
                            break
                        Mouse.click()
                        sleep(0.4, 0.8)
            sleep(4)

    def run(self):
        self.check_title()
        logger.num(0)
        sleep(2, 4)
        if self.state == self.STATE_WAIT_START:
            self.check_click(self.IMAGE_TIAOZHAN, timeout=5)
        sleep(2, 4)

        # 开始
        self.current_asset_list = [
            self.global_image.IMAGE_READY_OLD,
            self.global_image.IMAGE_READY_NEW,
            self.global_image.IMAGE_VICTORY,
            self.global_image.IMAGE_FAIL,
            self.global_image.IMAGE_FINISH,
        ]

        while True:
            if bool(event_thread):
                return

            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            logger.info(f"current result name: {result.name}")
            match result.name:
                case "ready_old" | "ready_new":
                    logger.ui("准备")
                    Mouse.click(result.random_point())
                    self.n += 1
                    logger.num(str(self.n))
                    sleep(2)
                case "finish":
                    finish_random_left_right()
                    break
                case "fail":
                    logger.ui_warn("失败，需要手动处理")
                    break

        if self.flag_guanzhan:
            self.guanzhan()
