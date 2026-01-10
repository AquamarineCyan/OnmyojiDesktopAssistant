from enum import Enum

from ..utils.adapter import KeyBoard, Mouse
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.log import logger
from ..utils.paddleocr import OcrData, RuleOcr
from ..utils.point import Point
from .base_package import BasePackage


class State(Enum):
    """初始状态"""

    START = 1
    """初始界面"""
    RUNNING = 2
    """挑战中"""


class SkillLevelCount:
    """技能等级计数器"""

    def __init__(self):
        self.level: int = 1

    def add(self):
        self.level += 1
        logger.ui(f"当前技能层数: {self.level}")

    def set_max(self):
        self.level = 5
        logger.ui(f"当前技能层数: {self.level}（已满级）")

    def reset(self):
        self.level = 1


class MapNodeCount:
    """地图节点计数器"""

    def __init__(self):
        self.node: int = 0
        self.max: int = 20

    def add(self):
        self.node += 1
        logger.ui(f"当前地图节点: {self.node}/{self.max}")

    def reset(self):
        self.node = 0

    def clear(self):
        self.node = 0


class LiuDaoZhiMen(BasePackage):
    """六道之门速刷"""

    scene_name = "六道之门速刷"
    resource_path = "liudaozhimen"
    resource_list: list = [
        "determine",  # 确定
        "fight",  # 挑战
        "fight_choose_skill_refresh",  # 选择技能-刷新
        "quit",  # 退出
        "imitation",  # 仿造
        "open",  # 开启宝箱
        "shop_refresh",  # 商店刷新
        "start",  # 开启挑战
    ]
    title_list: list = ["月之海", "香行域", "错季森", "净佛刹", "真言塔", "孔雀国"]
    """六道列表"""
    ocr_score: float = 0.7
    """文字识别阈值"""
    basic_skill_name: str = "柔风抱暖"
    """基础技能"""

    def __init__(self, n: int = 0) -> None:
        super().__init__(n)
        self.state: State = State.START
        self.map_node_count: MapNodeCount = MapNodeCount()
        self.skill_level_count: SkillLevelCount = SkillLevelCount()

    @staticmethod
    def description() -> None:
        logger.ui("六道之门速刷，目前仅适配：椒图，4柔风，不打星之子的阵容，需要手动勾选“不再提醒”")

    def load_asset(self):
        self.IMAGE_DETERMINE = self.get_image_asset("determine")
        self.IMAGE_FIGHT = self.get_image_asset("fight")
        self.IMAGE_FIGHT_CHOOSE_SKILL_REFRESH = self.get_image_asset("fight_choose_skill_refresh")
        self.IMAGE_IMITATION = self.get_image_asset("imitation")
        self.IMAGE_OPEN = self.get_image_asset("open")
        self.IMAGE_QUIT = self.get_image_asset("quit")
        self.IMAGE_SHOP_REFRESH = self.get_image_asset("shop_refresh")
        self.IMAGE_START = self.get_image_asset("start")

    def check_result_mult(self, list) -> OcrData | None:
        # TODO 概率返回"月""之海"，需要结合上下文判断

        result = RuleOcr().get_raw_result()
        for item in result:
            if item.score > self.ocr_score and item.text in list:
                logger.scene(item.text)
                return item
        return None

    def check_title(self):
        """判断当前场景为六道-月之海"""
        # 如果在六道之门主界面
        if RuleOcr(name="liudaozhimen", keyword="六道之门", score=0.6).match():
            logger.scene("六道之门")
            while True:
                if bool(event_thread):
                    raise GUIStopException

                data = self.check_result_mult(self.title_list)
                if data is None:
                    continue
                if data.text == self.title_list[0]:
                    Mouse.click(data.center)
                    break
            sleep(2)

        # 如果在月之海
        if RuleOcr(name="yuezhihai", keyword="月之海", score=self.ocr_score).match():
            # 开始挑战
            self.check_click(self.IMAGE_START, timeout=3)
            sleep(5)
            # 选择试炼式神
            self.check_click(self.IMAGE_DETERMINE, timeout=3)
            sleep(3)
            # 选择队友
            self.check_click(self.IMAGE_START, timeout=3)
            sleep(3)

    def check_current_scene(self) -> None:
        """判断当前场景，使用状态机记录"""
        result = RuleOcr().get_raw_result()
        for item in result:
            if item.score < self.ocr_score:
                continue
            if "回合后迎战月读" in item.text:
                logger.scene("战斗进行中")
                self.state = State.RUNNING
            if item.text == "六道之门":
                logger.scene("六道之门主界面")
                self.state = State.START

    def choose_initial_skill(self, skill_need_index: int = 1):
        """选择初始技能

        Args:
            skill_need_index (int): 初始技能序号，默认第1个
        """
        initial_skill_counts: int = 0  # 计数器
        result = RuleOcr().get_raw_result()
        for item in result:
            if item.text == "选择":
                initial_skill_counts += 1
                if initial_skill_counts == skill_need_index:
                    logger.ui(f"选择初始技能序号: {initial_skill_counts}")
                    Mouse.click(item.center)
                    self.skill_level_count.reset()
                    self.map_node_count.reset()
                    return
        logger.ui_error("选择初始技能出错")

    def get_current_money(self):
        """获取当前万相铃数量"""
        result = RuleOcr(region=(980, 0, 150, 70)).get_raw_result()
        try:
            for item in result:
                money = int(item.text)
                logger.ui(f"万相铃: {money}")
        except ValueError:
            money = 0
            logger.ui_error("万相铃识别失败")
        return money

    def _fight_blank_space_to_close(self, ocr_result: list[OcrData]) -> bool:
        """点击空白处关闭

        Args:
            ocr_result (list[OcrData]): 识别结果

        Returns:
            bool: 是否点击
        """
        # 可能的识别结果 -> +点击空白处关闭+
        keyword: str = "点击空白处关闭"
        for item in ocr_result:
            if keyword in item.text:
                logger.ui(keyword)
                Mouse.click(item.center)
                return True

        return False

    def _fight_map_choose_handle(self):
        """点击并验证地图节点"""
        logger.scene("地图")

        map_nodes: dict[int, Point] = {
            1: Point(585, 390),  # 1个关卡的中间
            2: Point(820, 400),  # 2个关卡的右侧
            3: Point(635, 330),  # 3个关卡的中间
        }
        self.map_node_numbers = self.map_node_numbers % 3 + 1
        point: Point = map_nodes[self.map_node_numbers]

        logger.ui(f"点击地图节点第{self.map_node_numbers}次")
        Mouse.click(point)

        logger.ui(f"检查是否生效，第{self.map_node_numbers}次")
        sleep(3)
        flag_map_point_counts = True

        new_result = RuleOcr().get_raw_result()
        for item in new_result:
            if item.text == self.title_list[0] or "回合后迎战月读" in item.text:
                flag_map_point_counts = False
                break

        if flag_map_point_counts:
            logger.ui(f"点击地图节点第{self.map_node_numbers}次生效")
            self.map_node_numbers = 0

    def _fight_hundunzhiyu_handle(self, result: list[OcrData]):
        """混沌之屿"""
        logger.scene("混沌之屿")
        flag_has_skill: bool = False
        for item in result:
            if "幸运" in item.text:
                logger.scene("幸运宝匣")
                Mouse.click(item.center)
                sleep(2)
                self.check_click(self.IMAGE_OPEN, timeout=3)
                flag_has_skill = True
                break

        if not flag_has_skill:
            Mouse.click(Point(560, 285))
            sleep(2)
            self.check_click(self.IMAGE_FIGHT, timeout=3)

    def _fight_luzhanzhiyu_handle(self):
        logger.scene("鏖战之屿")
        Mouse.click(Point(650, 270))  # 右侧怪 - 技能
        sleep(2)
        self.check_click(self.IMAGE_FIGHT, timeout=3)

    def _fight_xingzhiyu_handle(self):
        logger.scene("星之屿")
        Mouse.click(Point(380, 270))  # 左侧怪
        sleep(2)
        self.check_click(self.IMAGE_FIGHT, timeout=3)

    def _fight_shenmizhiyu_handle(self, result: list[OcrData]):
        logger.scene("神秘之屿")
        for item in result:
            if item.text == "背包仿造":
                logger.scene("背包仿造")
                #  遍历所有技能
                Mouse.click(Point(760, 210))
                flag_max_skill = True
                sleep(3)

                new_result = RuleOcr().get_raw_result()
                for item in new_result:
                    if item.score < self.ocr_score:
                        continue
                    if item.text == self.basic_skill_name:
                        self.check_click(self.IMAGE_IMITATION, timeout=3)
                        KeyBoard.enter(2)
                        self.skill_level_count.add()
                        sleep(4)
                        Mouse.click()
                        sleep(2)
                        flag_max_skill = False
                        break

                if flag_max_skill:
                    logger.ui("技能已满级")
                    self.skill_level_count.set_max()
                    self.check_click(self.IMAGE_QUIT, timeout=3)
                break

            elif item.text == "技能转换":
                logger.scene("技能转换")
                logger.ui("跳过")
                self.check_click(self.IMAGE_QUIT, timeout=3)
                break

    def _fight_ningxizhiyu_handle(self, result: list[OcrData]):
        logger.scene("宁息之屿")

        def leave():
            logger.ui("离开商店")
            result = RuleOcr().get_raw_result()
            for item in result:
                if item.text == "离开":
                    Mouse.click(item.center)
                    break

        if self.map_node_count.node < 10:
            logger.ui("当前地图节点未达10，跳过商店")
            leave()
            return

        if self.skill_level_count.level >= 5:
            logger.ui("技能等级已满，跳过商店")
            leave()
            return

        for i in range(3):
            # 检查货币
            money = self.get_current_money()
            if money < 300:
                logger.ui("货币不足，离开商店")
                break

            result = RuleOcr().get_raw_result()
            # 选择技能
            for item in result:
                if item.text == self.basic_skill_name:
                    logger.scene(f"选择技能「{self.basic_skill_name}」")
                    Mouse.click(item.center)
                    KeyBoard.enter(1)
                    self.skill_level_count.add()
                    break

            # 刷新
            sleep(2)
            logger.ui(f"刷新商店 第{i + 1}次")
            self.check_click(self.IMAGE_SHOP_REFRESH)
            KeyBoard.enter(1)  # 可能没有「不再提示」

        leave()

    def _fight_choose_skill(self):
        logger.ui("选择技能")

        for i in range(4):
            skill_need: int = 0
            skill_counts: int = 0

            result = RuleOcr().get_raw_result()
            for item in result:
                # 基础技能
                if item.text == self.basic_skill_name:
                    logger.ui(f"选择技能「{self.basic_skill_name}」")
                    # skill_need = 3 #  TODO 使用中心点匹配`选择`按钮` ocr_data.center.x
                    point = item.center
                    point.set_y(217)
                    Mouse.click(point)
                    self.skill_level_count.add()
                    return

                if item.text == "万相之赐":
                    if (
                        self.map_node_count.node > 10
                        and self.skill_level_count.level < 5
                        and self.get_current_money() > 50
                        and i < 3
                    ):
                        break  # 刷新

                    # 最后一次选择
                    logger.ui("选择技能「万相之赐」")
                    skill_need = 4

                elif item.text == "选择":
                    skill_counts += 1
                    if skill_counts == skill_need:
                        Mouse.click(item.center)
                        return

            # 刷新
            sleep(2)
            logger.ui(f"刷新技能 第{i + 1}次")
            self.check_click(self.IMAGE_FIGHT_CHOOSE_SKILL_REFRESH, timeout=3)
            sleep(2)

    def _fight_finish(self):
        logger.scene("结算")
        logger.ui("等待万相赐福")
        sleep(4)

        cannel_point = None  # 记录取消按钮位置
        result = RuleOcr().get_raw_result()
        for item in result:
            if "万相赐福" in item.text:
                logger.scene("万相赐福")
                for item in result:
                    if item.text == "使用":
                        logger.ui("使用万相赐福")
                        Mouse.click(item.center)
                        cannel_point = None
                        break
                    if item.text == "取消":
                        cannel_point = item
                break

        # 检测不到「万相赐福」则点击取消按钮
        if cannel_point:
            logger.ui("万相赐福不足，取消购买")
            Mouse.click(cannel_point.center)

        sleep(2)
        finish_random_left_right()
        sleep()
        Mouse.click()

    def fight(self):
        result = RuleOcr().get_raw_result()
        if self._fight_blank_space_to_close(result):
            return

        for item in result:
            if item.score < self.ocr_score:
                continue

            # 按优先级排序
            elif "回合后迎战月读" in item.text:
                self._fight_map_choose_handle()
                break

            elif item.text == "混沌之屿":
                self.map_node_count.add()
                self._fight_hundunzhiyu_handle(result)
                break

            elif "战之屿" in item.text:
                self.map_node_count.add()
                self._fight_luzhanzhiyu_handle()
                break

            elif item.text == "星之屿":
                self.map_node_count.add()
                self._fight_xingzhiyu_handle()
                break

            elif item.text == "神秘之屿":
                self.map_node_count.add()
                self._fight_shenmizhiyu_handle(result)
                break

            elif item.text == "宁息之屿":
                self.map_node_count.add()
                self._fight_ningxizhiyu_handle(result)
                break

            elif item.text in [self.basic_skill_name, "万相之赐"]:
                self._fight_choose_skill()
                break

            # BOSS战
            elif item.text == "奖励预览":
                logger.scene("BOSS战")
                self.check_click(self.IMAGE_FIGHT, timeout=3)
                sleep(2)

            elif "战斗失败" in item.text:
                logger.ui_warn("战斗失败")
                for item in result:
                    if item.text == "放弃前行":
                        Mouse.click(item.center)
                        KeyBoard.enter(1)
                        break

            # 结算
            elif "击败普通妖怪" in item.text:
                self._fight_finish()
                self.done()
                self.state = State.START

    def run(self):
        self.check_current_scene()  # TODO 3次

        self.map_node_numbers = 0  # 地图上节点的个数

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            # 初始流程
            if self.state == State.START:
                self.check_title()
                sleep()
                self.choose_initial_skill(1)
                self.state = State.RUNNING
                sleep(2)

            self.fight()
            sleep(2)
