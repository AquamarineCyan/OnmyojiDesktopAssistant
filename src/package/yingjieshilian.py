from ..utils.adapter import Mouse
from ..utils.event import event_thread
from ..utils.exception import GUIStopException, TimesNotEnoughException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from ..utils.mythread import WorkTimer
from .base_package import BasePackage
from .types import Yingjie


class YingJieShiLian(BasePackage):
    main_name = "英杰试炼"
    resource_path = "yingjieshilian"

    yingjie: Yingjie

    def __init__(
        self,
        yingjie: Yingjie,
        n: int = 0,
    ) -> None:
        self.yingjie = yingjie  # 必须在初始化前
        super().__init__(n)

        if self.yingjie == Yingjie.YUAN_LAI_GUANG:
            self.IMAGE_GOTO_EXP = self.get_image_asset("yuan_goto_exp")
            self.IMAGE_GOTO_SKILL = self.get_image_asset("yuan_goto_skill")
        elif self.yingjie == Yingjie.TENG_YUAN_DAO_CHANG:
            self.IMAGE_GOTO_EXP = self.get_image_asset("teng_goto_exp")
            self.IMAGE_GOTO_SKILL = self.get_image_asset("teng_goto_skill")
        else:
            raise ValueError(f"不支持的英杰: {self.yingjie}")
        self.IMAGE_MAIN_TITLE = self.get_image_asset("main_title")

    def goto_scene(self):
        """跳转对应场景"""
        logger.info("准备跳转子场景")
        if not RuleImage(self.IMAGE_MAIN_TITLE).match():
            return

        logger.scene(self.main_name)

        if isinstance(self, YingJieShiLianExp) and self.check_click(self.IMAGE_GOTO_EXP, timeout=3):
            logger.ui(f"正在进入[{self.scene_name}]")

        if isinstance(self, YingJieShiLianSkill) and self.check_click(self.IMAGE_GOTO_SKILL, timeout=3):
            logger.ui(f"正在进入[{self.scene_name}]")


class YingJieShiLianExp(YingJieShiLian):
    scene_name = "经验本"
    resource_list: list = [
        "exp_start",  # 开始
        "yuan_exp_title",  # 标题
        "teng_exp_title",  # 标题
    ]

    def __init__(self, yingjie: Yingjie, n: int = 0) -> None:
        super().__init__(yingjie, n)
        self._flag_timer_check_start: bool = False
        self.flag_soul_overflow: bool = False
        self.state = None

    @staticmethod
    def description() -> None:
        logger.ui("支持无御魂结算，获得新技能时会尝试结算")

    def load_asset(self) -> None:
        if self.yingjie == Yingjie.YUAN_LAI_GUANG:
            self.scene_name = "鬼兵演武"
            self.IMAGE_TITLE = self.get_image_asset("yuan_exp_title")
        elif self.yingjie == Yingjie.TENG_YUAN_DAO_CHANG:
            self.scene_name = "传承试炼"
            self.IMAGE_TITLE = self.get_image_asset("teng_exp_title")
        else:
            raise ValueError(f"不支持的英杰: {self.yingjie}")
        self.IMAGE_START = self.get_image_asset("exp_start")

    def timer_check_start(self):
        if RuleImage(self.IMAGE_TITLE).match():
            self._flag_timer_check_start = True

    def run(self) -> None:
        self.current_asset_list = [
            self.IMAGE_TITLE,
            self.IMAGE_START,
            # self.IMAGE_RESULT,
            self.global_assets.IMAGE_FINISH,
            self.global_assets.IMAGE_FAIL,
            self.global_assets.IMAGE_VICTORY,
            self.global_assets.IMAGE_SOUL_OVERFLOW,
        ]
        _flag_title_msg: bool = True
        self.log_current_asset_list()
        _count: int = 0  # 结算计数器，防止没御魂

        self.goto_scene()
        sleep(3)

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            if self._flag_timer_check_start:
                self._flag_timer_check_start = False
                logger.ui_error("进入挑战失败")
                break
            logger.info(f"current result name: {result.name}")
            match result.name:
                case "yuan_exp_title" | "teng_exp_title":
                    logger.scene(self.scene_name)
                    _flag_title_msg = False
                    self.start()
                    sleep()
                    _timer = WorkTimer(3, self.timer_check_start)
                    _timer.start()
                case "fail":
                    if _timer:
                        _timer.cancel()
                    logger.ui_error("失败")
                    break
                case "victory":
                    if _timer:
                        _timer.cancel()
                    logger.ui("胜利")
                    _count += 1
                    if _count >= 5:
                        logger.ui_warn("未检测到御魂，自动退出")
                        _count = 0
                        finish_random_left_right()
                        self.done()
                        sleep(2)
                        continue
                    sleep()
                case "finish":
                    if _timer:
                        _timer.cancel()
                    logger.ui("结束")
                    _count = 0
                    sleep(0.4, 0.8)
                    _coor_point = finish_random_left_right(is_multiple_drops_y=True)
                    sleep()
                    if self.flag_soul_overflow:
                        sleep()

                    # 尚未测试出
                    while True:
                        if bool(event_thread):
                            raise GUIStopException

                        # 先判断御魂上限提醒
                        result = RuleImage(self.global_assets.IMAGE_SOUL_OVERFLOW)
                        if result.match():
                            logger.ui_warn("御魂上限提醒")
                            self.flag_soul_overflow = True
                            Mouse.click(result.center_point())
                            continue

                        # 未重复检测到，表示成功点击
                        if not RuleImage(self.global_assets.IMAGE_FINISH).match():
                            break
                        Mouse.click(_coor_point)

                    self.done()
                    sleep()
                case "soul_overflow":
                    if _timer:
                        _timer.cancel()
                    logger.ui_warn("御魂上限提醒")
                    self.flag_soul_overflow = True
                    Mouse.click(result.center_point())
                case _:
                    if _flag_title_msg:
                        self.title_error_msg()
                        _flag_title_msg = False


class YingJieShiLianSkill(YingJieShiLian):
    scene_name = "技能本"

    def __init__(
        self,
        yingjie: Yingjie = Yingjie.TENG_YUAN_DAO_CHANG,
        n=0,
    ):
        super().__init__(yingjie, n)

    @staticmethod
    def description() -> None:
        logger.ui("支持自动选择结算技能")

    def load_asset(self) -> None:
        if self.yingjie == Yingjie.YUAN_LAI_GUANG:
            self.scene_name = "兵藏秘境"
            self.IMAGE_TITLE = self.get_image_asset("yuan_skill_title")
        elif self.yingjie == Yingjie.TENG_YUAN_DAO_CHANG:
            self.scene_name = "梦墟秘境"
            self.IMAGE_TITLE = self.get_image_asset("teng_skill_title")
        else:
            raise ValueError(f"不支持的英杰: {self.yingjie}")
        self.IMAGE_START = self.get_image_asset("skill_start")
        self.IMAGE_FIRST_REMAIN = self.get_image_asset("skill_first_remain")
        self.IMAGE_CHOOSE_ATTR = self.get_image_asset("skill_choose_attribute")
        self.IMAGE_CHOOSE_BUFF = self.get_image_asset("skill_choose_buff")
        self.IMAGE_CHOOSE_BUFF_ENSURE = self.get_image_asset("skill_choose_buff_ensure")

    def check_main_scene(self):
        _msg: bool = False
        while True:
            if bool(event_thread):
                raise GUIStopException

            if RuleImage(self.IMAGE_TITLE).match():
                logger.scene(self.scene_name)
                break

            sleep()
            if not _msg:
                self.title_error_msg()
                _msg = True

    def fight(self):
        self.check_click(self.IMAGE_START, timeout=3)

        # 跳过提醒
        sleep()
        result = RuleImage(self.IMAGE_FIRST_REMAIN)
        if result.match():
            Mouse.click(result.center_point())  # 满技能提醒
            sleep()
            Mouse.click()  # 不可更换提醒

        sleep(5)
        # 检测能否进入战斗
        if RuleImage(self.IMAGE_START).match():
            logger.info("次数不足，无法进入战斗")
            raise TimesNotEnoughException

        result = self.check_result()
        sleep(2)
        finish_random_left_right(is_multiple_drops_x=True)
        sleep(2)

        if result:
            if self.check_click(self.IMAGE_CHOOSE_BUFF, timeout=3):
                # 随便哪个祝福都可以
                logger.ui("选择祝福")
                sleep(2)
                self.check_click(self.IMAGE_CHOOSE_BUFF_ENSURE, timeout=3)
            elif self.check_click(self.IMAGE_CHOOSE_ATTR, timeout=3):
                logger.ui("选择属性")
                sleep(2)
                self.check_click(self.IMAGE_CHOOSE_BUFF_ENSURE, timeout=3)
            self.done()

    def run(self):
        self.goto_scene()
        sleep(3)
        self.check_main_scene()

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            sleep(3)
            self.fight()
