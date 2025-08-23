import time

import win32con
import win32gui
import win32ui
from PIL import Image, ImageGrab

from .config import config
from .log import logger
from .window import GameWindow, window_manager


class ScreenShot:
    """屏幕截图"""

    def __init__(
        self,
        rect: tuple[int, int, int, int] | None = None,
        handle: int | None = None,
        _log: bool = False,
        debug: bool = False,
    ) -> None:
        """
        Args:
            rect (tuple[int, int, int, int] | None): 自定义矩形(left, top, width, height)。默认为None，表示整个窗口客户区。
            handle (int | None): 窗口句柄。如果为None，则使用当前活动窗口。
            _log (bool): 是否记录日志。默认False。
            debug (bool): 是否在调试模式下显示截图。默认False。
        """
        if handle:
            if isinstance(handle, GameWindow):
                self.gamewindow = handle
            else:
                self.gamewindow = GameWindow(handle)
        else:  # 如果没有传入句柄，则使用当前窗口
            self.gamewindow = window_manager.current
        self.hwnd = self.gamewindow.handle

        self._image = None
        client_rect = self.gamewindow.client_rect

        if rect:  # 使用自定义矩形区域（相对于客户区）
            self.rect = rect
        else:
            self.rect = client_rect

        self._log = _log
        self._debug = debug

        # 最多重试10次
        for i in range(10):
            if not window_manager.is_alive:
                return

            try:
                if config.backend:
                    self._screenshot_backend(self.rect)
                else:
                    window_rect = (
                        self.gamewindow.client_left + self.rect[0],
                        self.gamewindow.client_top + self.rect[1],
                        self.rect[2],
                        self.rect[3],
                    )
                    self._screenshot_front(window_rect)
                break

            except Exception as e:
                logger.error(f"截图失败: {str(e)}")
                logger.ui_error(f"截图失败，重试第{i + 1}次")
                time.sleep(0.1)

    def _screenshot_front(self, window_rect: tuple[int, int, int, int]) -> Image.Image:
        # ImageGrab.grab() 需要一个四元组 (left, top, right, bottom)
        _rect = (window_rect[0], window_rect[1], window_rect[0] + window_rect[2], window_rect[1] + window_rect[3])
        _start = time.perf_counter()
        image = ImageGrab.grab(_rect)
        _end = time.perf_counter()
        self.time_cost = round((_end - _start) * 1000, 2)
        if self._log:
            logger.info(f"screenshot front cost {self.time_cost} ms, {window_rect}")
        if self._debug:
            image.show()
        self._image = image
        return image

    def _screenshot_backend(self, client_rect: tuple[int, int, int, int]) -> Image.Image:
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
        saveBitMap.CreateCompatibleBitmap(mfcDC, client_rect[2], client_rect[3])
        # 将截图保存到saveBitMap中
        saveDC.SelectObject(saveBitMap)
        # 保存bitmap到内存设备描述表
        saveDC.BitBlt(
            (0, 0),
            (client_rect[2], client_rect[3]),
            mfcDC,
            (client_rect[0], client_rect[1]),
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
