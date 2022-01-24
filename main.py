#!/usr/bin/env python3
# Onmyoji_python.py

import window
import yuhun
import zhaohuan

import os
import time
import win32api
import win32con
import win32gui
import pyautogui
import random

version = 1.1
# 获取当前目录的父目录
fpath = os.getcwd()
num_choice : int


# 初始化
def Init():
    print('Onmyoji_Python.py')
    print('version=' + str(version) + '\n')
    print('#################################################')
    print('仅供内部测试使用，请勿外传，本程序所产生的一切后果自负')
    print('#################################################')
    print('请确认您是使用管理员权限打开本程序，否则部分功能会失效')
    print('请严格遵守程序选择，如有错误请联系开发者')
    print('使用过程中，请不要移动游戏窗口，会导致点击位置错误')
    window.GetInfo_Window()
    print('\n')
    print('本程序目前实现的功能如下：')
    print('1.普通召唤')
    print('2.组队御魂副本')
    num_choice = int(input('回复数字选择功能：'))
    print('\n')
    if(num_choice == 1):
        print('请确认您的游戏窗口前置并能被鼠标点击')
        print('请确认您的游戏界面为召唤界面')
        print('\n')
        while (zhaohuan.zhaohuan_n < 1):
            zhaohuan.zhaohuan_n = int(input('请输入普通召唤十连的次数（请确保您的余票足够）：'))
        zhaohuan.Run_Zhaohuan(zhaohuan.zhaohuan_n)
    elif(num_choice == 2):
        print('请确认您的游戏窗口前置并能被鼠标点击')
        print('请确认您的游戏界面为御魂副本组队界面')
        print('\n')
        while(yuhun.yuhun_n < 1):
            yuhun.yuhun_n = int(input('请输入御魂副本的次数：'))
            yuhun.yuhun_time = int(input('请输入您的阵容时间（单位秒）：'))
            yuhun.flag_driver = int(input('是否为司机，回复“0”为“否”，回复“1”为“是”：'))
        yuhun.Run_Yuhun(yuhun.yuhun_n, yuhun.yuhun_time, yuhun.flag_driver)



if __name__ == '__main__':
    Init()
    print('感谢您的使用')
    input('Input Enter Key')
