from src.utils.function import click, random_coor
from src.utils.log import log


class Package:

    scene_name: str = None
    resource_path: str = None  # 路径
    resource_list: list = []  # 资源列表

    def __init__(self, n: int = 0) -> None:
        self.n: int = 0
        self.max: int = n

    def scene_print(self, scene: str = None) -> None:
        """打印当前场景"""
        if "/" in scene:
            scene = scene.split("/")[-1]
        log.ui(f"当前场景: {scene}")

    def start(self, sleeptime: float = 0.4) -> None:
        """挑战开始"""
        coor = random_coor(1067 - 50, 1067 + 50, 602 - 50, 602 + 50)
        click(coor, sleeptime=sleeptime)

    def done(self) -> None:
        """更新一次完成情况"""
        self.n += 1
        log.num(f"{self.n}/{self.max}")
