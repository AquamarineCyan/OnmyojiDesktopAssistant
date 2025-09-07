import win32gui

from .window import window_manager


class Point:
    def __init__(
        self,
        client_x: int = None,
        client_y: int = None,
        window_x: int = None,
        window_y: int = None,
        screen_x: int = None,
        screen_y: int = None,
    ):
        """新坐标类，优先客户端坐标，即去除窗口标题栏的坐标
        参数:
            client_x/y (int): 客户区坐标 (窗口内容区域)
            window_x/y (int): 窗口相对坐标 (包含标题栏和边框) # TODO 弃用
            screen_x/y (int): 屏幕绝对坐标

        """
        self.client_x: int = client_x
        self.client_y: int = client_y
        self.window_x: int = window_x
        self.window_y: int = window_y
        self.screen_x: int = screen_x
        self.screen_y: int = screen_y

        if window_manager.current is None:
            return
        handle = window_manager.current.handle  # 从window_manager获取当前窗口句柄

        # 获取窗口和客户区矩形
        self.client_rect = window_manager.current.client_rect
        self.window_rect = window_manager.current.window_rect

        # 计算客户区在屏幕中的左上角位置
        self.client_top_left = win32gui.ClientToScreen(handle, (0, 0))

        # 根据提供的坐标类型计算其他坐标系
        if client_x is not None and client_y is not None:
            self._set_from_client(client_x, client_y)
        elif window_x is not None and window_y is not None:
            self._set_from_relative(window_x, window_y)
        elif screen_x is not None and screen_y is not None:
            self._set_from_absolute(screen_x, screen_y)
        else:
            # 默认值
            self.client_x = 0
            self.client_y = 0
            self.window_x = 0
            self.window_y = 0
            self.screen_x = 0
            self.screen_y = 0

    def _set_from_client(self, x, y):
        """从客户区坐标设置"""
        self.client_x = x
        self.client_y = y

        # 计算绝对坐标
        self.screen_x = self.client_top_left[0] + x
        self.screen_y = self.client_top_left[1] + y

        # 计算相对坐标
        self.window_x = self.screen_x - self.window_rect[0]
        self.window_y = self.screen_y - self.window_rect[1]

    def _set_from_relative(self, x, y):
        """从窗口相对坐标设置"""
        self.window_x = x
        self.window_y = y

        # 计算绝对坐标
        self.screen_x = self.window_rect[0] + x
        self.screen_y = self.window_rect[1] + y

        # 计算客户区坐标
        self.client_x = self.screen_x - self.client_top_left[0]
        self.client_y = self.screen_y - self.client_top_left[1]

    def _set_from_absolute(self, x, y):
        """从屏幕绝对坐标设置"""
        self.screen_x = x
        self.screen_y = y

        # 计算相对坐标
        self.window_x = x - self.window_rect[0]
        self.window_y = y - self.window_rect[1]

        # 计算客户区坐标
        self.client_x = x - self.client_top_left[0]
        self.client_y = y - self.client_top_left[1]

    def set_x(self, x_offset: int):
        self.client_x = self.client_x + x_offset
        self.window_x = self.window_x + x_offset
        self.screen_x = self.screen_x + x_offset

    def set_y(self, y_offset: int):
        self.client_y = self.client_y + y_offset
        self.window_y = self.window_y + y_offset
        self.screen_y = self.screen_y + y_offset

    def __repr__(self):
        return (
            f"Point("
            f"client=({self.client_x}, {self.client_y}), "
            f"relative=({self.window_x}, {self.window_y}), "
            f"absolute=({self.screen_x}, {self.screen_y}))"
        )


class Rectangle:
    """矩形"""

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = None,
        height: int = None,
        x2: int = None,
        y2: int = None,
    ):
        assert width is None or x2 is None, "Cannot specify both x2, y2 and width, height at the same time"

        assert (width is not None and height is not None) or (x2 is not None and y2 is not None), (
            "width, height or x2, y2 must have one pair of data"
        )

        self.x1 = x
        self.y1 = y

        if width and height:
            self.width = width
            self.height = height
            self.x2 = x + width
            self.y2 = y + height
        elif x2 and y2:
            self.x2 = x2
            self.y2 = y2
            self.width = x2 - x
            self.height = y2 - y

    def get_box(self) -> tuple[int, int, int, int]:
        return (self.x1, self.y1, self.width, self.height)

    def get_coordinates(self) -> tuple[int, int, int, int]:
        return (self.x1, self.y1, self.x2, self.y2)

    def get_center(self) -> tuple[float, float]:
        return (self.x1 + self.width / 2, self.y1 + self.height / 2)
