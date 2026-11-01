import re

from ..utils.adapter import Mouse
from ..utils.config import config
from ..utils.coordinate import reference_size
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import DailyLimitException, GUIStopException
from ..utils.function import finish_random_left_right, random_normal, random_num, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from ..utils.ocr_engine import RuleOcr
from ..utils.point import Point
from ..utils.window import window_manager
from .base_package import BasePackage

_TARGET_CHAPTER = 28
"""默认目标章节（CPU 模型可识别第二十八章）"""

_MAX_SCROLL_TIMES = 15
"""最大滚动次数，防止识别异常时死循环"""


def _target_chapter() -> int:
    """GPU 版模型识别不到「第二十八章」，目标降为第二十七章，靠兜底滚动补足"""
    return 27 if config.is_gpu else _TARGET_CHAPTER


def _parse_chapter(text: str) -> int | None:
    """解析「第X章」中的章节号，未匹配返回 None"""
    cn_digits = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    match = re.search(r"第([一二三四五六七八九十]+)章", text)  # 游戏内只有中文数字
    if not match:
        return None
    num = match.group(1)
    if "十" in num:
        tens, _, ones = num.partition("十")
        return (int(cn_digits[tens]) if tens else 1) * 10 + (int(cn_digits[ones]) if ones else 0)
    return int(cn_digits[num])


class TanSuo(BasePackage):
    """探索"""

    scene_name = "探索"
    resource_path = "tansuo"
    resource_list = (
        "chuzhanxiaohao",
        "fighting",
        "fighting_boss",
        "quit_true",
        "tansuo",
        "tansuo_28",
        "tansuo_28_0",
        "tansuo_28_title",
        "treasure_box",
    )

    @log_function_call
    def __init__(self, n: int = 0, temp_pop: bool = False) -> None:
        super().__init__(n)
        self.has_temp_pop = temp_pop
        if self.has_temp_pop:
            logger.ui("已启用临时弹窗关闭功能")
        self.start_click_count = 0  # 连续点击IMAGE_START的次数

    @staticmethod
    def description() -> None:
        logger.ui("提前准备好自动轮换和加成，仅单人探索第二十八章。")

    def load_asset(self):
        self.IMAGE_START = self.get_image_asset("start")
        self.IMAGE_CHUZHANXIAOHAO = self.get_image_asset("chuzhanxiaohao")
        self.IMAGE_FIGHT_BOSS = self.get_image_asset("fight_boss")
        self.IMAGE_FIGHT_LITTLE_MONSTER = self.get_image_asset("fight_little_monster")
        self.IMAGE_QUIT = self.get_image_asset("quit")
        self.IMAGE_QUIT_TRUE = self.get_image_asset("quit_true")
        self.IMAGE_TREASURE_BOX = self.get_image_asset("treasure_box")
        self.IMAGE_TANSUO_28 = self.get_image_asset("tansuo_28")
        self.IMAGE_TITLE_28 = self.get_image_asset("title_28")

    def get_chapter_number(self) -> int | None:
        """返回当前界面可见的最大章节号，未识别到返回 None"""
        # 章节列表固定在右侧，只识别 x>=900 的区域，减少全屏 OCR 开销；
        x = 900
        width, height = window_manager.current.client_width, window_manager.current.client_height
        result = RuleOcr(region=(x, 0, width - x, height)).get_raw_result()
        chapters = [n for item in result if (n := _parse_chapter(item.text)) is not None]
        return max(chapters) if chapters else None

    def scroll_to_target_chapter(self) -> bool:
        """滚动章节列表到目标章节，返回是否正常识别到章节列表

        默认目标是第二十八章；GPU 版模型识别不到第二十八章，目标降为第二十七章，
        并在到达后兜底滚两格，保证第二十八章也露出。每滚一次都重新识别。
        """
        target = _target_chapter()
        chapter = self.get_chapter_number()
        if chapter is None:
            self.title_error_msg()
            return False
        if chapter >= target:
            logger.info(f"当前第{chapter}章，无需滚动")
            return True

        logger.ui(f"当前停留第{chapter}章，滚动到第{target}章")
        # 滚轮落点需在章节列表上，move 只需一次，后续滚动都作用于此
        Mouse.move(point=Point(1030, 340))
        for _ in range(_MAX_SCROLL_TIMES):
            if bool(event_thread):
                raise GUIStopException
            Mouse.scroll(-3 * 120)  # 向下3格

            self.sleep_interval()
            chapter = self.get_chapter_number()
            if chapter is None:
                logger.info("滚动后未识别到章节，继续滚动")
                continue
            if chapter >= target:
                logger.ui(f"已滚动到第{chapter}章")
                if config.is_gpu:
                    # GPU 版模型识别不到「第二十八章」，兜底再滚两格
                    logger.info("兜底再滚动两格")
                    Mouse.scroll(-120 * 2)
                    self.sleep_interval()
                return True
            logger.info(f"当前第{chapter}章，继续滚动")
        logger.ui_error(f"滚动次数超限，仍未到达第{target}章")
        return True

    def check_title(self) -> None:
        msg_title: bool = False

        msg_title = self.scroll_to_target_chapter()

        self.current_asset_list = [
            self.IMAGE_CHUZHANXIAOHAO,
            self.IMAGE_TANSUO_28,
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
            # 如果匹配到临时弹窗，点击关闭
            if self.has_temp_pop and RuleImage(self.global_assets.IMAGE_TEMP_POP).match():
                finish_random_left_right()
                logger.ui("关闭临时弹窗")
                sleep(2)
                continue

            _result = check_image_once(
                [
                    # self.global_image.IMAGE_VICTORY,
                    self.global_assets.IMAGE_FINISH,
                    *self.global_assets.ALL_FAIL_IMAGES,
                ]
            )
            if _result:
                flag_done = True
                logger.ui(f"战斗结束{('（' + _result.description + '）') if _result.description else ''}")
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
                self.check_click(self.IMAGE_QUIT, timeout=3)
                sleep(1)
                self.check_click(self.IMAGE_QUIT_TRUE, timeout=5)

            # 在探索进入的前置界面
            else:
                image_start = RuleImage(self.IMAGE_START)
                image_treasure_box = RuleImage(self.IMAGE_TREASURE_BOX)
                if image_start.match():
                    logger.ui("探索结束")
                # 宝箱
                elif image_treasure_box.match(logger_lever="ERROR"):
                    Mouse.click(image_treasure_box.center_point())
                    logger.info("获得宝箱")
                    Mouse.click(wait=2)
                else:
                    logger.ui_warn("未发现宝箱")

                # 不管有没有宝箱，都退出这次探索
                logger.ui("本轮探索结束")
                return

    def run(self):
        self.check_title()
        self.current_asset_list = [
            self.IMAGE_CHUZHANXIAOHAO,
            self.IMAGE_TANSUO_28,
            self.IMAGE_TITLE_28,
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
                case self.IMAGE_TANSUO_28.name:  # 右侧列表按钮
                    Mouse.click(result.center_point())
                    sleep(3)  # 等待行动动画

                case self.IMAGE_TITLE_28.name:
                    logger.ui("准备进入探索")
                    self.check_click(self.IMAGE_START)
                    self.start_click_count += 1
                    if self.start_click_count >= 3:
                        logger.ui_warn("尝试进入探索失败3次")
                        self.start_click_count = 0  # 重置计数器
                        raise DailyLimitException("探索次数已达本日上限")
                    sleep(2)

                case self.IMAGE_CHUZHANXIAOHAO.name:
                    self.start_click_count = 0  # 成功进入探索，重置计数器
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
                            x_middle = reference_size()[0] // 2
                            x_right = int(reference_size()[0] * 0.9)
                            x = random_normal(x_middle, x_right)
                            # 移动到窗口中心线右侧
                            Mouse.move(
                                point=Point(x, random_num(y1, y2)),
                                duration=random_num(0.5, 0.8),
                            )
                            Mouse.drag((x_middle - x) * 2, 0, random_num(0.5, 0.8))
                            logger.info(f"move width: {(x_middle - x) * 2}")
