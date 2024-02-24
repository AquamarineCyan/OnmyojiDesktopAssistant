import time

from ..utils.config import config
from ..utils.decorator import run_in_thread
from ..utils.event import event_thread, event_xuanshang
from ..utils.function import click, get_coor_info_center
from ..utils.log import logger
from ..utils.myschedule import global_scheduler
from ..utils.toast import toast
from .utils import Package


class XuanShangFengYin(Package):
    """悬赏封印"""
    scene_name = "悬赏封印"
    resource_path = "xuanshangfengyin"
    resource_list: list = [
        "title",  # 特征图像
        "xuanshang_accept",  # 接受
        "xuanshang_refuse",  # 拒绝
        "xuanshang_ignore",  # 忽略
    ]
    STATE_STOP = 1
    STATE_START = 2

    def __init__(self):
        self._flag_is_first: bool = True
        self._flag: bool = False
        self.state = self.STATE_STOP
        event_xuanshang.set()

    def check_click(self, file: str, timeout: int = None) -> None:
        """图像识别，并点击

        参数:
            file (str): 文件路径&图像名称（*.png）
            timeout (int): 超时时间（秒）
        """
        if timeout:
            start_time = time.time()
        while True:
            if event_thread.is_set():
                return
            if timeout:
                current_time = time.time()
                if current_time - start_time > timeout:
                    return

            coor = get_coor_info_center(f"{self.resource_path}/{file}", is_log=False)
            if coor.is_effective:
                click(coor)
                return

    def scheduler_check(self):
        if config.config_user.xuanshangfengyin == "关闭":
            return

        coor = get_coor_info_center(f"{self.resource_path}/title.png", is_log=False)
        if coor.is_effective:
            event_xuanshang.clear()
            logger.scene(self.scene_name)
            logger.ui("已暂停后台线程，等待处理", "warn")
            toast("悬赏封印", "检测到悬赏封印")

            self._flag = True
            match config.config_user.xuanshangfengyin:
                case "接受":
                    _msg = "接受协作"
                    _filename = "xuanshang_accept"
                case "拒绝":
                    _msg = "拒绝协作"
                    _filename = "xuanshang_refuse"
                case "忽略":
                    _msg = "忽略协作"
                    _filename = "xuanshang_ignore"
                case _:
                    _msg = "用户配置出错，自动接受协作"
                    _filename = "xuanshang_accept"
            logger.ui(_msg)
            self.check_click(_filename, 5)
            event_xuanshang.set()
        else:
            event_xuanshang.set()
            if self._flag:
                self._flag = False
                logger.ui("悬赏封印已消失，恢复线程")

    @run_in_thread
    def task_start(self):
        if config.config_user.xuanshangfengyin == "关闭":
            if global_scheduler.get_job(self.resource_path):
                logger.ui("检测到悬赏封印已关闭，停止定时任务")
                global_scheduler.remove_job(self.resource_path)
                self.state = self.STATE_STOP
        elif self.state == self.STATE_STOP:
            # 添加定时任务，间隔1分钟，同一时间只有一个实例在运行
            global_scheduler.add_job(
                self.scheduler_check,
                "interval", seconds=1,
                id=self.resource_path,
                coalesce=True
            )
            self.state = self.STATE_START


task_xuanshangfengyin = XuanShangFengYin()
