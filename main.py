#!/usr/bin/env python3
# Onmyoji_python.py

"""
main主程序
"""

import sys
import update
import window
import yuhun
import zhaohuan
import jiejietupo

version = 1.4
'''版本号'''
num_choice: int = 0
'''功能选择'''


# 初始化
def Init():
    """初始化"""
    print('Onmyoji_Python.py')
    print('本项目GitHub地址：https://github.com/AquamarineCyan/Onmyoji_Python')
    print('version=' + str(version) + '\n')
    print('#################################################')
    print('仅供内部测试使用，请勿外传，本程序所产生的一切后果自负')
    print('#################################################')
    print('\n')
    print('请确认您是使用管理员权限打开本程序，否则部分功能会失效')
    print('请严格遵守程序选择，如有错误请联系开发者')
    print('使用过程中，请不要移动游戏窗口，会导致点击位置错误')
    window.GetInfo_Window()
    print('\n')


# 功能列表
def Function_List():
    """功能列表"""
    function_list = {
        -1: '更新日志',
        0: '退出程序',
        1: '组队御魂副本',
        2: '普通召唤',
        3: '寮突破（默认6次）',
        4: '个人突破（默认胜3刷新）'
    }
    print('本程序目前实现的功能如下：')
    for key, value in function_list.items():
        print(str(key) + '.' + value)
    print('\n')


# 功能选择
def Choice():
    """功能选择"""
    while 1:
        Function_List()
        num_choice = int(input('回复数字选择功能：'))
        print('\n')
        if num_choice == -1:
            # 更新日志
            print('更新日志如下：')
            update.UpdateRecord()
        elif num_choice == 0:
            # 退出程序
            sys.exit()
        elif num_choice == 1:
            # 组队御魂副本
            print('请确认您的游戏窗口前置并能被鼠标点击')
            print('请确认您的游戏界面为御魂副本组队界面')
            print('\n')
            n = 0
            while n <= 0:
                print('目前仅适配乘客端，司机端请手动开始')
                n = int(input('请输入御魂副本的次数：'))
                flag_driver = input('是否为司机（默认否），回复“0”为“否”，回复“1”为“是”：')
                if flag_driver == '\n':
                    yuhun.flag_driver = 0
                    flag_passengers = 2
                elif flag_driver.isdigit():
                    yuhun.flag_driver = int(flag_driver)
                    flag_passengers = input('组队人数（默认2人），回复“2”为“2人”，回复“3”为“3人”：')
                    if flag_passengers == '\n':
                        flag_passengers = 2
                    elif flag_passengers.isdigit():
                        yuhun.flag_passengers = int(flag_passengers)
                # print('总计' + str(n) + '次')
                print('总计{}次'.format(str(n)))
            yuhun.Run_Yuhun(n, yuhun.flag_driver, yuhun.flag_passengers)
        elif num_choice == 2:
            # 普通召唤
            print('请确认您的游戏窗口前置并能被鼠标点击')
            print('请确认您的游戏界面为召唤界面')
            print('\n')
            n = 0
            while n <= 0:
                n = int(input('请输入普通召唤十连的次数（请确保您的余票足够）：'))
            zhaohuan.Run_Zhaohuan(n)
        elif num_choice == 3:
            # 寮突破（默认6次）
            print('请确认您的游戏窗口前置并能被鼠标点击')
            print('请确认您的游戏界面为寮突破界面')
            print('剩余功能待开发：滚轮翻页')
            print('\n')
            jiejietupo.Run_Tupo_Yinyangliao()
        elif num_choice == 4:
            # 个人突破（默认胜3刷新）
            print('请确认您的游戏窗口前置并能被鼠标点击')
            print('请确认您的游戏界面为结界突破界面')
            print('\n')
            n = 0
            while n <= 0:
                n = int(input('请输入剩余的结界突破券数量：'))
                jiejietupo.Run_Tupo_Geren(n)
        else:
            print('待开发')


if __name__ == '__main__':
    Init()
    Choice()
    # print('感谢您的使用')
    # input('Input Enter Key')
