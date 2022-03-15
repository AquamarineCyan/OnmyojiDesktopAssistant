#!/usr/bin/env python3
# main_old.py
"""
main主程序
"""

from package import *

import sys
import pathlib
from colorama import init, Fore, Back, Style

version: str = '1.5'
'''版本号'''
num_choice: int = 0
'''功能选择'''

def Init():
    """初始化"""
    print('本项目GitHub地址：https://github.com/AquamarineCyan/Onmyoji_Python')
    print('version=' + str(version) + '\n')
    print(Fore.RED + '仅供内部测试使用，请勿外传，本程序所产生的一切后果自负')
    print(Fore.RED + '请确认您是使用管理员权限打开本程序，否则部分功能会失效')
    print(Fore.RED + '使用过程中，请不要移动游戏窗口，会导致点击位置错误')
    print(Fore.RED + '如需中断程序，请将鼠标置于屏幕四角，这将触发安全措施')
    print('请尽量遵守程序选择，如有错误请联系开发者\n')
    window.GetInfo_Window()
    fpath = pathlib.Path.cwd()
    filepath = fpath / 'pic'
    if not filepath.exists():
        print(Fore.RED + '图片资源不存在')
        print('键入回车键退出程序')
        input('Input Enter Key')
        sys.exit()


def Function_List():
    """功能列表"""
    function_list = {
        -1: '更新日志',
        0: '退出程序',
        1: '组队御魂副本',
        2: '普通召唤',
        3: '寮突破（默认6次）',
        4: '个人突破（默认胜3刷新）',
        5: '百鬼夜行',
        6: '道馆突破',
        7: '御灵',
        8: '绘卷查分'
    }
    print('本程序目前实现的功能如下：')
    for key, value in function_list.items():
        print(str(key) + '.' + value)


def Choice():
    """功能选择"""
    while 1:
        # init(wrap=True)
        choice = 0
        print(Fore.RED + '请确认游戏窗口前置并能被鼠标点击')
        print(Fore.RED + '请确认游戏场景为所选功能场景（部分功能支持等待识别）')
        Function_List()
        while 1:
            print(Fore.GREEN + '回复数字选择功能：', end='')
            m = input()
            print('\n')
            if m.isdigit() or m == '-1':
                choice = int(m)
                break
            else:
                print(Fore.RED + '输入非数字，请重试')
        if choice == -1:
            # 更新日志
            print('更新日志如下：')
            update.update_record()
        elif choice == 0:
            # 退出程序
            sys.exit()
        elif choice == 1:
            # 组队御魂副本
            n = 0
            while n <= 0:
                print('目前可能仅适配乘客端，司机端请手动开始')
                n = int(input('请输入御魂副本的次数：'))
                m = input('是否为司机（默认否），回复“0”为“否”，回复“1”为“是”：')
                if m == '':
                    flag_driver = False
                    flag_passengers = 2
                elif m.isdigit():
                    if m == 0:
                        flag_driver = False
                    else:
                        flag_driver = True
                    s = input('组队人数（默认2人），回复“2”为“2人”，回复“3”为“3人”：')
                    if s == '':
                        flag_passengers = 2
                    elif s.isdigit():
                        flag_passengers = int(s)
                print('总计{}次'.format(str(n)))
            yuhun.Run_Yuhun(n, flag_driver, flag_passengers)
        elif choice == 2:
            # 普通召唤
            n = 0
            while n <= 0:
                n = int(input('请输入普通召唤十连的次数（请确保您的余票足够）：'))
            zhaohuan.run_zhaohuan(n)
        elif choice == 3:
            # 寮突破（默认6次）
            print('待开发：滚轮翻页')
            print('\n')
            n = 0
            while n <= 0:
                strn = input('请输入阴阳寮突破的次数（默认6次）：')
                if strn == '':
                    n = 6
                else:
                    n = int(strn)
            jiejietupo.Run_Tupo_Yinyangliao(n)
        elif choice == 4:
            # 个人突破（默认胜3刷新）
            n = 0
            while n <= 0:
                n = int(input('请输入剩余的结界突破券数量：'))
                jiejietupo.run_tupo_geren(n)
        elif choice == 5:
            # 百鬼夜行
            n = 0
            while n <= 0:
                n = int(input('请输入百鬼夜行券数量：'))
                baiguiyexing.Run_BaiGuiYeXing(n)
        elif choice == 6:
            # 道馆突破
            print(Fore.GREEN + '目前仅支持正在进行中的道馆突破，无法实现跳转道馆场景')
            print('待开发：冷却时间、观战助威')
            daoguantupo.run_daoguantupo()
        elif choice == 7:
            # 御灵
            n = 0
            while n <= 0:
                n = int(input('请输入御灵境之钥数量：'))
                yuling.run_yuling(n)
        elif choice == 8:
            # 绘卷查分
            huijuan.run_huijuan()
        else:
            print('待开发：全局跳转')


if __name__ == '__main__':
    Init()
    Choice()