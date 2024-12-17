import os
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
from PIL.Image import Image

from .assets import AssetImage
from .event import event_xuanshang
from .function import check_user_file_exists, random_normal
from .log import logger
from .point import RelativePoint
from .screenshot import ScreenShot, ScreenShotBackend
from .window import window


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
        point = image.center()
    ```
    """

    def __init__(
        self,
        assetimage: AssetImage = None,
        name: str = None,
        file: str | Path = None,
        region: tuple = None,
        score: float = 0.8,
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

        # 获得图像的绝对路径
        self.file = check_user_file_exists(_file)
        if self.region is None:
            self.region = (0, 0, window.window_width, window.window_height)
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

        if os.path.exists(str(self.file)):
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
    ) -> bool:
        if normal:
            event_xuanshang.wait()
        if image is None:
            image = convert_image_rgb_to_bgr(ScreenShot(self.region).get_image())
        elif isinstance(image, ScreenShot|ScreenShotBackend):
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
            return False

        logger.info(f"{self.name} 匹配成功，相似度: {round(max_val, 2)}")
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

    def random_point(self) -> RelativePoint:
        """获取随机坐标"""
        x1, y1, x2, y2 = self.match_result
        x = random_normal(x1, x2)
        y = random_normal(y1, y2)
        return RelativePoint(x, y)

    def center_point(self) -> RelativePoint:
        """获取中心坐标"""
        x1, y1, x2, y2 = self.match_result
        x = int((x1 + x2) / 2)
        y = int((y1 + y2) / 2)
        return RelativePoint(x, y)


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
