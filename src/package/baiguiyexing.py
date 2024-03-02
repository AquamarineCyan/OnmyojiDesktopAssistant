from ..utils.coordinate import RelativeCoor
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import (
    click,
    random_coor,
    random_num,
    random_sleep
)
from ..utils.log import logger
from ..utils.window import window
from .utils import Package


class BaiGuiYeXing(Package):
    """百鬼夜行"""
    scene_name = "百鬼夜行"
    resource_path = "baiguiyexing"
    resource_list = [
        "title",  # 标题
        "jinru",  # 进入
        "ya",  # 押选
        "kaishi",  # 开始
        "baiguiqiyueshu",  # 百鬼契约书
    ]
    description = "仅适用于清票，无法指定鬼王"

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    def check_title(self) -> bool:
        """场景"""
        _flag_title_msg = True
        while True:
            if event_thread.is_set():
                return
            coor = self.get_coor_info("title")
            if coor.is_effective:
                logger.scene(self.scene_name)
                return
            elif _flag_title_msg:
                _flag_title_msg = False
                logger.ui("请检查游戏场景", "warn")

    def start(self):
        """开始"""
        self.check_click("jinru")

    def choose(self):
        """鬼王选择"""
        _x1_left = 230
        _x1_right = 260
        _x2_left = 560
        _x2_right = 590
        _x3_left = 880
        _x3_right = 910
        _y1 = 300
        _y2 = 550
        while True:
            if event_thread.is_set():
                return
            m = random_num(1, 4)
            if m < 2:
                x1 = _x1_left
                x2 = _x1_right
            elif m < 3:
                x1 = _x2_left
                x2 = _x2_right
            else:
                x1 = _x3_left
                x2 = _x3_right
            x, y = random_coor(x1, x2, _y1, _y2).coor
            click(RelativeCoor(x, y))
            random_sleep()
            coor = self.get_coor_info("ya")
            if coor.is_effective:
                logger.ui("已选择鬼王")
                break
        self.check_click("kaishi")

    def fighting(self):
        """砸豆子"""
        random_sleep()
        for _ in range(250, 0, -5):
            if event_thread.is_set():
                return
            random_sleep(0.2, 1)
            x, y = random_coor(
                60,
                window.window_standard_width - 120,
                300,
                window.window_standard_height - 100
            ).coor
            click(RelativeCoor(x, y), dura=0.25)

    def finish(self):
        """结束"""
        while True:
            if event_thread.is_set():
                return
            coor = self.get_coor_info("baiguiqiyueshu")
            random_sleep()
            if coor.is_effective:
                self.screenshot()
                click(coor)
                break

    def run(self):
        self.check_title()
        logger.num(f"0/{self.max}")
        random_sleep(1, 3)

        while self.n < self.max:
            if event_thread.is_set():
                return
            random_sleep(0, 2)
            self.start()
            random_sleep(1, 3)
            self.choose()
            random_sleep(2, 4)
            self.fighting()
            random_sleep(2, 4)
            self.finish()
            self.done()
            random_sleep(3)
            # TODO 更新随机判断
            if self.n in {12, 25, 39}:
                random_sleep(10, 20)
