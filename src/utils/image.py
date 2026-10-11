import time
from enum import Enum
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
from PIL.Image import Image

from .assets import AssetImage
from .config import config
from .coordinate import STANDARD_CLIENT_HEIGHT, STANDARD_CLIENT_WIDTH, get_scale, scale_region
from .event import event_xuanshang
from .function import check_user_file_exists, random_normal
from .log import logger
from .point import Point
from .screenshot import ScreenShot
from .window import window_manager


class LOGLEVEL(Enum):
    """日志等级"""

    NONE = 0
    FAIL = 1
    SUCCESS = 2


def get_template_scale(client_w: float | None = None, client_h: float | None = None) -> tuple[float, float]:
    """计算模板缩放系数 / 基准空间 → 实际客户区的换算系数

    Args:
        client_w: 当前客户区宽度，None 则按当前窗口（coordinate.get_scale）
        client_h: 当前客户区高度，None 则按当前窗口（coordinate.get_scale）

    Returns:
        (fx, fy): 相对 1136x640 的缩放系数，桌面版/无窗口返回 (1.0, 1.0)
    """
    if client_w is None or client_h is None:
        return get_scale()
    return (client_w / STANDARD_CLIENT_WIDTH, client_h / STANDARD_CLIENT_HEIGHT)


def scale_template_image(img: cv2.typing.MatLike, fx: float, fy: float) -> cv2.typing.MatLike:
    """按系数缩放模板"""
    if img is None:
        return None
    if abs(fx - 1.0) < 0.01 and abs(fy - 1.0) < 0.01:
        return img
    new_w = max(1, int(round(img.shape[1] * fx)))
    new_h = max(1, int(round(img.shape[0] * fy)))
    interp = cv2.INTER_AREA if (fx < 1.0 and fy < 1.0) else cv2.INTER_LINEAR
    return cv2.resize(img, (new_w, new_h), interpolation=interp)


def convert_image_rgb_to_bgr(image: Image) -> cv2.typing.MatLike:
    """将RGB格式的图像转换为BGR格式

    参数:
        image (Image): RGB图像

    返回:
        cv2.typing.MatLike: BGR图像
    """
    img_np = np.array(image)
    # OpenCV使用BGR格式，而PIL使用RGB格式，因此需要转换颜色通道
    return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)


class RuleImage:
    """图像识别

    用法:
    ```python
    image = RuleImage(assetimage=AssetImage)
    result = image.match()
    if result:
        point = image.center_point()
    ```
    """

    def __init__(
        self,
        assetimage: AssetImage = None,
        name: str = None,
        file: str | Path = None,
        region: tuple = None,
        score: float = None,
        method: Literal["COLOR", "GRAYSCALE"] = "COLOR",
    ) -> None:
        """
        参数:
            assetimage (AssetImage): 素材文件
            file (str | Path): 相对路径
            name (str): 素材名称
            region (tuple): 匹配区域（左，上，宽，高）
            score (float): 阈值
            method (Literal[&quot;COLOR&quot;, &quot;GRAYSCALE&quot;]): 匹配方法
        """
        # 优先使用给定的素材
        if assetimage:
            _file = assetimage.file
            self.name = assetimage.name
            self.description = assetimage.description
            self.region = assetimage.region
            self.score = assetimage.score
            self.method = assetimage.method
        else:
            _file = file
            self.name = name
            self.description = ""
            self.region = region
            self.score = score
            self.method = method

        if region:
            self.region = region
        if score:
            self.score = score

        # 获得图像的绝对路径
        self.file = check_user_file_exists(_file)

        # 空值或者(0,0,0,0)则匹配整个窗口
        if self.region is None or self.region == (0, 0, 0, 0):
            cur = window_manager.current
            w = getattr(cur, "content_width", 0) or cur.client_width
            h = getattr(cur, "content_height", 0) or cur.client_height
            self.region = (0, 0, w, h)
            self._region_scalable = False  # 已是实际客户区尺寸
        else:
            self._region_scalable = True  # 素材/显式 region 是基准空间坐标

        self._image = None
        self._scaled_image = None
        self._scaled_key: tuple | None = None
        self.match_result = None

    def __str__(self):
        return str(self.file.absolute())

    def load_image(self) -> None:
        if self._image is not None:
            return
        if self.method == "COLOR":
            _method = cv2.IMREAD_COLOR
        elif self.method == "GRAYSCALE":
            _method = cv2.IMREAD_GRAYSCALE

        if Path(self.file).exists():
            img = cv2.imread(str(self.file), _method)
            self._image = img
        else:
            logger.warning(f"{self.file} 文件不存在")

    def actual_region(self) -> tuple[int, int, int, int]:
        """region 在实际客户区中的坐标（基准空间 region 按系数放大）"""
        if self._region_scalable:
            return scale_region(self.region)
        return tuple(self.region)

    def match(
        self,
        image: ScreenShot | Image | str | None = None,
        score: float = None,
        debug: bool = False,
        normal: bool = True,
        logger_lever: Literal["ERROR", "SUCCESS", "NONE"] = "SUCCESS",
    ) -> bool:
        """图像匹配

        Args:
            image (ScreenShot | Image | str | None): 待匹配图像，None表示使用当前截图
            score (float): 匹配阈值，低于该值则匹配失败
            debug (bool): 是否显示调试信息，默认为False
            normal (bool): 是否正常状态（非悬赏等待状态）下进行匹配
            logger_lever (Literal["ERROR", "SUCCESS", "NONE"]): 日志级别
                        - "ERROR" : 仅记录失败
                        - "SUCCESS" : 记录成功和失败
                        - "NONE" : 不记录日志

        Returns:
            bool: 匹配成功/失败
        """
        if normal:
            event_xuanshang.wait()
        fx, fy = get_template_scale()
        region = self.actual_region()
        if image is None:
            image = convert_image_rgb_to_bgr(ScreenShot(region, debug=debug).get_image())
        elif isinstance(image, ScreenShot):
            image = convert_image_rgb_to_bgr(image.get_image())
        elif isinstance(image, Image):
            image = convert_image_rgb_to_bgr(image)
        else:
            image = cv2.imread(image, cv2.IMREAD_COLOR)
        if score is None:
            score = self.score

        self.load_image()
        if self._image is None:
            return False
        # 按当前客户区相对 1136x640 缩放模板（模拟器窗口自由尺寸，裸匹配会掉分）
        template = self._image
        if abs(fx - 1.0) >= 0.01 or abs(fy - 1.0) >= 0.01:
            key = (round(fx, 4), round(fy, 4))
            if self._scaled_key != key or self._scaled_image is None:
                self._scaled_image = scale_template_image(self._image, fx, fy)
                self._scaled_key = key
            template = self._scaled_image
            if template.shape[0] > image.shape[0] or template.shape[1] > image.shape[1]:
                if logger_lever == "ERROR":
                    logger.warning(f"[ERROR] {self.name} scaled template larger than screenshot")
                return False
        res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        # 最小匹配度，最大匹配度，最小匹配度的坐标，最大匹配度的坐标
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val < score:
            if logger_lever == "ERROR":
                logger.warning(f"[ERROR] {self.name} [score] {round(max_val, 4)}")
            return False

        if logger_lever in ("SUCCESS", "ERROR"):
            logger.info(f"[SUCCESS] {self.name} [score] {round(max_val, 4)}")
        # https://blog.csdn.net/m0_37579176/article/details/116950903
        # 匹配区域里的相对坐标
        x1, y1 = max_loc
        # 加上图像自身占游戏窗口的坐标
        x1 = x1 + region[0]
        y1 = y1 + region[1]
        x2 = x1 + template.shape[1]
        y2 = y1 + template.shape[0]
        # 实际客户区 → 基准空间：业务侧统一按基准空间使用识别结果
        self.match_result = (x1 / fx, y1 / fy, x2 / fx, y2 / fy)

        if debug:
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 1)  # color: BGR
            # 使用 PIL 展示，避免依赖 opencv 的 GUI 组件（headless 版无 imshow）
            Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).show(title="DEBUG")

        return True

    def random_point(self) -> Point:  # TODO 移除，只使用中心坐标
        """获取随机坐标"""
        x1, y1, x2, y2 = self.match_result
        x = random_normal(x1, x2)
        y = random_normal(y1, y2)
        return Point(x, y)

    def center_point(self) -> Point:
        """获取中心坐标"""
        x1, y1, x2, y2 = self.match_result
        x = int((x1 + x2) / 2)
        y = int((y1 + y2) / 2)
        return Point(x, y)


def check_image_once(image_list: list[AssetImage]) -> RuleImage | None:
    """图像识别，仅遍历一次

    参数:
        image_list (list[AssetImage]): 图像列表

    返回:
        RuleImage | None: 识别结果
    """
    _screenshot = ScreenShot(_log=True)
    for item in image_list:
        image = RuleImage(item)
        if image.match(_screenshot):
            return image
    time.sleep(config.user.screenshot_interval / 1000.0)
    return None
