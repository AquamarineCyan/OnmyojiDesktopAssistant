import time

import win32con
import win32gui
import win32ui
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
            logger.info(f"screenshot cost {self.time_cost} ms, {_rect}")
        if debug:
            image.show()
        self._image = image
        return image

    def save(self, file, *args, **kwargs) -> None:
        self._image.save(file, *args, **kwargs)
        logger.info(f"screenshot cost {self.time_cost} ms, at {file}")

    def get_image(self) -> Image.Image:
        return self._image


class ScreenShotBackend:
    def __init__(
        self,
        _log: bool = False,
        debug: bool = False,
    ) -> None:
        self.hwnd = window.handle
        self._image = None
        self._image_mat = None
        self._log = _log
        self._screenshot(debug)

    def _screenshot(self, debug: bool = False) -> Image.Image:
        client_rect = window.client_rect
        width = client_rect[2] - client_rect[0]
        height = client_rect[3] - client_rect[1]
        _start = time.perf_counter()
        # 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
        hWndDC = win32gui.GetDC(self.hwnd)
        # 创建设备描述表
        mfcDC = win32ui.CreateDCFromHandle(hWndDC)
        # 创建内存设备描述表
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建位图对象准备保存图片
        saveBitMap = win32ui.CreateBitmap()
        # 为bitmap开辟存储空间
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        # 将截图保存到saveBitMap中
        saveDC.SelectObject(saveBitMap)
        # 保存bitmap到内存设备描述表
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

        ###获取位图信息
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        ###生成图像
        image = Image.frombuffer(
            "RGB",
            (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr,
            "raw",
            "BGRX",
            0,
            1,
        ).convert("RGB")

        # 内存释放
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hWndDC)

        # image = ImageGrab.grab(_rect)
        _end = time.perf_counter()
        self.time_cost = round((_end - _start) * 1000, 2)
        if self._log:
            logger.info(f"screenshot cost {self.time_cost} ms, {client_rect}")
        if debug:
            image.show()
        self._image = image
        return image

    def save(self, file, *args, **kwargs) -> None:
        self._image.save(file, *args, **kwargs)
        logger.info(f"screenshot cost {self.time_cost} ms, at {file}")

    def get_image(self) -> Image.Image:
        return self._image
