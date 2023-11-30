#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coordinate.py
"""坐标"""

import pyautogui
from .window import window


class Coor:
    """坐标"""

    def __init__(self, x: int | float = 0, y: int | float = 0) -> None:
        """一般坐标

        也可使用 `AbsoluteCoor()` `RelativeCoor()` 做精确区分

        参数:
            x (int | float): 横轴坐标
            y (int | float): 纵轴坐标
        """
        self.x: int | float = x
        self.y: int | float = y
        self.coor: tuple[int | float, int | float] = self._coor_tuple_format()
        self.is_zero: bool = self._is_zero_func()
        """全0，未找到图像"""
        self.is_effective: bool = self._is_effective_func()
        """坐标有效"""

    def _coor_tuple_format(self) -> tuple[int | float, int | float]:
        return (self.x, self.y)

    def _is_zero_func(self) -> bool:
        if self.x == 0 or self.y == 0:
            return True
        else:
            return False

    def _is_effective_func(self) -> bool:
        if self.x != 0 and self.y != 0:
            return True
        else:
            return False


class AbsoluteCoor(Coor):
    """绝对坐标

    对应屏幕，适用于鼠标点击等事件的传参
    """

    def __init__(self, x: int | float = 0, y: int | float = 0) -> None:
        super().__init__(x, y)

    def abs_to_rela(self):
        x = self.x - window.window_left
        y = self.y - window.window_top
        return RelativeCoor(x, y)


class RelativeCoor(Coor):
    """相对坐标

    对应游戏窗口内，一般包括windows窗口外框
    """

    def __init__(self, x: int | float = 0, y: int | float = 0) -> None:
        super().__init__(x, y)

    def rela_to_abs(self):
        x = self.x + window.window_left
        y = self.y + window.window_top
        if pyautogui.onScreen(x, y):
            return AbsoluteCoor(x, y)


class RectangleCoor:
    """矩形坐标"""

    def __init__(self,x1,x2,y1,y2) -> None:
        self.x1 = x1
        self.x2 = x2
        self.y1=y1
        self.y2=y2

    def get_rela_center_coor(self):
        """返回矩形的相对中心坐标"""
        x = (self.x1+self.x2)/2
        y = (self.y1+self.y2)/2
        return RelativeCoor(x,y)
