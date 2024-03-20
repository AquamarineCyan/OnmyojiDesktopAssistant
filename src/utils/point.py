from .window import window, SCREEN_SIZE


class Point:
    """
    坐标
    `RelativePoint`: 相对坐标
    `AbsolutePoint`: 绝对坐标

    用法:
        bool(point): 返回坐标是否有效
        point.coor: 返回坐标(x,y)
    """
    x :float = 0
    y :float = 0

    def __init__(self, x: float = 0, y:  float = 0) -> None:
        """参数:
            x (float): 横轴坐标
            y (float): 纵轴坐标
        """
        self.x: float = x
        self.y: float = y
        self.coor: tuple[float, float] = (self.x, self.y)

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __bool__(self) -> bool:
        return self.x != 0 and self.y != 0


class AbsolutePoint(Point):
    """绝对坐标

    对应屏幕，适用于鼠标点击等事件的传参
    """

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)

    def abs_to_rela(self):
        x = self.x - window.window_left
        y = self.y - window.window_top
        return RelativePoint(x, y)


class RelativePoint(Point):
    """相对坐标

    对应游戏窗口内，一般包括windows窗口外框
    """

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)

    def rela_to_abs(self):
        x = self.x + window.window_left
        y = self.y + window.window_top
        width, height = SCREEN_SIZE
        if 0 <= x < width and 0 <= y < height:
            return AbsolutePoint(x, y)


class RectanglePoint:
    """矩形坐标"""

    def __init__(self, x1, y1, x2, y2) -> None:
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.width = x2 - x1
        self.height = y2 - y1

    def get_rela_center_coor(self):
        """返回矩形的相对中心坐标"""
        x = self.x1 + self.width / 2
        y = self.y1 + self.height / 2
        return RelativePoint(x, y)
