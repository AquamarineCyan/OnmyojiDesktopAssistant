from src.utils.function import click, random_coor, screenshot
from src.utils.log import logger


class Package:

    scene_name: str = None
    """名称"""
    resource_path: str = None
    """路径"""
    resource_list: list = []
    """资源列表"""

    def __init__(self, n: int = 0) -> None:
        self.n: int = 0
        self.max: int = n

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
