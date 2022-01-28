#!/usr/bin/env python3
# Onmyoji_python.py


import window
import yuhun
import zhaohuan
import tupo


version = 1.3

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
    print('1.组队御魂副本')
    print('2.普通召唤')
    print('3.寮突破（默认6次）')
    num_choice = int(input('回复数字选择功能：'))
    print('\n')
    if(num_choice == 1):
        # 组队御魂副本
        print('请确认您的游戏窗口前置并能被鼠标点击')
        print('请确认您的游戏界面为御魂副本组队界面')
        print('\n')
        while (yuhun.yuhun_n < 1):
            print('目前仅适配乘客端，司机端请手动开始')
            yuhun.yuhun_n = int(input('请输入御魂副本的次数：'))
            flag_driver = input('是否为司机（默认否），回复“0”为“否”，回复“1”为“是”：')
            if (flag_driver == '\n'):
                yuhun.flag_driver = 0
            elif (flag_driver.isdigit()):
                yuhun.flag_driver = int(flag_driver)
            print('总计' + str(yuhun.yuhun_n) + '次')
        yuhun.Run_Yuhun(yuhun.yuhun_n, yuhun.flag_driver)
    elif(num_choice == 2):
        # 普通召唤
        print('请确认您的游戏窗口前置并能被鼠标点击')
        print('请确认您的游戏界面为召唤界面')
        print('\n')
        while (zhaohuan.zhaohuan_n < 1):
            zhaohuan.zhaohuan_n = int(input('请输入普通召唤十连的次数（请确保您的余票足够）：'))
        zhaohuan.Run_Zhaohuan(zhaohuan.zhaohuan_n)
    elif(num_choice == 3):
        # 结界突破
        print('请确认您的游戏窗口前置并能被鼠标点击')
        print('请确认您的游戏界面为寮突破界面')
        print('默认6个')
        print('剩余功能待开发：切换个人突破与寮突破界面、滚轮翻页')
        print('\n')
        tupo.Run_Tupo()
    else:
        print('待开发')




if __name__ == '__main__':
    Init()
    print('感谢您的使用')
    input('Input Enter Key')
