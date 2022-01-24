#!/usr/bin/env python3
# window.py
'''
鼠标信息
'''
from time import sleep
import pyautogui

# 获取鼠标当前位置坐标
def GetInfo_Mouse():
    global mouse_x
    global mouse_y
    mouse_x, mouse_y = pyautogui.position()
    print(mouse_x, mouse_y)
    return mouse_x, mouse_y

'''
if __name__ == '__main__':
    print('wait for 2s')
    sleep(2)
    GetInfo_Mouse()
'''