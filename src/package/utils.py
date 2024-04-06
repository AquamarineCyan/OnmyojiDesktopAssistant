import time
from pathlib import Path
from typing import Literal

from ..utils.adapter import Mouse
from ..utils.application import (
    RESOURCE_DIR_PATH,
    RESOURCE_GLOBAL_PATH,
    SCREENSHOT_DIR_PATH,
    USER_DATA_DIR_PATH,
)
from ..utils.assets import AssetOcr
from ..utils.decorator import log_function_call, run_in_thread
from ..utils.event import event_thread
from ..utils.function import (
    check_click,
    check_scene_multiple_once,
    click,
    finish_random_left_right,
    get_coor_info,
    merge_dict,
    open_asset_file,
    random_sleep,
)
from ..utils.image import AssetImage, RuleImage
from ..utils.log import logger
from ..utils.mysignal import global_ms as ms
from ..utils.paddleocr import RuleOcr
from ..utils.screenshot import ScreenShot
from ..utils.toast import toast


def load_asset(resource_path, type: str = Literal["image", "ocr"]) -> dict:
    _full_path = RESOURCE_DIR_PATH / resource_path / "assets.json"
    _full_path_user = (USER_DATA_DIR_PATH / "myresource").joinpath(
        *_full_path.parts[-2:]
    )

    data_default = open_asset_file(_full_path)
    assets_file = _full_path
    data_user = open_asset_file(_full_path_user)
    if data_user != {}:
        assets_file = _full_path_user

    data = merge_dict(data_default, data_user)
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


class GlobalResource:
    """通用资源"""

    resource_path: str = "global"  # 路径
    resource_list: list = [
        "accept_invitation",  # 接受邀请
        "fail",  # 失败
        "finish",  # 结束
        "fighting_friend_default",  # 战斗中好友图标-怀旧/简约
        "fighting_friend_linshuanghanxue",  # 战斗中好友图标-凛霜寒雪
        "fighting_friend_chunlvhanqing",  # 战斗中好友图标-春缕含青
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
            self.IMAGE_FAIL = AssetImage(**get_asset(self.image_data, "fail"))
            self.IMAGE_FINISH = AssetImage(**get_asset(self.image_data, "finish"))
            self.IMAGE_SOUL_OVERFLOW = AssetImage(
                **get_asset(self.image_data, "soul_overflow")
            )
            self.IMAGE_VICTORY = AssetImage(**get_asset(self.image_data, "victory"))
        except Exception as e:
            logger.ui_error(f"{self.resource_path}/assets.json文件内容解析失败: {e}")
            return


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
        self.current_scene: str = None
        """当前场景"""
        if self.ASSET:
            self.global_image = GlobalResource()
            """通用资源"""
            self.load_asset()

    def load_asset(self):
        self.asset_image_list = load_asset(self.resource_path, "image")
        self.asset_ocr_list = load_asset(self.resource_path, "ocr")

    def get_coor_info(self, file, *args, **kwargs):
        return get_coor_info(f"{self.resource_path}/{file}", *args, **kwargs)

    def check_scene_multiple_once(self, *args, **kwargs):
        return check_scene_multiple_once(self.current_resource_list, *args, **kwargs)

    def title_error_msg(self):
        logger.ui("请检查游戏场景", "warn")

    def scene_print(self, scene: str = None) -> None:  # FIXME remove
        """打印当前场景"""
        if "/" in scene:
            scene = scene.split("/")[-1]
        logger.scene(scene)

    def scene_handle(self, scene: str = None) -> str:
        if scene is None:
            scene = self.current_scene
        logger.info(f"current scene: {scene}.png")
        if "/" in scene:
            scene = scene.split("/")[-1]
        self.current_scene = scene
        return scene

    def log_current_scene_list(self) -> None:
        """记录当前匹配的资源列表"""
        if self.current_resource_list is None:
            return
        logger.info(f"current_resource_list: {len(self.current_resource_list)}")
        for item in self.current_resource_list:
            logger.info(item)

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
        _flag_title_msg = True
        _asset_title = None

        # 判断标题采用何种识别方法
        try:
            _asset_title = self.OCR_TITLE
        except AttributeError:
            logger.warn("no OCR_TITLE")
        try:
            _asset_title = self.IMAGE_TITLE
        except AttributeError:
            logger.warn("no IMAGE_TITLE")

        while True:
            if bool(event_thread):
                return

            if isinstance(_asset_title, AssetOcr):
                if RuleOcr(_asset_title).match():
                    logger.scene(self.scene_name)
                    return
            elif isinstance(_asset_title, AssetImage):
                if RuleImage(_asset_title).match():
                    logger.scene(self.scene_name)
                    return
            else:  # FIXME 兼容旧方法
                coor = self.get_coor_info("title")
                if coor.is_effective:
                    logger.scene(self.scene_name)
                    return

            if _flag_title_msg:
                _flag_title_msg = False
                self.title_error_msg()

    def check_click(
        self,
        asset: AssetImage | AssetOcr = None,
        timeout: float = 0,
        point_type: Literal["random", "center"] = "random",
        *args,
        **kwargs,
    ) -> bool:
        if isinstance(asset, str):
            check_click(f"{self.resource_path}/{asset}", *args, **kwargs)
            return

        if timeout:
            _start = time.time()
        while True:
            if bool(event_thread):
                return False
            if timeout and (time.time() - _start > timeout):
                logger.error("check_image_click timeout")
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
                    Mouse.click(result.rect.get_rela_center_coor(), *args, **kwargs)
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

    def ensure_finish(self):
        """确保结束"""
        logger.ui("结束")
        random_sleep(0.4, 0.8)
        finish_random_left_right()
        while True:
            if event_thread.is_set():
                return
            coor = get_coor_info(f"{self.global_resource_path}/finish")
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
        _start = time.perf_counter()
        if self.max:
            logger.num(f"0/{self.max}")
        self.run()
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
