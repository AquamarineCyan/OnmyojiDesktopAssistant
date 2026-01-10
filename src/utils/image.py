from enum import Enum
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
from PIL.Image import Image

from .assets import AssetImage
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
            self.region = assetimage.region
            self.score = assetimage.score
            self.method = assetimage.method
        else:
            _file = file
            self.name = name
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
            self.region = (0, 0, window_manager.current.client_width, window_manager.current.client_height)

        self._image = None
        self.match_result = None

    def __str__(self):
        return str(self.file.absolute())

    def load_image(self) -> None:
        if self._image:
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

    def match(
        self,
        image: ScreenShot | Image | str | None = None,
        score: float = None,
        debug: bool = False,
        normal: bool = True,
        logger_lever: Literal["ERROR", "SUCCESS", "NONE"] = "SUCCESS",
    ) -> bool:
        if normal:
            event_xuanshang.wait()
        if image is None:
            image = convert_image_rgb_to_bgr(ScreenShot(self.region, debug=debug).get_image())
        elif isinstance(image, ScreenShot):
            image = convert_image_rgb_to_bgr(image.get_image())
        elif isinstance(image, Image):
            image = convert_image_rgb_to_bgr(image)
        else:
            image = cv2.imread(image, cv2.IMREAD_COLOR)
        if score is None:
            score = self.score

        self.load_image()
        res = cv2.matchTemplate(image, self._image, cv2.TM_CCOEFF_NORMED)
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
        x1 = x1 + self.region[0]
        y1 = y1 + self.region[1]
        x2 = x1 + self._image.shape[1]
        y2 = y1 + self._image.shape[0]
        # 左，上，右，下
        self.match_result = (x1, y1, x2, y2)

        if debug:
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 1)  # color: BGR
            cv2.imshow("DEBUG", image)
            cv2.waitKey(0)

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
    return None
