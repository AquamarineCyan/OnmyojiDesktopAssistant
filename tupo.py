#!/usr/bin/env python3
# tupo.py

'''
结界突破界面
仅支持寮突破
主界面功能3
'''


import function


from time import sleep
import pyautogui


import window

'''
突破界面
tupo_biaoti.png
'''

'''
*****(460,170)*****(645,170)**(760,170)*****(945,170)
*****(460,260)*****(645,260)
****************************
*****(460,300)

'''

# 相对坐标
x1 = 345 + 115 * 1 + 185 * 0
x2 = 345 + 115 * 1 + 185 * 1
x3 = 345 + 115 * 2 + 185 * 1
x4 = 345 + 115 * 2 + 185 * 2
y1 = 130 + 40 * 1 + 90 * 0
y2 = 130 + 40 * 1 + 90 * 1
y3 = 130 + 40 * 2 + 90 * 1
y4 = 130 + 40 * 2 + 90 * 2
y5 = 130 + 40 * 3 + 90 * 2
y6 = 130 + 40 * 3 + 90 * 3
y7 = 130 + 40 * 4 + 90 * 3
y8 = 130 + 40 * 4 + 90 * 4
tupo_x = {
    1 : 460,
    2 : 760
}
tupo_y = {
    1 : 170,
    2 : 300,
    3 : 430,
    4 : 560
}


# 图像识别
def GetCoorInfo_Picture_Tupo(x1, y1):
    filename : str = './/pic//tupo_fail.png'
    try:
        button_location = pyautogui.locateOnScreen(filename, region = (x1 + window.window_left, y1 - 40 + window.window_top, 185 + 40, 90), confidence = 0.8)
        # print(button_location)
        x, y = function.Coor_Random(button_location[0], button_location[0] + button_location[2], button_location[1], button_location[1] + button_location[3])
    except:
        x = y = 0
    return x, y


def Run_Tupo():
    while(1):
        x, y = function.GetCoorInfo_Picture('tupo_biaoti.png')
        if(x != 0 and y != 0):
            print('当前界面为结界突破')
            break
    tupo_n = 6
    i = 1
    while(tupo_n != 0):
        print('剩余次数：', tupo_n)
        x, y = GetCoorInfo_Picture_Tupo(tupo_x[(i + 1) % 2 + 1], tupo_y[(i + 1) // 2])
        if (x == 0 or y == 0):
            print(i, 'need to fight')
            x, y = function.Coor_Random(tupo_x[(i + 1) % 2 + 1], tupo_x[(i + 1) % 2 + 1] + 185, tupo_y[(i + 1) // 2], tupo_y[(i + 1) // 2] + 90)
            pyautogui.moveTo(x, y, duration = 0.5)
            pyautogui.click()
            while(1):
                x, y = function.GetCoorInfo_Picture('tupo_jingong.png')
                if (x != 0 and y != 0):
                    pyautogui.moveTo(x, y, duration = 0.5)
                    pyautogui.click()
                    break
            if(function.Result()):
                tupo_n -= 1
            else:
                i += 1
            sleep(1)
            # 结束界面
            if (tupo_n % 2 == 0):
                strf = 'left'
            else:
                strf = 'right'
            x, y = function.Finish_Random_Left_Right(strf)
            pyautogui.moveTo(x + window.window_left, y + window.window_top, duration = 0.5)
            pyautogui.click()
            print(x + window.window_left, y + window.window_top)
        else:
            print(i, 'fail')
            i += 1
        sleep(3)
    print('end')

