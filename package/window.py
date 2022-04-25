#!/usr/bin/env python3
# window.py
"""
窗口信息
"""

import win32gui

from mysignal import global_ms as ms

# 窗口大小(官方1136*640)
absolute_window_width = 1154
'''窗口绝对宽度'''
absolute_window_height = 687
'''窗口绝对高度'''
# 窗口坐标
window_left: int = 0
'''窗口横坐标'''
window_top: int = 0
'''窗口纵坐标'''
window_width: int = 0
'''窗口宽度'''
window_height: int = 0
'''窗口高度'''


def getInfo_Window():
    """
    获取窗口信息，打印输出
    """
    global window_left
    global window_top
    global window_width
    global window_height
    try:
        # 获取窗口句柄
        handle = win32gui.FindWindow('Win32Window', '阴阳师-网易游戏')
        # print('%x' % handle)
        # 返回窗口信息（x,y坐标，还有宽度，高度）
        handle_coor = win32gui.GetWindowRect(handle)
    except:
        handle_coor = (0, 0, 0, 0)
    else:
        # 返回数据类型
        window_left = handle_coor[0] + 9
        window_top = handle_coor[1]
        window_width = handle_coor[2]
        window_height = handle_coor[3]
        handle_infodict = {
            0: '横坐标',
            1: '纵坐标',
            2: '宽度',
            3: '高度'
        }
        s = ''
        for i in range(4):
            if i == 0:
                s = s + f'{handle_infodict[i]}:{handle_coor[i] + 9}\n'
            else:
                s = s + f'{handle_infodict[i]}:{handle_coor[i]}\n'
        ms.text_wininfo_update.emit(s)
    return handle_coor
