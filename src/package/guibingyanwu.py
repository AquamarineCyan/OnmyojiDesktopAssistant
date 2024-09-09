from ..utils.adapter import Mouse
from ..utils.assets import AssetImage
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import finish_random_left_right, get_asset_data, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from ..utils.mythread import WorkTimer
from .utils import Package, get_asset


class GuiBingYanWu(Package):
    scene_name = "鬼兵演武"
    resource_path = "guibingyanwu"
    description = "适配活动「鬼兵演武」，支持无御魂结算，不支持获得新技能时结算。"

    ASSET = True

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)
        _, data = get_asset_data(self.resource_path)
        self.activity_name = data.get("activity_name")
        self._flag_timer_check_start: bool = False
        self.flag_soul_overflow: bool = False
        self.state = None

    def load_asset(self) -> None:
        self.IMAGE_TITLE = AssetImage(**get_asset(self.asset_image_list, "title"))
        self.IMAGE_START = AssetImage(**get_asset(self.asset_image_list, "start"))
        # self.IMAGE_RESULT = AssetImage(**get_asset(self.asset_image_list, "result"))

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
                case "title":
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
                        logger.ui_warn("请检查游戏场景")
                        _flag_title_msg = False
