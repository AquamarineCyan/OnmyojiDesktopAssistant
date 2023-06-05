#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coordinate.py
"""坐标"""


class Coor:
    """坐标"""

    def __init__(self, x: int | float = 0, y: int | float = 0):
        self.x: int | float = x
        self.y: int | float = y
        self.coor: tuple[int | float, int | float] = self._coor_tuple_format()
        self.is_zero: bool = self._is_zero_func()
        self.is_effective: bool = self._is_effective_func()

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
