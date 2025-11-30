from typing import Iterable, Literal

import win32api
import win32con
import win32gui

from .decorator import log_function_call
from .log import logger
from .mysignal import global_ms as ms

SCREEN_SIZE = (
    win32api.GetSystemMetrics(win32con.SM_CXSCREEN),
    win32api.GetSystemMetrics(win32con.SM_CYSCREEN),
)


def enum_windows(hwnd, result_list):
    result_list.append(hwnd)
    return True


def get_all_target_window(target_titles: str | Iterable[str]) -> list[int]:
    """返回所有符合标题的窗口句柄

    参数:
        target_titles (str | Iterable[str]): 单个标题或可迭代的多个窗口标题

    返回:
        list[int]: 符合任意标题的窗口句柄列表（可能为空）
    """
    if target_titles is None:
        return []

    if isinstance(target_titles, str):
        titles = {target_titles}
    else:
        titles = {t for t in target_titles if t}

    window_list = []
    win32gui.EnumWindows(enum_windows, window_list)
    target_handles: list[int] = []
    for hwnd in window_list:
        if win32gui.GetWindowText(hwnd) in titles:
            target_handles.append(hwnd)
    return target_handles


class GameWindow:
    handle: int = 0

    window_rect: tuple[int, int, int, int] = (0, 0, 0, 0)
    """窗口矩形坐标 (left, top, right, bottom)"""

    client_rect: tuple[int, int, int, int] = (0, 0, 0, 0)
    """客户区矩形坐标 (left, top, right, bottom)"""

    def __init__(self, handle: int):
        self.handle = int(handle)
        self.title = win32gui.GetWindowText(self.handle)

        # 偏移量见类初始定义
        self.window_rect = win32gui.GetWindowRect(self.handle)
        self.window_left = self.window_rect[0] + 9
        self.window_top = self.window_rect[1]
        self.window_right = self.window_rect[2] - 9
        self.window_bottom = self.window_rect[3] - 8
        self.window_width = self.window_rect[2] - self.window_rect[0] - 18
        self.window_height = self.window_rect[3] - self.window_rect[1] - 47

        self.client_rect = win32gui.GetClientRect(self.handle)
        self.client_width = self.client_rect[2] - self.client_rect[0]
        self.client_height = self.client_rect[3] - self.client_rect[1]

        # 计算客户区在屏幕中的左上角位置
        self.client_top_left = win32gui.ClientToScreen(handle, (0, 0))
        self.client_left: int = self.client_top_left[0]
        self.client_top: int = self.client_top_left[1]

    def display(self):
        s = "游戏窗口信息\n"
        s += f"{self.title}\n"
        s += f"左侧横坐标:{self.window_left}\n"
        s += f"顶部纵坐标:{self.window_top}\n"
        s += f"右侧横坐标:{self.window_right}\n"
        s += f"底部纵坐标:{self.window_bottom}\n"
        s += f"窗口宽度:{self.window_width}\n"
        s += f"窗口高度:{self.window_height}"
        logger.ui(s)


class WindowResolution:
    screen_size: tuple[int, int]
    """屏幕尺寸，16:9"""
    window_standard_width: int
    """窗口标准宽度"""
    window_standard_height: int
    """窗口标准高度"""


class WindowResolutionDefault(WindowResolution):
    """默认值"""

    screen_size = (1920, 1080)
    window_standard_width: int = 1136 + 18
    window_standard_height: int = 640 + 39 + 8


class WindowResolution1920(WindowResolution):
    """1920x1080"""

    screen_size = (1920, 1080)
    window_standard_width: int = 1136 + 18
    window_standard_height: int = 640 + 39 + 8


class WindowResolution2560(WindowResolution):
    """2560x1440"""

    # (704, 369, 1856, 1048)
    screen_size = (2560, 1440)
    window_standard_width: int = 1152
    window_standard_height: int = 679


class GameWindowManager:
    """游戏窗口"""

    window_standard_width: int = 1136 + 18
    """窗口标准宽度（官方1136+外框18=1154）"""
    window_standard_height: int = 640 + 39 + 8
    """窗口标准高度（官方640+标题栏39+外框8=687）"""

    window_title_zh: str = "阴阳师-网易游戏"  # 国服
    window_title_zh_mumu: str = "阴阳师-MuMu模拟器专版"  # 国服MuMu专版
    window_title_ja: str = "陰陽師Onmyoji"  # 日服

    current_window_resolution: WindowResolution = None
    """当前游戏窗口的分辨率"""

    def __init__(self):
        self._window_title: str = self.window_title_zh

        self.current: GameWindow = None  # 当前窗口
        self.handles: list[GameWindow] = []  # 窗口句柄列表

        self._initialized: bool = False
        self._background_flag: bool = False
        self._force_zoom_flag: bool = False
        self._close_window_flag: bool = False

    def screen_init(self):
        """初始化屏幕分辨率"""
        logger.ui(f"屏幕分辨率：{SCREEN_SIZE}")
        if SCREEN_SIZE == WindowResolution1920.screen_size:
            self.current_window_resolution = WindowResolution1920()
        elif SCREEN_SIZE == WindowResolution2560.screen_size:
            self.current_window_resolution = WindowResolution2560()
        else:
            self.current_window_resolution = WindowResolutionDefault()

    def set_window_title(self, language: str = Literal["国服", "日服"]):
        if language == "国服":
            self._window_title = self.window_title_zh
        elif language == "日服":
            self._window_title = self.window_title_ja

    def set_gui_button_callback(self, callback):
        """设置GUI按钮回调函数"""
        self.gui_button_callback = callback

    def set_gui_window_manager_list_callback(self, callback):
        """设置GUI窗口管理列表回调函数"""
        self.gui_window_manager_list_callback = callback

    def _titles_to_search(self) -> tuple[str, ...]:
        """返回用于搜索的窗口标题元组。

        - 国服（默认）尝试两个标题：普通 + MuMu 专版
        - 日服或其它只尝试当前设置的标题
        """
        if self._window_title == self.window_title_zh:
            return (self.window_title_zh, self.window_title_zh_mumu)
        return (self._window_title,)

    def _compare(self, old_rect: tuple[int, int, int, int], new_rect: tuple[int, int, int, int]) -> bool:
        """比较新旧窗口矩形坐标是否相同

        参数:
            old_rect (tuple[int, int, int, int]): 旧窗口
            new_rect (tuple[int, int, int, int]): 新窗口

        返回:
            bool: 是否相同
        """
        return old_rect == new_rect

    def _update(self, window: GameWindow):
        self.current = window
        self.current.display()
        if not self._check_background():
            self._check_force_zoom()

    def force_zoom(self):  # TODO 比例差一点
        """强制缩放 1154*687"""
        if not self.current:
            logger.ui_error("请先获取游戏窗口")
            return False

        self._force_zoom_flag = False

        if self.current.window_left != 0 and self.current.window_top != 0:
            try:
                win32gui.SetWindowPos(
                    self.current.handle,
                    win32con.HWND_TOP,
                    0,
                    0,
                    self.current_window_resolution.window_standard_width,
                    self.current_window_resolution.window_standard_height,
                    win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE,
                )
                logger.ui("强制缩放成功")
            except Exception as e:
                logger.ui_error(f"强制缩放失败: {str(e)}")
                return False
            return True
        else:
            logger.ui_error("强制缩放失败")
            return False

    def _check_force_zoom(self) -> bool:
        """检查是否需要强制缩放"""
        if self._force_zoom_flag:
            return False

        if not self.current:
            return False

        if not is_rect_within_range(
            self.current.window_rect,
            self.current_window_resolution.window_standard_width,
            self.current_window_resolution.window_standard_height,
        ):
            ms.main.qmessagbox_update.emit("question", "强制缩放")
            logger.info("尝试强制缩放")
            self._force_zoom_flag = True
        return True

    def _check_background(self) -> bool:
        """检查游戏窗口是否在后台"""
        if self._background_flag:
            return False

        rect = self.current.window_rect
        if rect[0] < -9 or rect[1] < 0 or rect[2] < 0 or rect[3] < 0:
            logger.error(f"Game is background, handle_rect:{rect}")
            ms.main.qmessagbox_update.emit("ERROR", "请前置游戏窗口！")
            self._background_flag = True
            return True

        return False

    def update_window_task(self):
        """更新游戏窗口信息"""
        target_handles = get_all_target_window(self._titles_to_search())

        if target_handles != self.handles:
            logger.info(f"检测到游戏窗口变化，当前窗口数量：{len(target_handles)}")
            self.handles = target_handles
            handles = []
            for handle in target_handles:
                handles.append(GameWindow(handle))
            if hasattr(self, "gui_window_manager_list_callback"):
                self.gui_window_manager_list_callback(handles)

        if not target_handles:
            self.current = None  # 未找到游戏窗口
            if self._initialized and not self._close_window_flag:
                logger.info("游戏窗口已关闭")
                self._close_window_flag = True
            return

        if not self._initialized and hasattr(self, "gui_button_callback"):
            self._initialized = True
            self.gui_button_callback()

        # 统一处理逻辑
        if self.current is None or self.current.handle not in target_handles:
            # 首次获取或原窗口消失
            new_handle = target_handles[0]
            logger.info("更新游戏窗口" if self.current else "首次获取游戏窗口")
            self._update(GameWindow(new_handle))
            return

        # 检查窗口变化
        new_window = GameWindow(self.current.handle)
        if not self._compare(self.current.window_rect, new_window.window_rect):
            logger.info("检测到游戏窗口变化")
            self._update(new_window)

        if hasattr(self, "gui_window_manager_list_current_callback"):
            self.gui_window_manager_list_current_callback(self.current)

    def force_update(self, handle: int = None):
        """强制更新游戏窗口

        Args:
            handle (int): 选中的句柄。默认为空。
        """
        if handle:
            self._update(GameWindow(handle))
        else:
            target_handles = get_all_target_window(self._titles_to_search())
            if not target_handles:
                logger.ui_error("未找到游戏窗口")
                return
            self._update(GameWindow(target_handles[0]))

    def set_foreground(self) -> bool:
        """将游戏窗口置于前台"""
        if self.current is None:
            logger.ui_error("请先获取游戏窗口")
            return False
        try:
            win32gui.SetForegroundWindow(self.current.handle)
            logger.ui("游戏窗口已置于前台")
            return True
        except Exception as e:
            logger.ui_error(f"将游戏窗口置于前台失败: {str(e)}")
            return False

    @property
    def is_alive(self) -> bool:
        """检查游戏窗口是否存在"""
        if self.current is None:
            return False
        return True


window_manager = GameWindowManager()


@log_function_call
def is_rect_within_range(rect, range_width, range_height):
    x1, y1, x2, y2 = rect
    offset = 10
    return (
        range_width - offset <= (x2 - x1) < range_width + offset
        and range_height - offset <= (y2 - y1) < range_height + offset
    )
