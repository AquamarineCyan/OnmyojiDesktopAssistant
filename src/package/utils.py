import time

from ..utils.decorator import run_in_thread
from ..utils.function import click, random_coor, screenshot
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
    description : str = None
    """功能描述"""

    def __init__(self, n: int = 0) -> None:
        self.n: int = 0
        """当前次数"""
        self.max: int = n
        """总次数"""

    def scene_print(self, scene: str = None) -> None:
        """打印当前场景"""
        if "/" in scene:
            scene = scene.split("/")[-1]
        logger.scene(scene)

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
        """更新一次完成情况"""
        self.n += 1
        logger.num(f"{self.n}/{self.max}")

    def run(self):
        pass

    @run_in_thread
    def start(self):
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
