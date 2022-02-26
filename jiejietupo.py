#!/usr/bin/env python3
# jiejietupo.py

"""
结界突破界面
主界面功能3、4
"""

import window
import function

from time import sleep
import pyautogui

picpath = 'jiejietupo'
'''图片路径'''

'''
突破界面
tupo_biaoti.png
个人突破
tupo_geren.png
阴阳寮按钮
tupo_yinyangliao.png
攻破图标
tupo_victory.png
失败图标
tupo_fail.png
防守记录（个人突破）
tupo_fangshoujilu.png
突破记录（阴阳寮突破）
tupo_yinyangliao.png
'''


# 图像识别，返回图像的局部相对坐标
def GetCoorInfo_Picture_Tupo(x1, y1, picname: str):
    """图像识别，返回图像的局部相对坐标"""
    filename: str = './/pic//' + picpath + '//' + picname
    if 'xunzhang' in picname:
        try:
            button_location = pyautogui.locateOnScreen(filename, region=(x1 + window.window_left - 25, y1 + window.window_top + 40, 185 + 20, 90 - 20), confidence=0.9)
            # print(button_location)
            # pyautogui.moveTo(x1 + window.window_left - 25, y1 + window.window_top + 20, duration=0.5)
            # pyautogui.moveTo(x1 + window.window_left - 25 + 185 + 20, y1 + window.window_top + 40 + 90 - 20, duration=0.5)
            x, y = function.Coor_Random(button_location[0], button_location[0] + button_location[2], button_location[1], button_location[1] + button_location[3])
        except:
            x = y = 0
    else:
        try:
            button_location = pyautogui.locateOnScreen(filename, region=(x1 + window.window_left, y1 - 40 + window.window_top, 185 + 40, 90), confidence=0.8)
            # print(button_location)
            x, y = function.Coor_Random(button_location[0], button_location[0] + button_location[2], button_location[1], button_location[1] + button_location[3])
        except:
            x = y = 0
    return x, y


# 结界突破战斗
def Tupo_Fight(x0, y0):
    """结界突破战斗"""
    x, y = function.Coor_Random(x0, x0 + 185, y0, y0 + 90)
    pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
    pyautogui.click()
    print(x + window.window_left, y + window.window_top)
    while 1:
        x, y = function.GetCoorInfo_Picture(picpath, 'tupo_jingong.png')
        if x != 0 and y != 0:
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click()
            break


# 创建列表，返回每个结界的勋章数
def List_Num_Xunzhang():
    """创建列表，返回每个结界的勋章数"""
    alist = [0]
    for i in range(1, 10):
        x5, y5 = GetCoorInfo_Picture_Tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_5.png')
        x4, y4 = GetCoorInfo_Picture_Tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_4.png')
        x3, y3 = GetCoorInfo_Picture_Tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_3.png')
        x2, y2 = GetCoorInfo_Picture_Tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_2.png')
        x1, y1 = GetCoorInfo_Picture_Tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_1.png')
        x0, y0 = GetCoorInfo_Picture_Tupo(tupo_geren_x[(i + 2) % 3 + 1], tupo_geren_y[(i + 2) // 3], 'xunzhang_0.png')
        if x5 != 0 and y5 != 0:
            # print(i, '5勋章')
            alist.append(5)
            continue
        if x4 != 0 and y4 != 0:
            # print(i, '4勋章')
            alist.append(4)
            continue
        if x3 != 0 and y3 != 0:
            # print(i, '3勋章')
            alist.append(3)
            continue
        if x2 != 0 and y2 != 0:
            # print(i, '2勋章')
            alist.append(2)
            continue
        if x1 != 0 and y1 != 0:
            # print(i, '1勋章')
            alist.append(1)
            continue
        if x0 != 0 and y0 != 0:
            # print(i, '0勋章')
            alist.append(0)
            continue
        if x0 == 0 and x1 == 0 and x2 == 0 and x4 == 0 and x5 == 0:
            print(i, '已攻破')
            alist.append(-1)
    '''
    for i in range (5, -1, -1):
        if i == 0:
            print(i, '勋章', alist.count(i) - 1, '个')
        else:
            print(i, '勋章', alist.count(i), '个')
    '''
    return alist


'''
pyautogui.moveTo(215+185,175+90+30+90+30+90)
*****(220,180)******(805,175)
*****(805,271)
'''

'''
个人突破相对坐标
宽185
高90
间隔宽115
间隔高30
'''

tupo_geren_x = {
    1: 215,
    2: 515,
    3: 815,
}
tupo_geren_y = {
    1: 175,
    2: 295,
    3: 415
}


# 个人突破主程序
def Run_Tupo_Geren(tupo_n: int = 30):
    """个人突破主程序"""
    sleep(2)
    while 1:
        x, y = function.GetCoorInfo_Picture(picpath, 'tupo_biaoti.png')
        if x != 0 and y != 0:
            print('当前界面为结界突破')
            break
    sleep(2)
    while 1:
        x, y = function.GetCoorInfo_Picture(picpath, 'tupo_fangshoujilu.png')
        if x != 0 and y != 0:
            print('当前界面为个人突破')
            break
        else:
            while 1:
                x, y = function.GetCoorInfo_Picture(picpath, 'tupo_geren.png')
                if x != 0 and y != 0:
                    pyautogui.moveTo(x, y, duration=0.5)
                    pyautogui.click()
                    print(x, y)
                    break
    while tupo_n != 0:
        print('剩余次数：', tupo_n)
        list_xunzhang = List_Num_Xunzhang()
        print(list_xunzhang)
        # 打法 胜3刷新
        tupo_victory = list_xunzhang.count(-1)
        if tupo_victory == 3:
            print('已攻破3次，等待刷新')
            function.SleepRandom(3,6)
            while 1:
                x, y = function.GetCoorInfo_Picture(picpath, 'shuaxin.png')
                if x != 0 and y != 0:
                    pyautogui.moveTo(x, y, duration=0.5)
                    pyautogui.click()
                    break
            sleep(1)
            while 1:
                x, y = function.GetCoorInfo_Picture(picpath, 'queding.png')
                if x != 0 and y != 0:
                    pyautogui.moveTo(x, y, duration=0.5)
                    pyautogui.click()
                    break
        elif tupo_victory < 3:
            print('已攻破', tupo_victory, '个')
            for i in range(5, -1, -1):
                # print('勋章数', i)
                if list_xunzhang.count(i):
                    k = 1
                    for j in range(1, list_xunzhang.count(i) + 1):
                        k = list_xunzhang.index(i, k)
                        print(k, 'need fight')
                        x, y = GetCoorInfo_Picture_Tupo(tupo_geren_x[(k + 2) % 3 + 1], tupo_geren_y[(k + 2) // 3], 'tupo_fail.png')
                        if x != 0 and y != 0:
                            print(k, 'fail')
                            k += 1
                            continue
                        Tupo_Fight(tupo_geren_x[(k + 2) % 3 + 1], tupo_geren_y[(k + 2) // 3])
                        if function.Result() == 1:
                            tupo_n -= 1
                            flag_victory = 1
                        else:
                            flag_victory = 0
                        sleep(1)
                        # 结束界面
                        x, y = function.Finish_Random_Left_Right()
                        pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
                        pyautogui.click()
                        sleep(2)
                        # 3胜奖励
                        if tupo_victory == 2 and flag_victory == 1:
                            sleep(2)
                            while 1:
                                x, y = function.GetCoorInfo_Picture('victory.png')
                                if x != 0 and y != 0:
                                    x, y = function.Finish_Random_Left_Right()
                                    pyautogui.moveTo(x, y, duration=0.5)
                                    pyautogui.click()
                                    print('victory for 3 times')
                                    break
                        sleep(3)
                        break
        elif tupo_victory > 3:
            print('暂不支持大于3个，请自行处理')
            break
        sleep(3)
    print('over')


'''
*****(460,170)*****(645,170)**(760,170)*****(945,170)
*****(460,260)*****(645,260)
****************************
*****(460,300)

'''

'''
阴阳寮突破相对坐标
宽185
高90
间隔宽115
间隔高40
'''

tupo_yinyangliao_x = {
    1: 460,
    2: 760
}
tupo_yinyangliao_y = {
    1: 170,
    2: 300,
    3: 430,
    4: 560
}


# 阴阳寮突破主程序
def Run_Tupo_Yinyangliao():
    """阴阳寮突破主程序"""
    sleep(2)
    while 1:
        x, y = function.GetCoorInfo_Picture(picpath, 'tupo_biaoti.png')
        if x != 0 and y != 0:
            print('当前界面为结界突破')
            break
    sleep(2)
    while 1:
        x, y = function.GetCoorInfo_Picture(picpath, 'tupo_tupojilu.png')
        if x != 0 and y != 0:
            print('当前界面为阴阳寮突破')
            break
        else:
            while 1:
                x, y = function.GetCoorInfo_Picture(picpath, 'tupo_yinyangliao.png')
                if x != 0 and y != 0:
                    pyautogui.moveTo(x, y, duration=0.5)
                    pyautogui.click()
                    print(x, y)
                    break
    tupo_n = 6
    i = 1
    while tupo_n != 0:
        print('剩余次数：', tupo_n)
        x, y = GetCoorInfo_Picture_Tupo(tupo_yinyangliao_x[(i + 1) % 2 + 1], tupo_yinyangliao_y[(i + 1) // 2], 'tupo_fail.png')
        if x == 0 or y == 0:
            print(i, 'need to fight')
            Tupo_Fight(tupo_yinyangliao_x[(i + 1) % 2 + 1], tupo_yinyangliao_y[(i + 1) // 2])
            if function.Result() == 1:
                tupo_n -= 1
            else:
                i += 1
            sleep(1)
            # 结束界面
            x, y = function.Finish_Random_Left_Right()
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
            pyautogui.click()
            print(x + window.window_left, y + window.window_top)
        else:
            print(i, 'fail')
            i += 1
        sleep(3)
    print('over')


if __name__ == '__main__':
    window.GetInfo_Window()
    Run_Tupo_Geren(9)
    # Run_Tupo_Yinyangliao()
