#!/usr/bin/env python3
# window.py
'''
窗口信息
'''

import win32gui

# 窗口坐标
window_x : int
window_y : int
# 窗口大小(官方1136*640)
absolute_window_width = 1154
absolute_window_height = 687
window_width : int
window_height : int

# 获取窗口信息
def GetInfo_Window():
    global window_x
    global window_y
    global window_width
    global window_height
    # 获取窗口句柄
    handle = win32gui.FindWindow('Win32Window', '阴阳师-网易游戏')
    # print('%x' % handle)
    # 返回窗口信息（x,y坐标，还有宽度，高度）
    handle_info = win32gui.GetWindowRect(handle)
    # 返回数据类型
    # print(type(handle_info))
    handle_infodict = {
        1: '窗体x坐标',
        2: '窗体y坐标',
        3: '窗体宽度',
        4: '窗体高度'
    }
    for i in range(4):
        if i == 0:
            window_x = handle_info[i]
            print(handle_infodict[i + 1] + ':' + str(window_x))
        elif i == 1:
            window_y = handle_info[i]
            print(handle_infodict[i + 1] + ':' + str(window_y))
        elif i == 2:
            window_width = (handle_info[i] - handle_info[i - 2])
            print(handle_infodict[i + 1] + ':' + str(window_width))
        elif i == 3:
            window_height = (handle_info[i] - handle_info[i - 2])
            print(handle_infodict[i + 1] + ':' + str(window_height))


'''
if __name__ == "__main__":
    GetInfo_Window()
'''