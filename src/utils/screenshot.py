import time

import win32con
import win32gui
import win32ui
from PIL import Image, ImageGrab

from .config import config
from .log import logger
from .window import GameWindow, window_manager


class ScreenShot:
    def __init__(
        self,
        rect: tuple[int, int, int, int] = None,
        handle: int = None,
        _log: bool = False,
        debug: bool = False,
    ) -> None:
        if handle:
            if isinstance(handle, GameWindow):
                self.gamewindow = handle
            else:
                self.gamewindow = GameWindow(handle)
        else:  # 如果没有传入句柄，则使用当前窗口
            self.gamewindow = window_manager.current
        self.hwnd = self.gamewindow.handle

        self._image = None
        _rect = (
            self.gamewindow.window_left,
            self.gamewindow.window_top,
            self.gamewindow.window_width,
            self.gamewindow.window_height,
        )
        if rect:
            self.rect = (_rect[0] + rect[0], _rect[1] + rect[1], rect[2], rect[3])
        else:
            self.rect = _rect
        # self.rect = window.handle_rect if rect is None else rect
        self._log = _log
        self._debug = debug
        self.rect_backend = None

        # 最多重试10次
        for i in range(10):
            if not window_manager.is_alive:
                return

            try:
                if config.backend:
                    if rect:
                        self.rect_backend = rect
                        if rect[1] > 0:  # top
                            self.rect_backend = (rect[0], rect[1] - 39, rect[2], rect[3])
                    self._screenshot_backend()
                else:
                    self._screenshot_front()
                break

            except Exception as e:
                logger.error(f"截图失败: {str(e)}")
                logger.ui_error(f"截图失败，重试第{i + 1}次")
                time.sleep(0.1)

    def _screenshot_front(self) -> Image.Image:
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
            logger.info(f"screenshot front cost {self.time_cost} ms, {_rect}")
        if self._debug:
            image.show()
        self._image = image
        return image

    def _screenshot_backend(self) -> Image.Image:
        """截图区域只有窗口客户区，不包括标题栏等"""
        client_rect = self.gamewindow.client_rect
        if self.rect_backend:
            width = self.rect_backend[2]
            height = self.rect_backend[3] + 39
        else:
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
        if self.rect_backend:
            srcPos = (self.rect_backend[0], self.rect_backend[1])
        else:
            srcPos = (0, 0)
        saveDC.BitBlt(
            (0, 0),
            (width, height),
            mfcDC,
            srcPos,
            win32con.SRCCOPY,
        )

        # 获取位图信息
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        # 生成图像
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
            logger.info(f"screenshot backend cost {self.time_cost} ms, {client_rect}")
        if self._debug:
            image.show()
        self._image = image
        return image

    def save(self, file, *args, **kwargs) -> None:
        self._image.save(file, *args, **kwargs)
        logger.info(f"screenshot cost {self.time_cost} ms, at {file}")

    def get_image(self) -> Image.Image:
        return self._image
