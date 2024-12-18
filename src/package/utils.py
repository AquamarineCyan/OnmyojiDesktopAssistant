import time
from pathlib import Path
from typing import Literal

from ..utils.adapter import Mouse
from ..utils.application import RESOURCE_GLOBAL_PATH, SCREENSHOT_DIR_PATH
from ..utils.assets import AssetOcr
from ..utils.decorator import log_function_call, run_in_thread
from ..utils.event import event_thread
from ..utils.function import finish_random_left_right, get_asset_data, sleep
from ..utils.image import AssetImage, RuleImage
from ..utils.log import logger
from ..utils.mysignal import global_ms as ms
from ..utils.paddleocr import RuleOcr
from ..utils.screenshot import ScreenShot
from ..utils.toast import toast


class GUIStopException(Exception):
    """GUI停止按钮"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_error("异常捕获：GUI停止按钮")


def load_asset(resource_path, type: str = Literal["image", "ocr"]) -> dict:
    assets_file, data = get_asset_data(resource_path)
    if data.get(f"{type}_data") is None:
        return None

    try:
        if type == "image":
            current_asset = data["current_path"]
            data = data["image_data"]
            for item in data:
                _item = item["file"]
                item["file"] = f"{current_asset}/{_item}"
            return data
        elif type == "ocr":
            data = data["ocr_data"]
            return data
    except KeyError:
        logger.ui_error(f"{assets_file}文件内容格式错误")
    except Exception as e:
        logger.ui_error(f"{assets_file}文件内容解析失败: {e}")

    return {}


def get_asset(dict_, name):
    for item in dict_:
        if item["name"] == name:
            return item


def get_image_asset(asset_image_list, name) -> AssetImage:
    return AssetImage(**get_asset(asset_image_list, name))


class GlobalResource:
    """通用资源"""

    resource_path: str = "global"  # 路径
    resource_list: list = [
        "accept_invitation",  # 接受邀请
        "fail",  # 失败
        "fighting",  # 战斗中
        "fighting_back_default",  # 战斗中返回
        # "fighting_friend_default",  # 战斗中好友图标-怀旧/简约
        # "fighting_friend_linshuanghanxue",  # 战斗中好友图标-凛霜寒雪
        # "fighting_friend_chunlvhanqing",  # 战斗中好友图标-春缕含青
        "finish",  # 结束
        "passenger_2",  # 队员2
        "passenger_3",  # 队员3
        "ready_new",  # 准备-简约主题
        "ready_old",  # 准备-怀旧主题
        "start_single",  # 单人挑战
        "start_team",  # 组队挑战
        "tanchigui",  # 贪吃鬼
        "victory",  # 成功
    ]

    def __init__(self):
        self.image_data = load_asset(self.resource_path, "image")
        if self.image_data == {}:
            logger.ui_error(f"{self.resource_path}/assets.json文件解析失败")
            return
        try:
            self.load_asset()
        except Exception as e:
            logger.ui_error(f"{self.resource_path}/assets.json文件内容解析失败: {e}")

    def load_asset(self):
        self.IMAGE_ACCEPT_INVITATION = AssetImage(
            **get_asset(self.image_data, "accept_invitation")
        )
        self.IMAGE_FAIL = AssetImage(**get_asset(self.image_data, "fail"))
        self.IMAGE_FIGHTING = AssetImage(**get_asset(self.image_data, "fighting"))
        self.IMAGE_FIGHTING_BACK_DEFAULT = AssetImage(
            **get_asset(self.image_data, "fighting_back_default")
        )
        self.IMAGE_FINISH = AssetImage(**get_asset(self.image_data, "finish"))
        self.IMAGE_PASSENGER_2 = AssetImage(**get_asset(self.image_data, "passenger_2"))
        self.IMAGE_PASSENGER_3 = AssetImage(**get_asset(self.image_data, "passenger_3"))
        self.IMAGE_READY_NEW = AssetImage(**get_asset(self.image_data, "ready_new"))
        self.IMAGE_READY_OLD = AssetImage(**get_asset(self.image_data, "ready_old"))
        self.IMAGE_START_SINGLE = AssetImage(
            **get_asset(self.image_data, "start_single")
        )
        self.IMAGE_START_TEAM = AssetImage(**get_asset(self.image_data, "start_team"))
        self.IMAGE_SOUL_OVERFLOW = AssetImage(
            **get_asset(self.image_data, "soul_overflow")
        )
        self.IMAGE_TANCHIGUI = AssetImage(**get_asset(self.image_data, "tanchigui"))
        self.IMAGE_VICTORY = AssetImage(**get_asset(self.image_data, "victory"))
        self.IMAGE_XIEZHANDUIWU = AssetImage(
            **get_asset(self.image_data, "xiezhanduiwu")
        )


class Package:
    scene_name: str = None
    """名称"""
    resource_path: str = None
    """路径"""
    resource_list: list = []
    """资源列表"""
    description: str = None
    """功能描述"""
    fast_time: int = 0
    """最快通关速度，用于中途等待"""
    global_resource_path: Path = RESOURCE_GLOBAL_PATH
    """通用资源路径"""
    ASSET: bool = False

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        self.n: int = 0
        """当前次数"""
        self.max: int = n
        """总次数"""
        self.current_resource_list: list = None
        """当前使用的资源列表"""
        self.current_asset_list: list = None
        """当前使用的资源列表"""
        self.current_scene: str = None
        """当前场景"""

        self.global_image = GlobalResource()
        """通用资源"""
        self.load_asset_list()
        try:
            self.load_asset()
        except Exception as e:
            logger.error(f"{self.resource_path}/assets.json 资源加载失败：{e}")
            logger.ui_error(
                f"{self.resource_path}/assets.json 资源加载失败，请检查资源文件"
            )

    def load_asset_list(self):
        self.asset_image_list = load_asset(self.resource_path, "image")
        self.asset_ocr_list = load_asset(self.resource_path, "ocr")

    def load_asset(self):
        pass

    def get_image_asset(self, name: str) -> AssetImage:
        return get_image_asset(self.asset_image_list, name)

    def title_error_msg(self):
        logger.ui("请检查游戏场景", "warn")

    def scene_handle(self, scene: str = None) -> str:
        if scene is None:
            scene = self.current_scene
        logger.info(f"current scene: {scene}.png")
        if "/" in scene:
            scene = scene.split("/")[-1]
        self.current_scene = scene
        return scene

    def log_current_asset_list(self) -> None:
        """记录当前匹配的资源列表"""
        if self.current_asset_list is None:
            return
        logger.info(f"current_image_list: {len(self.current_asset_list)}")
        for item in self.current_asset_list:
            logger.info(item)

    @log_function_call
    def check_title(self):
        """检查主场景"""
        msg_title: bool = True
        asset = None

        # 判断标题采用何种识别方法
        try:
            asset = self.OCR_TITLE
        except AttributeError:
            logger.warn("no OCR_TITLE")
        try:
            asset = self.IMAGE_TITLE
        except AttributeError:
            logger.warn("no IMAGE_TITLE")

        while True:
            if bool(event_thread):
                return

            if isinstance(asset, AssetOcr):
                if RuleOcr(asset).match():
                    logger.scene(self.scene_name)
                    return
            elif isinstance(asset, AssetImage):
                if RuleImage(asset).match():
                    logger.scene(self.scene_name)
                    return
            else:
                logger.error("no title asset")
                return

            if msg_title:
                self.title_error_msg()
                msg_title = False

    def check_click(
        self,
        asset: AssetImage | AssetOcr = None,
        timeout: float = 0,
        point_type: Literal["random", "center"] = "random",
        *args,
        **kwargs,
    ) -> bool:
        if isinstance(asset, str):
            raise TypeError("asset must be AssetImage or AssetOcr")

        if timeout:
            _start = time.time()
        while True:
            if bool(event_thread):
                return False
            if timeout and (time.time() - _start > timeout):
                logger.error("check_click timeout")
                return False

            if isinstance(asset, AssetImage):
                image = RuleImage(asset)
                if image.match():
                    if point_type == "random":
                        Mouse.click(image.random_point(), *args, **kwargs)
                    elif point_type == "center":
                        Mouse.click(image.center_point(), *args, **kwargs)
                    return True
            elif isinstance(asset, AssetOcr):
                ocr = RuleOcr(asset)
                if result := ocr.match():
                    Mouse.click(result.center, *args, **kwargs)
                    return True

    def check_scene(
        self,
        asset: AssetImage | AssetOcr = None,
        timeout: float = 0,
    ) -> bool:
        if timeout:
            _start = time.time()
        while True:
            if bool(event_thread):
                return False
            if timeout and (time.time() - _start > timeout):
                logger.error("check_scene timeout")
                return False

            if isinstance(asset, AssetImage):
                if RuleImage(asset).match():
                    return True
            elif isinstance(asset, AssetOcr):
                if RuleOcr(asset).match():
                    return True

    @log_function_call
    def is_passengers_on_position(self, passengers: int = 2):
        """队员就位"""
        logger.ui("等待队员")
        while True:
            if bool(event_thread):
                return False
            # 是否3人组队
            if passengers == 3:
                if not RuleImage(self.global_image.IMAGE_PASSENGER_3).match():
                    logger.ui("队员3 就位")
                    return True
            elif not RuleImage(self.global_image.IMAGE_PASSENGER_2).match():
                logger.ui("队员2 就位")
                return True

    def start(self, *args, **kwargs) -> None:
        """挑战开始"""
        # coor = random_coor(1067 - 50, 1067 + 50, 602 - 50, 602 + 50)
        # click(coor, sleeptime=sleeptime)
        self.check_click(self.IMAGE_START, *args, **kwargs)

    def screenshot(self) -> None:
        screenshot_path = "cache" if self.resource_path is None else self.resource_path
        screenshot_path = SCREENSHOT_DIR_PATH / screenshot_path
        if not screenshot_path.exists():
            screenshot_path.mkdir(parents=True)

        screenshot_file = (
            screenshot_path / f"screenshot-{time.strftime('%Y%m%d%H%M%S')}.png"
        )
        ScreenShot().save(str(screenshot_file))
        logger.info(f"screenshot: {screenshot_file}")

    def done(self) -> None:
        """更新一次完成次数"""
        self.n += 1
        logger.num(f"{self.n}/{self.max}")

    @log_function_call
    def check_result(self) -> bool:
        """结果判断

        返回:
            bool: Success or Fail
        """
        while True:
            if bool(event_thread):
                raise GUIStopException
            _screenshot = ScreenShot()
            if RuleImage(self.global_image.IMAGE_VICTORY).match(_screenshot):
                logger.ui("战斗胜利")
                return True
            if RuleImage(self.global_image.IMAGE_FINISH).match(_screenshot):
                logger.ui("战斗结束")
                return True
            if RuleImage(self.global_image.IMAGE_FAIL).match(_screenshot):
                logger.ui_warn("战斗失败")
                return False

    @log_function_call
    def check_finish(self, timeout: int = None) -> bool:
        """结束/掉落判断

        返回:
            bool: Success or Fail
        """
        if timeout:
            _start = time.time()
        while True:
            if bool(event_thread):
                return None
            if timeout and (time.time() - _start > timeout):
                logger.error("check_finish timeout")
                return False

            _screenshot = ScreenShot()
            if RuleImage(self.global_image.IMAGE_FINISH).match(_screenshot):
                logger.ui("战斗结束")
                return True
            if RuleImage(self.global_image.IMAGE_FAIL).match(_screenshot):
                logger.ui_warn("战斗失败")
                return False

    def ensure_finish(self):
        """确保结束"""
        logger.ui("结束")
        sleep(0.4, 0.8)
        finish_random_left_right()
        while True:
            if bool(event_thread):
                return
            # 未重复检测到，表示成功点击
            if not RuleImage(self.global_image.IMAGE_FINISH).match():
                self.done()
                break
            Mouse.click()
            sleep(0.4, 0.8)

    def run(self):
        """任务内容"""
        pass

    @run_in_thread
    def task_start(self):
        """任务开始"""
        # 禁用按钮
        ms.main.is_fighting_update.emit(True)
        _start = time.perf_counter()
        if self.max:
            logger.num(f"0/{self.max}")

        try:
            self.run()
        except Exception as e:
            logger.error(e)

        _end = time.perf_counter()
        _cost = _end - _start
        try:
            if _cost >= 60:
                logger.ui(f"耗时{int(_cost // 60)}分{int(_cost % 60)}秒")
            else:
                logger.ui(f"耗时{int(_cost)}秒")
        except Exception:
            logger.error("耗时统计计算失败")
        # 启用按钮
        ms.main.is_fighting_update.emit(False)
        logger.ui(f"已完成 {self.scene_name} {self.n}次")
        # 系统通知
        # 5s结束，保留至通知中心
        toast("任务已完成")
