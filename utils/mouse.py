#!/usr/bin/env python3
# mouse.py
"""
鼠标信息
"""

import pyautogui

# https://pyautogui.readthedocs.io/en/latest/mouse.html#the-screen-and-mouse-position

print('Press Ctrl-C to quit.')
try:
    while True:
        x, y = pyautogui.position()
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        print(positionStr, end='')
        print('\b' * len(positionStr), end='', flush=True)
except KeyboardInterrupt:
    print('\n')
