#!/usr/bin/env python3
# window.py
"""
窗口信息
"""
import sys
import win32gui
from colorama import init, Fore, Back, Style

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
init(autoreset=True)

def GetInfo_Window():
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
        handle_info = win32gui.GetWindowRect(handle)
    except:
        print(Fore.RED + '请登录游戏并重新启动本程序')
        print(Fore.GREEN + '键入回车键退出程序')
        input('Input Enter Key')
        sys.exit()
    else:
        # 返回数据类型
        window_left = handle_info[0] + 9
        window_top = handle_info[1]
        window_width = handle_info[2]
        window_height = handle_info[3]
        handle_infodict = {
            0: '窗口横坐标',
            1: '窗口纵坐标',
            2: '窗口宽度',
            3: '窗口高度'
        }
        for i in range(4):
            if i == 0:
                print(handle_infodict[i] + ':' + str(handle_info[i] + 9))
            else:
                print(handle_infodict[i] + ':' + str(handle_info[i]))
