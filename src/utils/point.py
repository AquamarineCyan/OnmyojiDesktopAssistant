from .window import SCREEN_SIZE, window


class Point:
    """
    坐标
    `RelativePoint`: 相对坐标
    `AbsolutePoint`: 绝对坐标

    用法:
        bool(point): 返回坐标是否有效
        point.coor: 返回坐标(x,y)
    """

    x: float = 0
    y: float = 0

    def __init__(self, x: float = 0, y: float = 0) -> None:
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

    def abs_to_rela(self) -> "RelativePoint":
        x = self.x - window.window_left
        y = self.y - window.window_top
        return RelativePoint(x, y)


class RelativePoint(Point):
    """相对坐标

    对应游戏窗口内，一般包括windows窗口外框
    """

    def __init__(self, x: float = 0, y: float = 0) -> None:
        super().__init__(x, y)

    def rela_to_abs(self) -> "AbsolutePoint":
        x = self.x + window.window_left
        y = self.y + window.window_top
        width, height = SCREEN_SIZE
        if 0 <= x < width and 0 <= y < height:
            return AbsolutePoint(x, y)


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
        assert (
            width is None or x2 is None
        ), "Cannot specify both x2, y2 and width, height at the same time"

        assert (width is not None and height is not None) or (
            x2 is not None and y2 is not None
        ), "width, height or x2, y2 must have one pair of data"

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

    def get_box(self):
        return (self.x1, self.y1, self.width, self.height)

    def get_coordinates(self):
        return (self.x1, self.y1, self.x2, self.y2)

    def get_center(self):
        return (self.x1 + self.width / 2, self.y1 + self.height / 2)

    def get_rela_center(self) -> "RelativePoint":
        return RelativePoint(self.x1 + self.width / 2, self.y1 + self.height / 2)
