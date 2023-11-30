import time

from ..utils.decorator import run_in_thread
from ..utils.event import event_thread
from ..utils.function import (
    RESOURCE_FIGHT_PATH,
    check_click,
    check_scene_multiple_once,
    click,
    finish_random_left_right,
    get_coor_info,
    random_coor,
    random_sleep,
    screenshot
)
from ..utils.log import logger
from ..utils.mysignal import global_ms as ms
from ..utils.toast import toast


class Package:

    scene_name: str = None
    """名称"""
    resource_path: str = None
    """路径"""
    resource_list: list = []
    """资源列表"""
    description: str = None
    """功能描述"""

    def __init__(self, n: int = 0) -> None:
        self.n: int = 0
        """当前次数"""
        self.max: int = n
        """总次数"""
        self.current_resource_list: list = None
        """当前使用的资源列表"""

    def get_coor_info(self, file):
        return get_coor_info(f"{self.resource_path}/{file}")

    def check_click(self, file, *args, **kwargs):
        return check_click(f"{self.resource_path}/{file}", *args, **kwargs)

    def check_scene_multiple_once(self, *args, **kwargs):
        return check_scene_multiple_once(self.current_resource_list, *args, **kwargs)

    def scene_print(self, scene: str = None) -> None:  # FIXME remove
        """打印当前场景"""
        if "/" in scene:
            scene = scene.split("/")[-1]
        logger.scene(scene)

    def scene_handle(self, scene: str = None) -> str:
        logger.info(f"current scene: {scene}")
        if "/" in scene:
            scene = scene.split("/")[-1]
        return scene

    def log_current_scene_list(self) -> None:
        """记录当前匹配的资源列表"""
        if self.current_resource_list is None:
            return
        logger.info(f"current_resource_list: {len(self.current_resource_list)}")
        for item in self.current_resource_list:
            logger.info(item)

    def start(self, sleeptime: float = 0.4) -> None:
        """挑战开始"""
        coor = random_coor(1067 - 50, 1067 + 50, 602 - 50, 602 + 50)
        click(coor, sleeptime=sleeptime)

    def screenshot(self) -> None:
        _screenshot_path = self.resource_path
        if self.resource_path is None:
            _screenshot_path = "cache"
        screenshot(_screenshot_path)

    def done(self) -> None:
        """更新一次完成次数"""
        self.n += 1
        logger.num(f"{self.n}/{self.max}")

    def ensure_finish(self):
        """确保结束"""
        logger.ui("结束")
        random_sleep(0.4, 0.8)
        finish_random_left_right()
        while True:
            if event_thread.is_set():
                return
            coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")
            # 未重复检测到，表示成功点击
            if coor.is_zero:
                self.done()
                break
            click()
            random_sleep(0.4, 0.8)

    def run(self):
        """任务内容"""
        pass

    @run_in_thread
    def task_start(self):
        """任务开始"""
        # 禁用按钮
        ms.main.is_fighting_update.emit(True)
        start = time.perf_counter()
        self.run()
        end = time.perf_counter()
        try:
            if end - start >= 60:
                logger.ui(f"耗时{int((end - start) // 60)}分{int((end - start) % 60)}秒")
            else:
                logger.ui(f"耗时{int(end - start)}秒")
        except Exception:
            logger.error("耗时统计计算失败")
        # 启用按钮
        ms.main.is_fighting_update.emit(False)
        logger.ui(f"已完成 {self.scene_name} {self.n}次")
        # 系统通知
        # 5s结束，保留至通知中心
        toast("任务已完成")
