from ..utils.adapter import KeyBoard, Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.log import logger
from ..utils.paddleocr import OcrData, ocr
from ..utils.point import RelativePoint
from .utils import Package


class LiuDaoZhiMen(Package):
    """六道之门速刷"""

    scene_name = "六道之门速刷"
    resource_path = "liudaozhimen"
    resource_list: list = [
        "determine",  # 确定
        "fight",  # 挑战
        "fight_ready_quit",  # 退出
        "fight_ready_refresh",  # 技能装备-刷新
        "fight_ready_reset",  # 技能装备-重置
        "imitation",  # 仿造
        "open",  # 开启宝箱
        "shop_refresh",  # 商店刷新
        "start",  # 开启挑战
    ]
    STATE_START = 1
    STATE_RUNNING = 2

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)
        self.state = self.STATE_START

    @staticmethod
    def description() -> None:
        logger.ui("六道之门速刷，目前仅适配：椒图，4柔风，不打星之子的阵容，需要手动勾选“不再提醒”")

    def load_asset(self):
        self.IMAGE_DETERMINE = self.get_image_asset("determine")
        self.IMAGE_FIGHT_READY_QUIT = self.get_image_asset("fight_ready_quit")
        self.IMAGE_FIGHT_READY_REFRESH = self.get_image_asset("fight_ready_refresh")
        self.IMAGE_FIGHT_READY_RESET = self.get_image_asset("fight_ready_reset")
        self.IMAGE_FIGHT = self.get_image_asset("fight")
        self.IMAGE_IMITATION = self.get_image_asset("imitation")
        self.IMAGE_OPEN = self.get_image_asset("open")
        self.IMAGE_SHOP_REFRESH = self.get_image_asset("shop_refresh")
        self.IMAGE_START = self.get_image_asset("start")

    def check_ocr_result(self, text: str | list = None) -> OcrData | None:
        result = ocr.get_raw_result()
        for item in result:
            ocr_data = OcrData(item)
            if ocr_data.score < 0.8:
                continue
            if (isinstance(text, str) and ocr_data.text == text) or (isinstance(text, list) and ocr_data.text in text):
                logger.scene(ocr_data.text)
            return ocr_data
        return None

    def check_result_once(self, text):
        result = ocr.get_raw_result()
        for item in result:
            ocr_data = OcrData(item)
            if ocr_data.score > 0.8 and ocr_data.text == text:
                # click(RelativePoint(ocr_data.x1, ocr_data.y1).rela_to_abs())
                return ocr_data
        return None

    def check_result_mult(self, list):
        # TODO 概率返回"月""之海"，需要结合上下文判断
        result = ocr.get_raw_result()
        for item in result:
            ocr_data = OcrData(item)
            if ocr_data.score > 0.8 and ocr_data.text in list:
                logger.scene(ocr_data.text)
                return ocr_data
        return None

    def check_title(self):
        """判断当前场景为六道-月之海"""
        # 如果在六道之门主界面
        if self.check_result_once("六道之门"):
            while True:
                if bool(event_thread):
                    raise GUIStopException

                data = self.check_result_mult(["月之海", "香行域", "错季森", "净佛刹", "真言塔", "孔雀国"])
                if data is None:
                    continue
                if data.text == "月之海":
                    Mouse.click(data.center)
                    break
            sleep(2)

        if self.check_result_once("月之海"):
            # 如果在月之海
            self.check_click(self.IMAGE_START, timeout=3)
            # 跳转
            sleep(2)
            # 选择试炼式神
            self.check_click(self.IMAGE_DETERMINE, timeout=3)
            # 选择队友
            self.check_click(self.IMAGE_START, timeout=3)

    def check_current_scene(self) -> int:
        """判断当前场景，使用状态机记录"""
        result = ocr.get_raw_result()
        for item in result:
            ocr_data = OcrData(item)
            if ocr_data.score < 0.8:
                continue
            if "回合后迎战月读" in ocr_data.text:
                logger.scene("战斗进行中")
                return self.STATE_RUNNING
            if ocr_data.text == "六道之门":
                logger.scene("六道之门主界面")
                return self.STATE_START

    def choose_initial_buff(self, initial_buff_need: int = 1):
        initial_buff_counts = 0
        result = ocr.get_raw_result()
        for item in result:
            ocr_data = OcrData(item)
            if ocr_data.text == "选择":
                initial_buff_counts += 1
                if initial_buff_counts == initial_buff_need:
                    logger.scene(f"选择初始BUFF{initial_buff_counts}")
                    Mouse.click(ocr_data.center)
                    return
        logger.ui_error("选择初始BUFF出错")

    def fight(self):
        # TODO 判断地图上的点位 文字识别&图像识别均失败 使用固定坐标范围
        fight_buff_counts = 0
        fight_buff_need = 0

        flag_already_reset = False

        result = ocr.get_raw_result()
        for item in result:
            ocr_data = OcrData(item)
            logger.ui(ocr_data.text)
            if ocr_data.score < 0.8:
                continue

            # 按优先级排序
            if "点击空白处关闭" in ocr_data.text:
                # 识别结果为"+点击空白处关闭+"
                logger.scene("点击空白处关闭")
                Mouse.click(ocr_data.center)
                break

            elif "回合后迎战月读" in ocr_data.text:
                logger.scene("地图")
                self.map_node_numbers += 1
                # 重新选择地图节点
                if self.map_node_numbers > 3:
                    self.map_node_numbers = 1
                if self.map_node_numbers == 1:
                    _coor = RelativePoint(585, 420)
                if self.map_node_numbers == 2:
                    # 2个关卡的右侧
                    _coor = RelativePoint(820, 430)
                if self.map_node_numbers == 3:
                    # 3个关卡的中间
                    _coor = RelativePoint(635, 360)
                logger.ui(f"点击地图坐标{_coor.coor}")
                Mouse.click(_coor)

                logger.ui(f"检查是否生效，第{self.map_node_numbers}次")
                sleep()
                new_result = ocr.get_raw_result()
                flag_map_coor_counts = True
                for item in new_result:
                    ocr_data = OcrData(item)
                    if "回合后迎战月读" in ocr_data.text:
                        flag_map_coor_counts = False
                        break
                if flag_map_coor_counts:
                    logger.ui(f"地图点击第{self.map_node_numbers}次生效")
                    self.map_node_numbers = 0
                break

            elif ocr_data.text == "混沌之屿":
                logger.scene("混沌之屿")
                flag_has_buff = False
                for item in result:
                    ocr_data = OcrData(item)
                    if ocr_data.text in [
                        "幸运宝匣",
                        "幸运宝厘",
                        "幸运宝匝",
                        "幸运宝画",
                    ]:
                        logger.scene("幸运宝匣")
                        Mouse.click(ocr_data.center)
                        sleep(2)
                        self.check_click(self.IMAGE_OPEN, timeout=3)
                        flag_has_buff = True
                        break
                if not flag_has_buff:
                    Mouse.click(RelativePoint(560, 315))
                    self.check_click(self.IMAGE_FIGHT, timeout=3)
                break
            elif "战之屿" in ocr_data.text:
                logger.scene("鏖战之屿")
                _coor = RelativePoint(650, 300)  # 右侧怪 - 技能BUFF
                Mouse.click(_coor)
                self.check_click(self.IMAGE_FIGHT, timeout=3)
                break
            elif ocr_data.text == "星之屿":
                logger.scene("星之屿")
                Mouse.click(RelativePoint(380, 300))  # 左侧怪
                self.check_click(self.IMAGE_FIGHT, timeout=3)
                break
            elif ocr_data.text == "神秘之屿":
                logger.scene("神秘之屿")
                for item in result:
                    ocr_data = OcrData(item)
                    if ocr_data.text == "背包仿造":
                        logger.scene("背包仿造")
                        #  遍历所有buff
                        Mouse.click(RelativePoint(760, 240))
                        flag_max_buff = True
                        new_result = ocr.get_raw_result()
                        for item in new_result:
                            ocr_data = OcrData(item)
                            logger.ui(ocr_data.text)
                            if ocr_data.score < 0.8:
                                continue
                            if ocr_data.text == "柔风抱暖":
                                self.check_click(self.IMAGE_IMITATION, timeout=3)
                                KeyBoard.enter(1)
                                sleep()
                                Mouse.click()
                                flag_max_buff = False
                                break
                        if flag_max_buff:
                            logger.ui("buff已满级")
                            self.check_click(self.IMAGE_FIGHT_READY_QUIT, timeout=3)
                        break
                    elif ocr_data.text == "技能转换":
                        logger.scene("技能转换")
                        logger.ui_warn("未来可期")
                        self.check_click(self.IMAGE_FIGHT_READY_QUIT, timeout=3)
                        break
                break
            elif ocr_data.text == "宁息之屿":
                logger.scene("宁息之屿")
                if self.shop_refresh_counts == 3:
                    logger.scene("离开商店")
                    for item in result:
                        ocr_data = OcrData(item)
                        if ocr_data.text == "离开":
                            Mouse.click(ocr_data.center)
                            break
                    logger.ui("刷新商店次数用完")
                    self.shop_refresh_counts = 0
                    break
                # 所有需要的BUFF
                for item in result:
                    ocr_data = OcrData(item)
                    if ocr_data.text == "柔风抱暖":
                        logger.scene("BUFF选取柔风抱暖")
                        Mouse.click(ocr_data.center)
                        KeyBoard.enter(1)
                        break
                sleep()
                self.check_click(self.IMAGE_SHOP_REFRESH)
                logger.ui(f"刷新商店第{self.shop_refresh_counts}次")
                self.shop_refresh_counts += 1
                # 可能没有"不再提示"
                KeyBoard.enter(1)
                # 需要重新识别，防止和战斗后的选取BUFF冲突
                break

            # 不能break，需要遍历当前所有的BUFF
            elif ocr_data.text in ["柔风抱暖", "万相之赐"]:
                if ocr_data.text == "柔风抱暖":
                    logger.scene("柔风抱暖")
                    # fight_buff_need = 3
                    _coor = ocr_data.center
                    _coor.y += 217
                    Mouse.click(_coor)
                if ocr_data.text == "万相之赐":
                    logger.scene("万相之赐")
                    fight_buff_need = 4
            elif ocr_data.text == "选择":
                logger.scene("选择BUFF")
                fight_buff_counts += 1  # TODO
                if fight_buff_counts == fight_buff_need:
                    Mouse.click(ocr_data.center)

            # BOSS战
            elif ocr_data.text == "奖励预览":
                for item in result:
                    ocr_data = OcrData(item)
                    # if ocr_data.text == ["备战", "奋战", "画战"]:  # score过低
                    # click(ocr_data)
                    # break
                    if ocr_data.text == "当前装配":
                        _coor = ocr_data.center
                        _coor.x -= 80
                        Mouse.click(_coor)
                        break
                break
            elif ocr_data.text == "备战":
                logger.scene("备战")
                self.check_click(self.IMAGE_FIGHT_READY_REFRESH, timeout=3)
                break
            elif ocr_data.text == "技能装配":
                logger.scene("技能装配")
                if not flag_already_reset:
                    self.check_click(self.IMAGE_FIGHT_READY_RESET, timeout=3)
                    flag_already_reset = True
                    KeyBoard.enter(1)
                # 检查每个BUFF
                for _ in range(1):
                    Mouse.click(RelativePoint(760, 150))  # [1,1]
                    # Mouse.click(RelativePoint(760, 240))  # [2,1]
                    sleep()
                    new_result = ocr.get_raw_result()
                    for item in new_result:
                        ocr_data = OcrData(item)
                        if ocr_data.text in ["柔风抱暖", "细雨化屏"]:
                            for item in new_result:
                                ocr_data = OcrData(item)
                                if ocr_data.text == "装备":
                                    logger.scene(ocr_data.center.coor)
                                    Mouse.click(ocr_data.center)
                                    break
                            break
                sleep()
                self.check_click(self.IMAGE_FIGHT_READY_QUIT, timeout=3)
                sleep()
                Mouse.click()
                sleep(2)
                self.check_click(self.IMAGE_FIGHT, timeout=3)
                sleep(2)
                break
            elif "战斗失败" in ocr_data.text:
                logger.ui("战斗失败", "warn")
                for item in result:
                    ocr_data = OcrData(item)
                    if ocr_data.text == "放弃前行":
                        Mouse.click(ocr_data.center)
                        KeyBoard.enter(1)
            # 结算
            elif "击败普通妖怪" in ocr_data.text:
                logger.scene("结算")
                logger.ui("等待万相赐福")
                sleep(2)
                new_result = ocr.get_raw_result()
                _ocr_data_cannel = None  # 记录取消按钮位置
                for item in new_result:
                    ocr_data = OcrData(item)
                    if "万相赐福" in ocr_data.text:
                        logger.scene("万相赐福")
                        for item in new_result:
                            ocr_data = OcrData(item)
                            if ocr_data.text == "使用":
                                logger.ui("使用万相赐福")
                                Mouse.click(ocr_data.center)
                                _ocr_data_cannel = None
                                break
                            if ocr_data.text == "取消":
                                _ocr_data_cannel = ocr_data
                        break
                # 检测不到“万相赐福”则点击取消按钮
                if _ocr_data_cannel is not None:
                    logger.ui("没有万相赐福，取消购买")
                    Mouse.click(_ocr_data_cannel.center)
                sleep()
                finish_random_left_right()
                sleep()
                Mouse.click()
                self.done()
                self.state = self.STATE_START

    def run(self):
        logger.num(f"0/{self.max}")
        self.check_current_scene()

        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            if self.state == self.STATE_START:
                self.check_title()
                # self.check_title_jiaotu() #TODO
                sleep()
                self.choose_initial_buff(1)
                self.map_node_numbers = 0  # 地图上节点的个数
                self.shop_refresh_counts = 0  # 商店刷新次数
                self.state = self.STATE_RUNNING

            self.fight()
            sleep(2)
