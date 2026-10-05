import time
from typing import Iterable

import win32api
import win32con
import win32gui

from .config import GameLanguage, config
from .decorator import log_function_call
from .log import logger
from .message import MessageBoxPayload
from .signals import signal_manager

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

    family: str = "pc"
    """窗口家族：'pc'（桌面版）/'mumu'（MuMu 模拟器）"""
    shot_hwnd: int = 0
    control_hwnds: list[int] = []
    scale_rate: float = 1.0
    instance_index: int = 0

    @property
    def label(self) -> str:
        n = self.instance_index + 1
        if self.family == "mumu":
            return f"模拟器 - 实例{n} - {self.title}"
        return f"桌面版 - 实例{n} - {self.title} - {self.handle}"

    def __init__(self, handle: int, family: str | None = None, instance_index: int = 0):
        self.handle = int(handle)
        self.instance_index = int(instance_index)
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

        # 内容（帧）尺寸：pc 与客户区一致；mumu 探针成功后改写为 shot(nemudisplay) 客户区，
        # 因为后台截图帧正是 shot 尺寸（模板缩放必须以此为准，root 客户区含播放器工具条）。
        self.content_width = self.client_width
        self.content_height = self.client_height

        # 计算客户区在屏幕中的左上角位置
        self.client_top_left = win32gui.ClientToScreen(handle, (0, 0))
        self.client_left: int = self.client_top_left[0]
        self.client_top: int = self.client_top_left[1]

        # 家族判定：调用方（进程发现）已给出 family 时直接采用，不再探测；
        # 未给出时按句柄树自动判定（适配 Qt/nemuwin 树），失败即 pc。
        # 不再依赖 emulator_type 开关与窗口标题。
        if family in ("mumu", "pc"):
            self.family = family
            if family == "pc":
                return
        else:
            self.family = "pc"

        # 决策 A：开关关闭时一律按桌面版处理，且不做任何模拟器探测
        if not config.user.interaction_mode.backend.enable_mumu:
            self.family = "pc"
            return
        try:
            from .emulator.mumu_handle import build_handle, detect_mumu_folder
        except Exception:
            return
        try:
            folder = detect_mumu_folder(config.user.interaction_mode.backend.mumu_folder)
        except Exception:
            folder = ""
        if not folder:
            return
        try:
            h = build_handle(self.handle, mumu_folder=folder, wait_tries=1)
        except Exception:
            self.family = "pc"
            return
        self.family = "mumu"
        self.shot_hwnd = h.shot_hwnd
        self.control_hwnds = h.control_hwnds
        self.scale_rate = h.scale_rate
        try:
            cr = win32gui.GetClientRect(self.shot_hwnd)
            w, hh = cr[2] - cr[0], cr[3] - cr[1]
            if w > 0 and hh > 0:
                self.content_width, self.content_height = w, hh
        except Exception:
            pass

    def display(self):
        s = "游戏窗口信息\n"
        s += f"{self.title}\n"
        s += f"窗口句柄:{self.handle}\n"
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

    window_check_interval: float = 1.0
    """窗口信息线程更新间隔（秒）"""

    def __init__(self):
        self._window_title: str = self.window_title_zh

        self.current: GameWindow = None  # 当前窗口
        self.handles: list[GameWindow] = []  # 窗口句柄列表

        self._initialized: bool = False
        self._background_flag: bool = False
        self._force_zoom_flag: bool = False
        self._close_window_flag: bool = False
        self._last_check_timestamp: float = 0.0  # 上次检测时间戳

    def screen_init(self):
        """初始化屏幕分辨率"""
        logger.ui(f"屏幕分辨率：{SCREEN_SIZE[0]}x{SCREEN_SIZE[1]}")
        if SCREEN_SIZE == WindowResolution1920.screen_size:
            self.current_window_resolution = WindowResolution1920()
        elif SCREEN_SIZE == WindowResolution2560.screen_size:
            self.current_window_resolution = WindowResolution2560()
        else:
            self.current_window_resolution = WindowResolutionDefault()

    def set_window_title(self, language: GameLanguage):
        if language == GameLanguage.CN:
            self._window_title = self.window_title_zh
        elif language == GameLanguage.JA:
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

    def discover(self) -> list[GameWindow]:
        """发现窗口：进程优先（桌面版在前、模拟器在后，各自按序编号），零发现才回落标题兜底。"""
        from .client_discovery import build_client_items, discover_process_clients

        out: list[GameWindow] = []
        seen: set[int] = set()
        try:
            clients = discover_process_clients(
                config.user.interaction_mode.backend.mumu_folder,
                enable_emulator=bool(config.user.interaction_mode.backend.enable_mumu),
            )
        except Exception:
            clients = []
        for label, client in build_client_items(clients, fallback_titles=list(self._titles_to_search())):
            if client is None:
                for hwnd in get_all_target_window([label]):
                    if hwnd in seen:
                        continue
                    try:
                        out.append(GameWindow(hwnd))
                    except Exception:
                        continue
                    seen.add(hwnd)
                continue
            if int(client.hwnd) in seen:
                continue
            try:
                w = GameWindow(
                    int(client.hwnd),
                    family=client.kind == "emulator" and "mumu" or "pc",
                    instance_index=(client.index or 1) - 1,
                )
            except Exception:
                continue
            out.append(w)
            seen.add(int(client.hwnd))
        return out

    def _update(self, window: GameWindow):
        self.current = window
        self.current.display()
        if self.current.family == "mumu":
            # 模拟器：显示区尺寸不匹配时复用桌面版的「强制缩放」确认流程
            self._check_force_zoom()
            return  # 模拟器最小化是常态，跳过"前置窗口"检查
        if not self._check_background():
            self._check_force_zoom()

    def _need_force_zoom(self) -> bool:
        """窗口尺寸是否需要规范化

        桌面版：按窗口矩形与标准窗口尺寸比较；
        模拟器：按显示区（截图帧）尺寸与基准 1136x640 比较。
        """
        from .coordinate import STANDARD_CLIENT_HEIGHT, STANDARD_CLIENT_WIDTH

        window = self.current
        if window.family == "mumu":
            w = int(getattr(window, "content_width", 0) or 0)
            h = int(getattr(window, "content_height", 0) or 0)
            if w <= 0 or h <= 0:
                return False  # 尺寸未知，不提示
            return abs(w - STANDARD_CLIENT_WIDTH) > 2 or abs(h - STANDARD_CLIENT_HEIGHT) > 2
        return not is_rect_within_range(
            window.window_rect,
            self.current_window_resolution.window_standard_width,
            self.current_window_resolution.window_standard_height,
        )

    def _force_zoom_emulator(self) -> bool:
        """模拟器强制缩放：把显示区规范化到基准尺寸 1136x640"""
        from .coordinate import STANDARD_CLIENT_HEIGHT, STANDARD_CLIENT_WIDTH
        from .emulator.mumu_handle import fit_display_size, is_window

        window = self.current
        shot_hwnd = int(getattr(window, "shot_hwnd", 0) or 0)
        if not shot_hwnd or not is_window(int(window.handle)) or not is_window(shot_hwnd):
            logger.ui_error("模拟器窗口无效，强制缩放失败")
            return False
        try:
            final = fit_display_size(
                window.handle,
                shot_hwnd,
                STANDARD_CLIENT_WIDTH,
                STANDARD_CLIENT_HEIGHT,
            )
        except Exception as e:
            logger.ui_error(f"强制缩放失败: {str(e)}")
            return False
        try:
            # 尺寸可能已变化（含未达标时的部分调整），客户区/内容尺寸都过期，重建窗口对象
            self.current = GameWindow(window.handle, family="mumu", instance_index=window.instance_index)
        except Exception as e:
            logger.warning(f"重建游戏窗口失败：{e}")
        if abs(int(final[0]) - STANDARD_CLIENT_WIDTH) > 2 or abs(int(final[1]) - STANDARD_CLIENT_HEIGHT) > 2:
            logger.ui_error(
                f"强制缩放未达标：显示区 {final[0]}x{final[1]}，"
                f"目标 {STANDARD_CLIENT_WIDTH}x{STANDARD_CLIENT_HEIGHT}（请恢复模拟器窗口后重试）"
            )
            return False
        logger.ui("强制缩放成功")
        logger.info(f"模拟器显示区已调整为 {final[0]}x{final[1]}")
        return True

    def _emit_window_status_changed(self):
        """发出窗口状态更新信号"""
        count = len(self.handles)
        current_text = f"{self.current.title} - {self.current.handle}" if self.current else ""
        signal_manager.main.window_status_changed.emit(count, current_text)

    def force_zoom(self):  # TODO 比例差一点
        """强制缩放：桌面版调整到标准窗口尺寸；模拟器把显示区调整到 1136x640"""
        if not self.current:
            logger.ui_error("请先获取游戏窗口")
            return False

        self._force_zoom_flag = False

        if self.current.family == "mumu":
            return self._force_zoom_emulator()

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

        if self._need_force_zoom():
            if config.user.remember_force_zoom_choice:
                if config.user.force_zoom_accepted:
                    self.force_zoom()
                else:
                    logger.info("用户此前已选择不强制缩放，不再提醒")
                return True

            signal_manager.main.message_box_requested.emit(
                MessageBoxPayload.question(MessageBoxPayload.Action.FORCE_ZOOM)
            )
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
            signal_manager.main.message_box_requested.emit(MessageBoxPayload.error("请前置游戏窗口！"))
            self._background_flag = True
            return True

        return False

    def update_window_task(self):
        """更新游戏窗口信息"""
        now = time.monotonic()
        if now - self._last_check_timestamp < self.window_check_interval:
            return
        self._last_check_timestamp = now

        game_windows = self.discover()
        target_handles = [w.handle for w in game_windows]
        old_handles = [w.handle for w in self.handles]

        if target_handles != old_handles:
            logger.info(f"检测到游戏窗口变化，当前窗口数量：{len(target_handles)}")
            self.handles = game_windows
            if hasattr(self, "gui_window_manager_list_callback"):
                self.gui_window_manager_list_callback(game_windows)

        if not game_windows:
            self.current = None  # 未找到游戏窗口
            if self._initialized and not self._close_window_flag:
                logger.info("游戏窗口已关闭")
                self._close_window_flag = True
            self._emit_window_status_changed()
            return

        if not self._initialized and hasattr(self, "gui_button_callback"):
            self._initialized = True
            self.gui_button_callback()

        # 统一处理逻辑
        if self.current is None or self.current.handle not in target_handles:
            # 首次获取或原窗口消失
            new_window = game_windows[0]
            logger.info("更新游戏窗口" if self.current else "首次获取游戏窗口")
            self._update(new_window)
            self._emit_window_status_changed()
            return

        # 检查窗口变化
        new_window = GameWindow(self.current.handle)
        if not self._compare(self.current.window_rect, new_window.window_rect):
            logger.info("检测到游戏窗口变化")
            self._update(new_window)

        self._emit_window_status_changed()

    def force_update(self, handle: int = None):
        """强制更新游戏窗口

        Args:
            handle (int): 选中的句柄。默认为空。
        """
        if handle:
            self._update(GameWindow(handle))
        else:
            wins = self.discover()
            if not wins:
                logger.ui_error("未找到游戏窗口")
                return
            self._update(wins[0])
        self._emit_window_status_changed()

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

    @property
    def is_emulator(self) -> bool:
        """当前是否为模拟器窗口（family 为 mumu）"""
        return self.current is not None and getattr(self.current, "family", "pc") == "mumu"

    def get_current_handle(self) -> int | None:
        """获取当前游戏窗口句柄，窗口未初始化时返回 None"""
        if self.current is None:
            logger.ui_error("游戏窗口未初始化")
            return None
        return self.current.handle


window_manager = GameWindowManager()


@log_function_call
def is_rect_within_range(rect, range_width, range_height):
    x1, y1, x2, y2 = rect
    offset = 10
    return (
        range_width - offset <= (x2 - x1) < range_width + offset
        and range_height - offset <= (y2 - y1) < range_height + offset
    )
