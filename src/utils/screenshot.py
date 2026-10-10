import time
from ctypes import windll

import cv2
import numpy as np
import win32con
import win32gui
import win32ui
from PIL import Image, ImageGrab

from .config import InteractionMode, ScreenshotMethod, config
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
        self._bgr = None
        self._raw = None  # (buf, (w, h), crop)：后台原始缓冲，惰性重建 PIL 用
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
                if config.user.interaction_mode.mode == InteractionMode.BACKEND:
                    if self.gamewindow.family == "mumu":
                        self._screenshot_mumu()
                    else:
                        self._screenshot_backend(
                            self.rect,
                            config.user.interaction_mode.backend.screenshot_method,
                        )
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
            logger.info(f"screenshot front cost {self.time_cost:.2f} ms, {window_rect}")
        if self._debug:
            image.show()
        self._image = image
        return image

    def _screenshot_mumu(self) -> None:
        """mumu 后台截图：走 MumuBackend（PrintWindow→IPC→BitBlt，最小化走 IPC 不黑屏）。"""
        from .emulator import get_backend

        _start = time.perf_counter()
        backend = get_backend(
            self.hwnd,
            self.gamewindow.instance_index,
            config.user.interaction_mode.backend.mumu_folder,
            config.user.interaction_mode.backend.ipc_dll_override,
        )
        if backend is None:
            raise RuntimeError("mumu backend unavailable")
        img = backend.screenshot()
        if img is None:
            raise RuntimeError("mumu screenshot black/unavailable")
        # 帧即 shot 客户区：先按 rect（客户区相对 (l, t, w, h)）裁剪到帧边界，
        # 与 _screenshot_backend 的裁剪语义一致（image.py 按 region 原点偏移坐标）；
        # 帧本身即 BGR，直接留作 BGR 缓冲（零拷贝切片视图），PIL 图像按需惰性生成
        frame_h, frame_w = img.shape[:2]
        l = max(0, int(self.rect[0]))
        t = max(0, int(self.rect[1]))
        r = min(frame_w, l + int(self.rect[2]))
        b = min(frame_h, t + int(self.rect[3]))
        if r <= l or b <= t:
            raise RuntimeError(f"mumu screenshot rect outside frame: {self.rect}")
        self._bgr = img[t:b, l:r]
        self.time_cost = round((time.perf_counter() - _start) * 1000, 2)
        if self._log:
            logger.info(f"screenshot mumu cost {self.time_cost:.2f} ms, {self.rect}")

    def _screenshot_backend(
        self,
        client_rect: tuple[int, int, int, int],
        method: ScreenshotMethod,
    ) -> np.ndarray:
        """后台截图

        Args:
            client_rect (tuple[int, int, int, int]): 客户区尺寸
            method (ScreenshotMethod): 截图模式

        Returns:
            np.ndarray: 截取图像（BGR，原始缓冲视图）
        """
        _start = time.perf_counter()
        # 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
        hWndDC = win32gui.GetDC(self.hwnd)
        # 创建设备描述表
        mfcDC = win32ui.CreateDCFromHandle(hWndDC)
        # 创建内存设备描述表
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建位图对象准备保存图片
        saveBitMap = win32ui.CreateBitmap()
        client_rect_full = self.gamewindow.client_rect

        # 为bitmap开辟存储空间
        if method == ScreenshotMethod.BITBLT:
            saveBitMap.CreateCompatibleBitmap(mfcDC, client_rect[2], client_rect[3])
        elif method == ScreenshotMethod.PRINTWINDOW:
            saveBitMap.CreateCompatibleBitmap(mfcDC, client_rect_full[2], client_rect_full[3])

        # 将截图保存到saveBitMap中
        saveDC.SelectObject(saveBitMap)

        # 保存bitmap到内存设备描述表
        if method == ScreenshotMethod.BITBLT:
            saveDC.BitBlt(
                (0, 0),
                (client_rect[2], client_rect[3]),
                mfcDC,
                (client_rect[0], client_rect[1]),
                win32con.SRCCOPY,
            )
        elif method == ScreenshotMethod.PRINTWINDOW:
            windll.user32.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), 3)
        else:
            raise ValueError("method must be ScreenshotMethod.BITBLT or ScreenshotMethod.PRINTWINDOW")

        # 获取位图信息
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        # 原始缓冲为 BGRX（4 字节/像素）：reshape 后取前 3 通道即 BGR 视图，
        # 不经 PIL 转换/拷贝（PIL 图像在 get_image() 中按需惰性生成）
        buf = np.frombuffer(bmpstr, dtype=np.uint8)
        full = buf.reshape(bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4)
        if method == ScreenshotMethod.PRINTWINDOW:
            # PRINTWINDOW 截取的是整窗，需按客户区相对坐标裁剪
            crop = (
                client_rect[0],
                client_rect[1],
                client_rect[0] + client_rect[2],
                client_rect[1] + client_rect[3],
            )
            self._raw = (bmpstr, (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), crop)
            self._bgr = full[crop[1] : crop[3], crop[0] : crop[2], :3]
        else:
            self._raw = (bmpstr, (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), None)
            self._bgr = full[:, :, :3]

        # 内存释放
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hWndDC)

        _end = time.perf_counter()
        self.time_cost = round((_end - _start) * 1000, 2)
        if self._log:
            logger.info(f"screenshot backend [{method}] cost {self.time_cost:.2f} ms, {client_rect}")
        if self._debug:
            self.get_image().show()
        return self._bgr

    def save(self, file, *args, **kwargs) -> None:
        self.get_image().save(file, *args, **kwargs)
        logger.info(f"screenshot cost {self.time_cost:.2f} ms, at {file}")

    def get_image(self) -> Image.Image:
        """获取 PIL 图像（惰性：后台优先用原始缓冲重建）"""
        if self._image is None:
            if self._raw is not None:
                buf, size, crop = self._raw
                image = Image.frombuffer("RGB", size, buf, "raw", "BGRX", 0, 1).convert("RGB")
                if crop is not None:
                    image = image.crop(crop)
                self._image = image
                self._raw = None  # 释放原始缓冲
            elif self._bgr is not None:
                # 负步长视图会走 PIL 慢路径（实测约慢 3 倍），先转连续 RGB
                self._image = Image.fromarray(np.ascontiguousarray(self._bgr[:, :, ::-1]))
        return self._image

    def get_bgr(self) -> np.ndarray:
        """获取 BGR 图像（后台截图直接复用原始缓冲视图，免整图转换与拷贝）"""
        if self._bgr is None:
            self._bgr = cv2.cvtColor(np.array(self._image), cv2.COLOR_RGB2BGR)
        return self._bgr
