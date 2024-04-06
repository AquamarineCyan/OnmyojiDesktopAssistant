import time

from PIL import Image, ImageGrab

from .log import logger
from .window import window


class ScreenShot:
    def __init__(
        self,
        rect: tuple[int, int, int, int] = None,
        _log: bool = False,
        debug: bool = False,
    ) -> None:
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
        self._screenshot(debug)

    def _screenshot(self, debug: bool = False) -> Image.Image:
        _rect = (
            self.rect[0],
            self.rect[1],
            self.rect[0] + self.rect[2],
            self.rect[1] + self.rect[3] + 39,
        )
        _start = time.perf_counter()
        image = ImageGrab.grab(_rect)
        _end = time.perf_counter()
        self.time_cost = round((_end - _start) * 1000, 2)
        if self._log:
            logger.info(f"screenshot cost {self.time_cost} ms")
        if debug:
            image.show()
        self._image = image
        return image

    def save(self, file, *args, **kwargs) -> None:
        self._image.save(file, *args, **kwargs)
        logger.info(f"screenshot cost {self.time_cost} ms, at {file}")

    def get_image(self) -> Image.Image:
        return self._image
