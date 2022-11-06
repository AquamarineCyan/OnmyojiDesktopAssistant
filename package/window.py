#!/usr/bin/env python3
# window.py
"""
窗口信息
"""

import win32gui
import win32con

from utils.mysignal import global_ms as ms
from .log import log

# 窗口大小(官方1136*640)
# 窗口+外框(1154*687)
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
handle = None
"""窗口句柄"""
handle_coor: tuple[int, int, int, int] = (0, 0, 0, 0)
"""窗口坐标 x1,y1,x2,y2"""


def getInfo_Window():
    """
    获取窗口信息，打印输出
    """
    global window_left
    global window_top
    global window_width
    global window_height
    global handle
    global handle_coor
    try:
        # 获取窗口句柄
        handle = win32gui.FindWindow('Win32Window', '阴阳师-网易游戏')
        # print('%x' % handle)
        # 返回窗口信息（x1,y1,x2,y2）
        handle_coor = win32gui.GetWindowRect(handle)
        print('handle_coor:', handle_coor)

        # 修正
        # handle_coor[0] = handle_coor[0] + 9
        # handle_coor[2] = handle_coor[2] - handle_coor[0]
        # handle_coor[3] = handle_coor[3] - handle_coor[1]
    except:
        handle_coor = (0, 0, 0, 0)
    else:
        # 返回数据类型
        window_left = handle_coor[0] + 9
        window_top = handle_coor[1]
        window_width = handle_coor[2]
        window_height = handle_coor[3]
        # window_width = handle_coor[2] - handle_coor[0] - 18
        # window_height = handle_coor[3] - handle_coor[1] - 47
        handle_infodict = {
            0: '横坐标',
            1: '纵坐标',
            2: '宽度',
            3: '高度'
        }
        s = ''
        # 显示修正，对主体判断无影响
        s = s + f'{handle_infodict[0]}:{handle_coor[0] + 9}\n'
        s = s + f'{handle_infodict[1]}:{handle_coor[1]}\n'
        s = s + f'{handle_infodict[2]}:{handle_coor[2] - handle_coor[0] - 18}\n'
        s = s + f'{handle_infodict[3]}:{handle_coor[3] - handle_coor[1] - 47}\n'
        """for i in range(4):
            if i == 0:
                s = s + f'{handle_infodict[i]}:{handle_coor[i]}\n'
            else:
                s = s + f'{handle_infodict[i]}:{handle_coor[i]}\n'"""
        s = s + '横纵坐标为窗体区域\n宽高为游戏本体区域'
        ms.text_wininfo_update.emit(s)
    return handle_coor


def force_zoom():
    """
    强制缩放

    :return:None
    """
    global handle
    global handle_coor
    if handle is not None and handle_coor[0] != 0 and handle_coor[1] != 0:
        # 强制缩放 1154*687
        win32gui.SetWindowPos(handle, win32con.HWND_TOP, handle_coor[0], handle_coor[1], 1154, 687,
                              win32con.SWP_SHOWWINDOW)
        handle_coor = win32gui.GetWindowRect(handle)
        log.log_write(f"handle_coor_new:{handle_coor}")
    else:
        log.log_write("get handle_coor error")
