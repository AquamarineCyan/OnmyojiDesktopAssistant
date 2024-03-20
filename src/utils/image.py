import time
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
from PIL import ImageGrab
from pydantic import BaseModel

from .function import check_user_file_exists, random_normal
from .log import logger
from .point import RelativePoint
from .window import window


class ScreenShot:
    def __init__(self, rect: tuple[int, int, int, int] = None):
        self._image = None
        _rect = (
            window.window_left,
            window.window_top,
            window.window_width,
            window.window_height,
        )
        if rect:
            self.rect = (_rect[0] + rect[0], _rect[1] + rect[1], rect[2], rect[3])
        else:
            self.rect = _rect
        # self.rect = window.handle_rect if rect is None else rect
        self._image_mat = None
        self._screenshot()

    def _screenshot(self):
        _rect = (
            self.rect[0],
            self.rect[1],
            self.rect[0] + self.rect[2],
            self.rect[1] + self.rect[3] + 39,
        )
        _start = time.perf_counter()
        image = ImageGrab.grab(_rect)
        _end = time.perf_counter()
        logger.info(f"screenshot cost {round((_end - _start) * 1000, 2)}ms")
        # image.show()
        self._image = image
        return image

    def save(self, file):
        self._image.save(file)

    def return_mat(self):
        img_np = np.array(self._image)
        # OpenCV使用BGR格式，而PIL使用RGB格式，因此需要转换颜色通道
        img_mat = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        self._image_mat = img_mat
        return img_mat


class AssstImage(BaseModel):
    name: str = None
    file: str = None
    region: tuple[int, int, int, int] = None
    score: float = 0.8
    method: Literal["COLOR", "GRAYSCALE"] = "COLOR"


class RuleImage:
    """图像识别

    用法:
    ```python
    image = RuleImage(assstimage=AssstImage)
    result = image.match()
    if result:
        point = image.center()
    ```
    """

    def __init__(
        self,
        assstimage: AssstImage = None,
        name: str = None,
        file: str | Path = None,
        region: tuple = None,
        score: float = 0.8,
        method: Literal["COLOR", "GRAYSCALE"] = "COLOR",
    ) -> None:
        """
        参数:
            assstimage (AssstImage): 素材文件
            file (str | Path): 相对路径
            region (tuple): 匹配区域
            score (float): 阈值
            method (Literal[&quot;COLOR&quot;, &quot;GRAYSCALE&quot;]): method
        """
        if assstimage:
            _file = assstimage.file
            self.name = assstimage.name
            self.region = assstimage.region
            self.score = assstimage.score
            self.method = assstimage.method
        else:
            _file = file
            self.name = name
            self.region = region
            self.score = score
            self.method = method

        self.file = check_user_file_exists(_file)
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

        img = cv2.imread(str(self.file), _method)
        self._image = img

    def match(self, image=None, score: float = None, debug: bool = False) -> bool:
        if image is None:
            image = ScreenShot(self.region).return_mat()
            # if debug:
            #     cv2.imshow("image", image)
            #     cv2.waitKey(0)
        else:
            image = cv2.imread(image, cv2.IMREAD_COLOR)
        if score is None:
            score = self.score

        self.load_image()
        res = cv2.matchTemplate(image, self._image, cv2.TM_CCOEFF_NORMED)
        # 最小匹配度，最大匹配度，最小匹配度的坐标，最大匹配度的坐标
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # logger.attr(self.name, max_val)

        if max_val < score:
            return False

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


def check_image_once(image_list: list[AssstImage]) -> RuleImage | None:
    """图像识别，仅遍历一次

    参数:
        image_list (list[AssstImage]): 图像列表

    返回:
        RuleImage | None: 识别结果
    """
    for item in image_list:
        image = RuleImage(item)
        logger.debug(image)
        if image.match():
            return image
    return None
