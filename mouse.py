#!/usr/bin/env python3
# window.py
'''
鼠标信息
'''

import pyautogui

mouse_x : int
mouse_y : int

# 获取鼠标当前位置坐标
def GetInfo_Mouse():
    global mouse_x
    global mouse_y
    mouse_x, mouse_y = pyautogui.position()
    print(mouse_x, mouse_y)
