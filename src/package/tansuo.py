from ..utils.adapter import KeyBoard, Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, random_normal, random_num, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from ..utils.point import RelativePoint
from ..utils.window import window_manager
from .utils import Package


class TanSuo(Package):
    """探索"""

    scene_name = "探索"
    resource_path = "tansuo"
    resource_list = [
        "chuzhanxiaohao",
        "fighting",
        "fighting_boss",
        "kunnan_big",
        "quit",
        "quit_true",
        "tansuo",
        "tansuo_28",
        "tansuo_28_0",
        "tansuo_28_title",
        "treasure_box",
    ]

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    @staticmethod
    def description() -> None:
        logger.ui("提前准备好自动轮换和加成，仅单人探索")

    def load_asset(self):
        self.IMAGE_START = self.get_image_asset("tansuo")
        self.IMAGE_CHUZHANXIAOHAO = self.get_image_asset("chuzhanxiaohao")
        self.IMAGE_FIGHT_BOSS = self.get_image_asset("fight_boss")
        self.IMAGE_FIGHT_LITTLE_MONSTER = self.get_image_asset("fight_little_monster")
        self.IMAGE_KUNNAN_BIG = self.get_image_asset("kunnan_big")
        self.IMAGE_QUIT_TRUE = self.get_image_asset("quit_true")
        self.IMAGE_TREASURE_BOX = self.get_image_asset("treasure_box")
        self.IMAGE_QUIT = self.get_image_asset("quit")
        self.IMAGE_TANSUO_28_0 = self.get_image_asset("tansuo_28_0")
        self.IMAGE_TANSUO_28 = self.get_image_asset("tansuo_28")
        self.IMAGE_TITLE_28 = self.get_image_asset("tansuo_28_title")

    @log_function_call
    def check_title(self) -> None:
        msg_title = True
        self.current_asset_list = [
            self.IMAGE_CHUZHANXIAOHAO,
            self.IMAGE_TANSUO_28,
            self.IMAGE_TANSUO_28_0,
            self.IMAGE_TITLE_28,
        ]
        self.log_current_asset_list()

        while True:
            if bool(event_thread):
                raise GUIStopException

            if image := check_image_once(self.current_asset_list):
                logger.info(f"current image name: {image.name}")
                return
            if msg_title:
                msg_title = False
                self.title_error_msg()

    @log_function_call
    def fight(self) -> None:
        flag_done: bool = False  # 是否已经结束
        point = None
        sleep(2)
        while True:
            if bool(event_thread):
                raise GUIStopException

            # 如果匹配到小怪的按钮，返回上一级
            if not flag_done and RuleImage(self.IMAGE_FIGHT_LITTLE_MONSTER).match():
                logger.ui_warn("未进入战斗，重新匹配")
                return

            if check_image_once(
                [
                    # self.global_image.IMAGE_VICTORY,
                    self.global_assets.IMAGE_FINISH,
                    self.global_assets.IMAGE_FAIL,
                ]
            ):
                flag_done = True
                if point is None:
                    point = finish_random_left_right()
                else:
                    Mouse.click(point)
                sleep(2)
            elif flag_done:  # 没有匹配到图像，说明已经结束结算
                logger.ui("战斗结束")
                return

    @log_function_call
    def finish(self) -> None:
        """boss战后的结束阶段

        1.有掉落物，不需要点击，直接左上角退出即可

        2.无掉落物，系统自动跳转出去

        3.1、2出来之后，存在宝箱/妖气封印的可能，当前章节的小界面被关闭，需要右侧列表重新点开
        """
        while True:
            if bool(event_thread):
                raise GUIStopException

            # 等待加载完毕
            sleep(1.5, 2)

            # 如果还在探索里，说明有掉落物，直接退出
            if RuleImage(self.IMAGE_CHUZHANXIAOHAO).match():
                logger.ui("有掉落物，直接退出")
                KeyBoard.esc(1)
                self.check_click(self.IMAGE_QUIT_TRUE)

            # 在探索进入的前置界面
            else:
                image = RuleImage(self.IMAGE_START)
                image_treasure_box = RuleImage(self.IMAGE_TREASURE_BOX)
                if image.match():
                    logger.ui("探索结束")
                # 宝箱
                elif image_treasure_box.match():
                    Mouse.click(image_treasure_box.center_point())
                    Mouse.click(wait=2)
                # 不管有没有宝箱，都退出这次探索
                return

    def run(self):
        self.check_title()
        self.current_asset_list = [
            self.IMAGE_CHUZHANXIAOHAO,
            self.IMAGE_TANSUO_28_0,
            self.IMAGE_TITLE_28,
            self.IMAGE_KUNNAN_BIG,
            self.IMAGE_START,
        ]

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            logger.info(f"current result name: {result.name}")
            match result.name:
                case self.IMAGE_TANSUO_28_0.name:  # 右侧列表按钮
                    Mouse.click(result.center_point())
                    sleep()

                case self.IMAGE_TITLE_28.name:
                    self.check_click(self.IMAGE_START)
                    sleep(2)

                case self.IMAGE_CHUZHANXIAOHAO.name:
                    # 先判断boss面灵气
                    sleep()
                    result = RuleImage(self.IMAGE_FIGHT_BOSS)
                    if result.match():
                        Mouse.click(result.center_point())
                        logger.ui("BOSS")
                        self.fight()
                        self.finish()
                        self.done()

                    else:
                        result = RuleImage(self.IMAGE_FIGHT_LITTLE_MONSTER)
                        if result.match(score=0.6):
                            Mouse.click(result.center_point())
                            logger.ui("小怪")
                            self.fight()
                        else:
                            logger.ui("移动视角")
                            sleep()
                            y1 = 300
                            y2 = 550
                            x_middle = window_manager.current.window_width // 2
                            x_right = int(window_manager.current.window_width * 0.9)
                            x = random_normal(x_middle, x_right)
                            # 移动到窗口中心线右侧
                            Mouse.move(
                                point=RelativePoint(x, random_num(y1, y2)),
                                duration=random_num(0.5, 0.8),
                            )
                            Mouse.drag((x_middle - x) * 2, 0, random_num(0.5, 0.8))
                            logger.info(f"move width: {(x_middle - x) * 2}")
