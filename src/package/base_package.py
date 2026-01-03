import time
from typing import Literal

from ..utils.adapter import Mouse
from ..utils.application import SCREENSHOT_DIR_PATH
from ..utils.assets import AssetOcr
from ..utils.config import config
from ..utils.decorator import log_function_call, run_in_thread
from ..utils.event import event_thread
from ..utils.exception import CustomException, GUIStopException
from ..utils.function import finish_random_left_right, prevent_sleep, sleep
from ..utils.image import AssetImage, RuleImage
from ..utils.log import logger
from ..utils.mysignal import global_ms as ms
from ..utils.paddleocr import RuleOcr
from ..utils.screenshot import ScreenShot
from ..utils.toast import toast
from ..utils.window import window_manager
from .global_parameter import xuanshangfengyin_count
from .global_resource import GlobalResource
from .utils import get_image_asset, get_ocr_asset, load_asset


class BasePackage:
    scene_name: str = None
    """名称"""
    resource_path: str = None
    """路径"""
    resource_list: list = []
    """资源列表"""
    init: bool = False
    """初始化"""

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

        self.global_assets = GlobalResource()
        """通用资源"""
        self.load_asset_list()
        try:
            self.load_asset()
            self.init = True
        except Exception as e:
            logger.error(f"{self.resource_path}/assets.json 资源加载失败：{e}")
            logger.ui_error(f"{self.resource_path}/assets.json 资源加载失败，请检查资源文件")

    @staticmethod
    def description() -> None:
        """功能描述，支持重写"""
        pass

    def load_asset_list(self):
        self.asset_image_list = load_asset(self.resource_path, "image")
        self.asset_ocr_list = load_asset(self.resource_path, "ocr")

    def load_asset(self):
        pass

    def get_image_asset(self, name: str) -> AssetImage:
        return get_image_asset(self.asset_image_list, name)

    def get_ocr_asset(self, name: str) -> AssetOcr:
        return get_ocr_asset(self.asset_ocr_list, name)

    def title_error_msg(self):
        logger.ui_warn("请检查游戏场景")

    def soul_overflow_warn_msg(self):
        logger.ui_warn("御魂上限提醒")

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
            logger.warning("no OCR_TITLE")
        try:
            asset = self.IMAGE_TITLE
        except AttributeError:
            logger.warning("no IMAGE_TITLE")

        while True:
            if bool(event_thread):
                raise GUIStopException

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
                raise GUIStopException

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
                raise GUIStopException

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
    def wait_passengers_on_position(self, passengers: int = 2):
        """等待队员就位，需要在组队界面，
        没有匹配到对应的背景说明该位置被玩家模型占用，
        其中队员3的位置消失表示3个人都就位
        """
        logger.ui("等待队员就位")
        while True:
            if bool(event_thread):
                raise GUIStopException

            # 优先判断3人组队
            if passengers == 3:
                if not RuleImage(self.global_assets.IMAGE_PASSENGER_3).match():
                    logger.ui("队员3 就位")
                    return True
            elif not RuleImage(self.global_assets.IMAGE_PASSENGER_2).match():
                logger.ui("队员2 就位")
                return True

    def start(self, *args, **kwargs) -> None:
        """挑战开始"""
        # coor = random_coor(1067 - 50, 1067 + 50, 602 - 50, 602 + 50)
        # click(coor, sleeptime=sleeptime)
        self.check_click(self.IMAGE_START, *args, **kwargs)

    def screenshot(self) -> None:
        """截图，保存在当前功能的名称截图目录"""
        screenshot_path = "cache" if self.resource_path is None else self.resource_path
        screenshot_path = SCREENSHOT_DIR_PATH / screenshot_path
        if not screenshot_path.exists():
            screenshot_path.mkdir(parents=True)

        screenshot_file = screenshot_path / f"screenshot-{time.strftime('%Y%m%d%H%M%S')}.png"
        ScreenShot().save(str(screenshot_file))
        logger.info(f"screenshot: {screenshot_file}")

    def done(self) -> None:
        """更新一次完成情况"""
        self.n += 1
        logger.progress(f"{self.n}/{self.max}")

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
            if RuleImage(self.global_assets.IMAGE_VICTORY).match(_screenshot):
                logger.ui("战斗胜利")
                return True
            if RuleImage(self.global_assets.IMAGE_FINISH).match(_screenshot):
                logger.ui("战斗结束")
                return True
            if RuleImage(self.global_assets.IMAGE_FAIL).match(_screenshot):
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
                raise GUIStopException

            if timeout and (time.time() - _start > timeout):
                logger.error("check_finish timeout")
                return False

            _screenshot = ScreenShot()
            if RuleImage(self.global_assets.IMAGE_FINISH).match(_screenshot):
                logger.ui("战斗结束")
                return True
            if RuleImage(self.global_assets.IMAGE_FAIL).match(_screenshot):
                logger.ui_warn("战斗失败")
                return False

    @log_function_call
    def ensure_finish(self):
        """确保结束"""
        logger.ui("结束")
        sleep(0.4, 0.8)
        finish_random_left_right()
        while True:
            if bool(event_thread):
                raise GUIStopException

            # 未重复检测到，表示成功点击
            if not RuleImage(self.global_assets.IMAGE_FINISH).match():
                self.done()
                break
            Mouse.click()
            sleep(0.4, 0.8)

    def close_current_scene(self):
        """关闭当前场景"""
        logger.ui("准备关闭当前场景")
        sleep()
        if self.check_click(self.global_assets.IMAGE_CLOSE, timeout=5):
            logger.ui("关闭当前场景成功")
        else:
            logger.ui_warn("关闭当前场景失败")

    def run(self):
        """任务内容，支持重写"""
        pass

    def task_finish_info(self):
        """任务结束信息，支持重写"""
        pass

    def _format_time_cost(self, cost: int):
        """格式化用时为可读字符串，支持小时/分钟/秒

        Args:
            cost (int): 秒数
        """
        try:
            s = int(cost)
            if s >= 3600:
                hours = s // 3600
                minutes = (s % 3600) // 60
                seconds = s % 60
                logger.ui(f"用时 {hours}时{minutes}分{seconds}秒")
            elif s >= 60:
                logger.ui(f"用时 {(s // 60)}分{(s % 60)}秒")
            else:
                logger.ui(f"用时 {s}秒")
        except Exception:
            logger.error("用时统计计算失败")

    @run_in_thread
    def task_start(self):
        """任务开始"""

        # 禁用按钮
        ms.main.is_fighting_update.emit(True)
        _start = time.perf_counter()
        if self.max:
            logger.progress(f"0/{self.max}")
        else:
            logger.progress(0)

        xuanshangfengyin_count.reset()

        need_prevent_sleep: bool = False  # 是否需要防止休眠
        interaction_mode = config.user.model_dump().get("interaction_mode")
        if interaction_mode.get("mode") == "前台":
            if interaction_mode.get("frontend").get("force_window"):
                window_manager.set_foreground()
        else:
            if interaction_mode.get("backend").get("prevent_sleep"):
                if prevent_sleep(True):
                    need_prevent_sleep = True

        try:
            self.run()
        except Exception as e:
            if not isinstance(e, CustomException):
                import traceback

                logger.ui_error(f"任务出错: {e}")
                logger.error(traceback.format_exception(e))

        if need_prevent_sleep:
            prevent_sleep(False)

        _end = time.perf_counter()
        self._format_time_cost(int(_end - _start))

        self.task_finish_info()
        if xuanshangfengyin_count.get():
            logger.ui_warn(f"接到 {xuanshangfengyin_count.get()} 个悬赏封印")
            xuanshangfengyin_count.reset()

        # 启用按钮
        ms.main.is_fighting_update.emit(False)
        logger.ui(f"已完成 {self.scene_name} {self.n}次")
        # 系统通知
        # 5s结束，保留至通知中心
        toast("任务已完成")
