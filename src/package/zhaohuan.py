from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import random_sleep
from ..utils.log import logger
from .utils import Package


class ZhaoHuan(Package):
    """普通召唤"""
    scene_name = "普通召唤"
    resource_path = "zhaohuan"
    resource_list = [
        "putongzhaohuan",  # 普通召唤
        "queding",  # 确定
        "title",  # 标题
        "zaicizhaohuan",  # 再次召唤
    ]
    description = "普通召唤，请选择十连次数，请选择合适的召唤屋"

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    def run(self) -> None:
        self.check_title()
        logger.num(f"0/{self.max}")
        self.check_click("putongzhaohuan")
        while self.n < self.max:
            if event_thread.is_set():
                return
            self.done()
            random_sleep(4, 6)
            if self.max == 1:
                break
            self.check_click("zaicizhaohuan")
        self.check_click("queding")
