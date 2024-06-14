import pytest


class Rectangle:
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


def test_x_y_width_height():
    rect = Rectangle(10, 20, 100, 200)
    assert rect.x1 == 10
    assert rect.y1 == 20
    assert rect.width == 100
    assert rect.height == 200
    assert rect.x2 == 110
    assert rect.y2 == 220
    assert rect.get_coordinates() == (10, 20, 110, 220)
    assert rect.get_box() == (10, 20, 100, 200)
    assert rect.get_center() == (60, 120)


def test_x_y_x2_y2():
    rect = Rectangle(10, 20, x2=30, y2=60)
    assert rect.x1 == 10
    assert rect.y1 == 20
    assert rect.width == 20
    assert rect.height == 40
    assert rect.x2 == 30
    assert rect.y2 == 60
    assert rect.get_coordinates() == (10, 20, 30, 60)
    assert rect.get_box() == (10, 20, 20, 40)
    assert rect.get_center() == (20, 40)

def test_no_arge():
    with pytest.raises(AssertionError):
        Rectangle()

def test_assert_x2_width():
    with pytest.raises(AssertionError):
        Rectangle(10, 20, x2=30, width=25)


def test_assert_x2_height():
    with pytest.raises(AssertionError):
        Rectangle(10, 20, x2=30, height=25)


def test_assert_x2_without_width_height():
    with pytest.raises(AssertionError):
        Rectangle(10, 20)


def test_assert_x2_width_height():
    with pytest.raises(AssertionError):
        Rectangle(10, 20, x2=30, width=25, height=25)
