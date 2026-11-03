import time
from collections.abc import Iterable

import win32api
import win32con
import win32gui

from .client_discovery import build_client_items, discover_process_clients
from .config import GameLanguage, config
from .emulator.mumu_handle import build_handle, detect_mumu_folder, fit_display_size, is_window
from .log import logger
from .message import MessageBoxPayload
from .signals import signal_manager

SCREEN_SIZE = (
    win32api.GetSystemMetrics(win32con.SM_CXSCREEN),
    win32api.GetSystemMetrics(win32con.SM_CYSCREEN),
)

STANDARD_CLIENT_WIDTH: int = 1136
"""基准客户区宽度"""

STANDARD_CLIENT_HEIGHT: int = 640
"""基准客户区高度"""


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
    control_hwnds: list[int]
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
        self.control_hwnds: list[int] = []
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


class GameWindowManager:
    """游戏窗口"""

    window_title_zh: str = "阴阳师-网易游戏"  # 国服
    window_title_zh_mumu: str = "阴阳师-MuMu模拟器专版"  # 国服MuMu专版
    window_title_ja: str = "陰陽師Onmyoji"  # 日服

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
        self._custom_size: tuple[int, int] | None = None  # 用户自定义的目标尺寸（持久化于 config）
        # 启动时读取持久化的自定义尺寸，作为本次会话的规范化目标（重启后仍记住用户的缩放偏好）
        _w = int(getattr(config.user, "custom_window_width", 0) or 0)
        _h = int(getattr(config.user, "custom_window_height", 0) or 0)
        if _w > 0 and _h > 0:
            self._custom_size = (_w, _h)
        self._resizing: bool = False  # 缩放进行中标记（窗口信息线程据此挂起强制缩放检测）

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

    def topmost_window(self, windows: list[GameWindow]) -> GameWindow:
        """返回 Z 序最靠前（最上层）的窗口。

        EnumWindows 按 Z 序自上而下枚举顶层窗口，故首个命中的句柄即当前最上层
        （前置）的游戏窗口。枚举失败时退回首项。
        """
        by_handle = {w.handle: w for w in windows}
        z_order: list[int] = []
        try:
            win32gui.EnumWindows(lambda h, p: p.append(h) or True, z_order)
        except Exception:
            z_order = []
        for hwnd in z_order:
            if hwnd in by_handle:
                return by_handle[hwnd]
        return windows[0]

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

        桌面版：按客户区尺寸与规范化目标比较（不看外框，容差 5px）；
        模拟器：按显示区（截图帧）尺寸与规范化目标比较（容差 2px）。
        规范化目标默认 1136x640；用户自定义缩放后跟随自定义尺寸，
        否则自定义尺寸会被判为不匹配，点「应用」时又被弹回基准。
        """
        window = self.current
        target_w, target_h = self.zoom_target
        if window.family == "mumu":
            w = int(getattr(window, "content_width", 0) or 0)
            h = int(getattr(window, "content_height", 0) or 0)
            if w <= 0 or h <= 0:
                return False  # 尺寸未知，不提示
            return abs(w - target_w) > 2 or abs(h - target_h) > 2
        w = int(getattr(window, "client_width", 0) or 0)
        h = int(getattr(window, "client_height", 0) or 0)
        if w <= 0 or h <= 0:
            return False  # 尺寸未知，不提示
        return abs(w - target_w) > 5 or abs(h - target_h) > 5

    def _emit_window_status_changed(self):
        """发出窗口状态更新信号"""
        count = len(self.handles)
        current_text = f"{self.current.title} - {self.current.handle}" if self.current else ""
        signal_manager.main.window_status_changed.emit(count, current_text)

    def _resize_pc_client(self, width: int, height: int) -> bool:
        """桌面版按客户区精准缩放（迭代修正窗口外框尺寸）

        外框/标题栏厚度随 DPI、主题变化，固定偏移量并不精确，因此按「当前客户区 vs 目标客户区」的差值迭代修正窗口总尺寸。

        Args:
            width (int): 目标客户区宽度
            height (int): 目标客户区高度

        Returns:
            bool: 客户区是否达到目标尺寸（误差 ≤5px）
        """
        window = self.current
        tolerance: int = 5  # 误差范围，单位像素
        try:
            rect = win32gui.GetWindowRect(window.handle)
            win_w, win_h = rect[2] - rect[0], rect[3] - rect[1]
            for _ in range(5):
                cr = win32gui.GetClientRect(window.handle)
                cw, ch = cr[2] - cr[0], cr[3] - cr[1]
                dw, dh = width - cw, height - ch
                if abs(dw) <= tolerance and abs(dh) <= tolerance:
                    break
                win_w, win_h = win_w + dw, win_h + dh
                win32gui.SetWindowPos(
                    window.handle,
                    win32con.HWND_TOP,
                    0,
                    0,
                    win_w,
                    win_h,
                    win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE,
                )
                time.sleep(0.05)
            cr = win32gui.GetClientRect(window.handle)
            cw, ch = cr[2] - cr[0], cr[3] - cr[1]
            if abs(cw - width) > tolerance or abs(ch - height) > tolerance:
                logger.ui_error(f"缩放未达标：客户区 {cw}x{ch}，目标 {width}x{height}")
                return False
        except Exception as e:
            logger.ui_error(f"缩放失败: {e!s}")
            return False
        try:
            self.current = GameWindow(window.handle, family="pc", instance_index=window.instance_index)
        except Exception as e:
            logger.warning(f"重建游戏窗口失败：{e}")
        return True

    def _resize_mumu_client(self, width: int, height: int) -> bool:
        """模拟器按显示区（截图帧）客户区缩放

        通过 fit_display_size 迭代调整显示子窗口尺寸，成功后重建窗口对象
        以刷新客户区/内容尺寸；误差超过 2px 视为未达标。

        Args:
            width (int): 目标显示区宽度
            height (int): 目标显示区高度

        Returns:
            bool: 显示区是否达到目标尺寸
        """
        window = self.current
        shot_hwnd = int(getattr(window, "shot_hwnd", 0) or 0)
        if not shot_hwnd or not is_window(int(window.handle)) or not is_window(shot_hwnd):
            logger.ui_error("模拟器窗口无效，缩放失败")
            return False
        try:
            final = fit_display_size(window.handle, shot_hwnd, width, height)
        except Exception as e:
            logger.ui_error(f"缩放失败: {e!s}")
            return False
        try:
            # 尺寸可能已变化（含未达标时的部分调整），客户区/内容尺寸都过期，重建窗口对象
            self.current = GameWindow(window.handle, family="mumu", instance_index=window.instance_index)
        except Exception as e:
            logger.warning(f"重建游戏窗口失败：{e}")
        if abs(int(final[0]) - width) > 2 or abs(int(final[1]) - height) > 2:
            logger.ui_error(f"缩放未达标：显示区 {final[0]}x{final[1]}，目标 {width}x{height}")
            return False
        return True

    def resize_window(self, width: int | None = None, height: int | None = None) -> bool:
        """主动缩放：把窗口调整到指定客户区宽高

        Args:
            width (int | None): 目标客户区宽度，默认取规范化目标（自定义过则用自定义尺寸，否则 1136）
            height (int | None): 目标客户区高度，默认取规范化目标（自定义过则用自定义尺寸，否则 640）

        Returns:
            bool: 是否调整成功（窗口不存在、位置异常或尺寸未达标时返回 False）
        """
        if not self.current:
            logger.ui_error("请先获取游戏窗口")
            return False

        explicit = width is not None or height is not None
        target_w, target_h = self.zoom_target
        width = int(target_w if width is None else width)
        height = int(target_h if height is None else height)
        if width <= 0 or height <= 0:
            logger.ui_error("宽度和高度必须为正整数")
            return False

        # 窗口位于屏幕边缘/后台时 SetWindowPos 可能不生效，此时不做缩放
        if self.current.family != "mumu" and (self.current.window_left == 0 or self.current.window_top == 0):
            logger.ui_error("缩放失败")
            return False

        # 缩放期间窗口尺寸反复变化（模拟器迭代逼近最长 8 轮），窗口信息线程会读到中间尺寸：
        # 置位标记让检测线程挂起强制缩放判断，避免缩放未完成时又被判「不匹配」再次弹窗
        self._resizing = True
        try:
            if self.current.family == "mumu":
                if not self._resize_mumu_client(width, height):
                    logger.ui_error("缩放失败")
                    return False
            elif not self._resize_pc_client(width, height):
                logger.ui_error("缩放失败")
                return False
        finally:
            self._resizing = False

        # 以下仅在成功后生效：
        # - 记录并持久化自定义目标：失败时记录会让不可达的目标反复触发强制缩放提示；
        # - 重置 _force_zoom_flag 允许后续再次提示：失败时保持拦截，避免「确认→失败→下一秒再弹」循环
        if explicit:
            self._custom_size = (width, height)
            config.update("custom_window_width", width)
            config.update("custom_window_height", height)
            if self.current.family != "mumu" and (width, height) != (STANDARD_CLIENT_WIDTH, STANDARD_CLIENT_HEIGHT):
                logger.ui_warn("桌面版识别基准为 1136x640，非基准尺寸可能导致识别失败")
        self._force_zoom_flag = False

        logger.ui("缩放成功")
        logger.info(f"窗口客户区已调整为 {width}x{height}")
        return True

    def _check_force_zoom(self) -> bool:
        """检查是否需要强制缩放"""
        # 已提示待处理，或缩放正在进行（窗口尺寸处于中间态，判断无意义）时挂起
        if self._force_zoom_flag or self._resizing:
            return False

        if not self.current:
            return False

        if self._need_force_zoom():
            if config.user.remember_force_zoom_choice:
                if config.user.force_zoom_accepted:
                    self.resize_window()
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
            # 首次获取或原窗口消失：取最上层（前置）的游戏窗口
            new_window = self.topmost_window(game_windows)
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

    def force_update(self, handle: int | None = None):
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
            # 「检测前置游戏窗口」：在发现的窗口里取最上层（前置）的一个
            self._update(self.topmost_window(wins))
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
            logger.ui_error(f"将游戏窗口置于前台失败: {e!s}")
            return False

    @property
    def is_alive(self) -> bool:
        """检查游戏窗口是否存在"""
        return self.current is not None

    @property
    def is_emulator(self) -> bool:
        """当前是否为模拟器窗口（family 为 mumu）"""
        return self.current is not None and getattr(self.current, "family", "pc") == "mumu"

    @property
    def zoom_target(self) -> tuple[int, int]:
        """强制缩放的规范化目标尺寸：用户自定义过则用自定义尺寸，否则基准 1136x640"""
        return self._custom_size or (STANDARD_CLIENT_WIDTH, STANDARD_CLIENT_HEIGHT)

    def get_current_handle(self) -> int | None:
        """获取当前游戏窗口句柄，窗口未初始化时返回 None"""
        if self.current is None:
            logger.ui_error("游戏窗口未初始化")
            return None
        return self.current.handle


window_manager = GameWindowManager()
