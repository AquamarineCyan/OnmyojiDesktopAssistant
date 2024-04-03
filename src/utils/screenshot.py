import time

import cv2
import numpy as np
from PIL import ImageGrab

from .log import logger
from .window import window


class ScreenShot:
    def __init__(self, rect: tuple[int, int, int, int] = None, _log: bool = True):
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
        self._log = _log
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
        if self._log:
            logger.info(f"screenshot cost {round((_end - _start) * 1000, 2)}ms")
        # image.show()
        self._image = image
        return image

    def save(self, file, *args, **kwargs):
        self._image.save(file, *args, **kwargs)

    def return_mat(self) -> cv2.typing.MatLike:
        img_np = np.array(self._image)
        # OpenCV使用BGR格式，而PIL使用RGB格式，因此需要转换颜色通道
        img_mat = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        self._image_mat = img_mat
        return img_mat
