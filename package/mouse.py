#!/usr/bin/env python3
# window.py
"""
鼠标信息
"""

import time
import pyautogui

mouse_x: int
mouse_y: int


def GetInfo_Mouse():
    """获取鼠标当前位置坐标"""
    global mouse_x
    global mouse_y
    mouse_x, mouse_y = pyautogui.position()
    print(mouse_x, mouse_y)


if __name__ == '__main__':
    time.sleep(2)
    GetInfo_Mouse()
