from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import (
    RESOURCE_FIGHT_PATH,
    check_click,
    check_scene,
    click,
    finish,
    finish_random_left_right,
    get_coor_info,
    is_passengers_on_position,
    random_sleep,
    result
)
from ..utils.log import logger
from ..utils.window import window
from .utils import Package


class RiLun(Package):
    """日轮副本"""
    scene_name = "日轮副本"
    resource_path = "rilun"
    resource_yuhun_path: str = "yuhun"  # 御魂路径，复用资源
    resource_list: list = [
        "fighting",  # 对局进行中
    ]

    @log_function_call
    def __init__(self, n: int = 0, flag_driver: bool = False, flag_passengers: int = 2) -> None:
        super().__init__(n)
        self.flag_driver: bool = flag_driver  # 是否为司机（默认否）
        self.flag_passengers: bool = flag_passengers  # 组队人数
        self.flag_driver_start: bool = False  # 司机待机
        self.flag_fighting: bool = False  # 是否进行中对局（默认否）

    def check_title(self) -> bool:
        """场景"""
        _flag_title_msg = True
        while True:
            if event_thread.is_set():
                return
            if check_scene(f"{self.resource_yuhun_path}/xiezhanduiwu", timeout=0.5):
                self.flag_driver_start = True
                return
            elif check_scene(f"{self.resource_yuhun_path}/fighting", timeout=0.5):
                self.flag_fighting = True
                return
            elif _flag_title_msg:
                _flag_title_msg = False
                self.title_error_msg()

    def finish(self) -> None:
        """结束"""
        result()
        random_sleep(1.5, 3)
        coor = finish_random_left_right(is_click=False)
        import pyautogui
        while True:
            if event_thread.is_set():
                return
            pyautogui.moveTo(
                coor.x + window.window_left,
                coor.y + window.window_top,
                duration=0.25
            )
            pyautogui.doubleClick()
            if finish():
                while True:
                    if event_thread.is_set():
                        return
                    random_sleep()
                    click()
                    random_sleep()
                    coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")
                    if coor.is_zero:
                        break
                break
            random_sleep(0.4, 0.8)

    def run(self) -> None:
        self.check_title()
        logger.num(f"0/{self.max}")
        while self.n < self.max:
            if event_thread.is_set():
                return
            # 司机
            if self.flag_driver and self.flag_driver_start:
                is_passengers_on_position(self.flag_passengers)
                # 开始挑战
                check_click(f"{RESOURCE_FIGHT_PATH}/start_team", dura=0.25)
                logger.ui("开始")
            if not self.flag_fighting:
                check_click(f"{self.resource_path}/fighting", False)
                self.flag_fighting = False
                logger.ui("对局进行中")
            self.finish()
            self.done()
            random_sleep()
