from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException, TimesNotEnoughException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from ..utils.mythread import WorkTimer
from .utils import Package


class YingJieShiLian(Package):
    main_name = "英杰试炼"
    resource_path = "yingjieshilian"

    def __init__(self, n: int = 0) -> None:
        super().__init__(n)
        self.main_IMAGE_TITLE = self.get_image_asset("main_title")
        self.main_IMAGE_GOTO_EXP = self.get_image_asset("main_goto_exp")
        self.main_IMAGE_GOTO_SKILL = self.get_image_asset("main_goto_skill")

    @log_function_call
    def goto_scene(self):
        """跳转对应场景"""
        if not RuleImage(self.main_IMAGE_TITLE).match():
            return

        logger.scene(self.main_name)
        if isinstance(self, GuiBingYanWu) and self.check_click(self.main_IMAGE_GOTO_EXP, timeout=3):
            logger.ui(f"正在进入[{self.scene_name}]")

        if isinstance(self, BingZangMiJing) and self.check_click(self.main_IMAGE_GOTO_SKILL, timeout=3):
            logger.ui(f"正在进入[{self.scene_name}]")


class GuiBingYanWu(YingJieShiLian):
    scene_name = "鬼兵演武"
    resource_list: list = [
        "exp_title",  # 标题
        "exp_start",  # 开始
    ]

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)
        self._flag_timer_check_start: bool = False
        self.flag_soul_overflow: bool = False
        self.state = None

    @staticmethod
    def description() -> None:
        logger.ui("支持无御魂结算，不支持获得新技能时结算")

    def load_asset(self) -> None:
        self.IMAGE_TITLE = self.get_image_asset("exp_title")
        self.IMAGE_START = self.get_image_asset("exp_start")

    def start(self) -> None:
        """开始"""
        self.check_click(self.IMAGE_START)

    @log_function_call
    def timer_check_start(self):
        if RuleImage(self.IMAGE_TITLE).match():
            self._flag_timer_check_start = True

    def run(self) -> None:
        self.current_asset_list = [
            self.IMAGE_TITLE,
            self.IMAGE_START,
            # self.IMAGE_RESULT,
            self.global_image.IMAGE_FINISH,
            self.global_image.IMAGE_FAIL,
            self.global_image.IMAGE_VICTORY,
            self.global_image.IMAGE_SOUL_OVERFLOW,
        ]
        _flag_title_msg: bool = True
        self.log_current_asset_list()
        _count: int = 0  # 结算计数器，防止没御魂

        self.goto_scene()
        sleep(3)

        while self.n < self.max:
            if bool(event_thread):
                return
            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            if self._flag_timer_check_start:
                self._flag_timer_check_start = False
                logger.ui_error("进入挑战失败")
                break
            logger.info(f"current result name: {result.name}")
            match result.name:
                case "exp_title":
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
                            return
                        # 先判断御魂上限提醒
                        result = RuleImage(self.global_image.IMAGE_SOUL_OVERFLOW)
                        if result.match():
                            logger.ui_warn("御魂上限提醒")
                            self.flag_soul_overflow = True
                            Mouse.click(result.center_point())
                            continue

                        # 未重复检测到，表示成功点击
                        if not RuleImage(self.global_image.IMAGE_FINISH).match():
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


class BingZangMiJing(YingJieShiLian):
    scene_name = "兵藏秘境"

    def __init__(self, n=0):
        super().__init__(n)

    @staticmethod
    def description() -> None:
        logger.ui("支持自动选择结算BUFF")

    def load_asset(self):
        self.IMAGE_TITLE = self.get_image_asset("skill_title")
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
        finish_random_left_right()

        if result:
            if self.check_click(self.IMAGE_CHOOSE_BUFF, timeout=3):
                # 随便哪个buff都可以
                logger.ui("选择buff")
                self.check_click(self.IMAGE_CHOOSE_BUFF_ENSURE, timeout=3)
            elif self.check_click(self.IMAGE_CHOOSE_ATTR, timeout=3):
                logger.ui("选择属性")
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
