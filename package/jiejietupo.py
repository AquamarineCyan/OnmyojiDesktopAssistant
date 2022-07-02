#!/usr/bin/env python3
# jiejietupo.py
"""
结界突破场景
"""

import math
import time
import pyautogui

from . import window
from .function import Function
from mysignal import global_ms as ms

'''
突破界面
title.png
个人突破
geren.png
阴阳寮按钮
yinyangliao.png
攻破图标
victory.png
失败图标
fail.png
防守记录（个人突破）
fangshoujilu.png
突破记录（阴阳寮突破）
yinyangliao.png
'''


class JieJieTuPo(Function):
    """结界突破"""

    def __init__(self):
        self.picpath = 'jiejietupo'  # 图片路径

    def get_coor_info_picture_tupo(self, x1, y1, pic: str):
        """
        图像识别，返回图像的局部相对坐标

        :param x1: 识别区域左侧横坐标
        :param y1: 识别区域顶部纵坐标
        :param picname: 图像名称
        :return: x, y
        """
        filename: str = fr'.\pic\{self.picpath}\{pic}'
        if 'xunzhang' in pic:
            # 个人突破
            try:
                button_location = pyautogui.locateOnScreen(filename, region=(
                    x1 + window.window_left - 25, y1 + window.window_top + 40, 185 + 20, 90 - 20), confidence=0.9)
                x, y = self.random_coor(button_location[0], button_location[0] + button_location[2],
                                        button_location[1],
                                        button_location[1] + button_location[3])
            except:
                x = y = 0
        else:
            # 阴阳寮突破
            try:
                button_location = pyautogui.locateOnScreen(filename, region=(
                    x1 + window.window_left, y1 - 40 + window.window_top, 185 + 40, 90), confidence=0.8)
                x, y = self.random_coor(button_location[0], button_location[0] + button_location[2],
                                        button_location[1],
                                        button_location[1] + button_location[3])
            except:
                x = y = 0
        return x, y

    def fighting_tupo(self, x0, y0):
        """
        结界突破战斗

        :param x0: 左侧横坐标
        :param y0: 顶部纵坐标
        :return: None
        """
        x, y = self.random_coor(x0, x0 + 185, y0, y0 + 80)
        pyautogui.moveTo(x + window.window_left, y + window.window_top, duration=0.5)
        pyautogui.click()
        while 1:
            x, y = self.get_coor_info_picture(f'{self.picpath}/jingong.png')
            if x != 0 and y != 0:
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                break

    def fighting_fail_again(self):
        # 主动失败
        time.sleep(2)
        while True:
            pyautogui.press('esc')
            if self.judge_scene(f'{self.picpath}/fighting_fail.png'):
                pyautogui.press('enter')
                ms.text_print_update.emit('手动退出')
                break
            time.sleep(0.5)


class JieJieTuPoGeRen(JieJieTuPo):
    """个人突破"""
    '''
    个人突破相对坐标
    宽185
    高90
    间隔宽115
    间隔高30
    '''

    def __init__(self):
        super().__init__()
        self.tupo_geren_x = {
            1: 215,
            2: 515,
            3: 815,
        }
        self.tupo_geren_y = {
            1: 175,
            2: 295,
            3: 415
        }
        self.m = 0  # 当前次数
        self.n = None  # 总次数
        self.list_xunzhang = None  # 勋章列表
        self.tupo_victory = None  # 攻破次数
        self.time_refresh = 0  # 记录刷新时间

    def title(self):
        """场景"""
        flag_title = True  # 场景提示
        while 1:
            if self.judge_scene(f'{self.picpath}/title.png', '[SCENE] 结界突破'):
                while 1:
                    if self.judge_scene(f'{self.picpath}/fangshoujilu.png', '[SCENE] 个人突破'):
                        return True
                    else:
                        time.sleep(1)
                        self.judge_click(f'{self.picpath}/geren.png', dura=0.5)
                        time.sleep(4)
            elif flag_title:
                flag_title = False
                ms.text_print_update.emit('[WARN] 请检查游戏场景')

    def list_num_xunzhang(self):
        """
        创建列表，返回每个结界的勋章数

        :return: 勋章个数列表
        """
        alist = [0]
        for i in range(1, 10):
            x5, y5 = self.get_coor_info_picture_tupo(self.tupo_geren_x[(i + 2) % 3 + 1],
                                                     self.tupo_geren_y[(i + 2) // 3],
                                                     'xunzhang_5.png')
            x4, y4 = self.get_coor_info_picture_tupo(self.tupo_geren_x[(i + 2) % 3 + 1],
                                                     self.tupo_geren_y[(i + 2) // 3],
                                                     'xunzhang_4.png')
            x3, y3 = self.get_coor_info_picture_tupo(self.tupo_geren_x[(i + 2) % 3 + 1],
                                                     self.tupo_geren_y[(i + 2) // 3],
                                                     'xunzhang_3.png')
            x2, y2 = self.get_coor_info_picture_tupo(self.tupo_geren_x[(i + 2) % 3 + 1],
                                                     self.tupo_geren_y[(i + 2) // 3],
                                                     'xunzhang_2.png')
            x1, y1 = self.get_coor_info_picture_tupo(self.tupo_geren_x[(i + 2) % 3 + 1],
                                                     self.tupo_geren_y[(i + 2) // 3],
                                                     'xunzhang_1.png')
            x0, y0 = self.get_coor_info_picture_tupo(self.tupo_geren_x[(i + 2) % 3 + 1],
                                                     self.tupo_geren_y[(i + 2) // 3],
                                                     'xunzhang_0.png')
            if x5 != 0 and y5 != 0:
                alist.append(5)
                continue
            if x4 != 0 and y4 != 0:
                alist.append(4)
                continue
            if x3 != 0 and y3 != 0:
                alist.append(3)
                continue
            if x2 != 0 and y2 != 0:
                alist.append(2)
                continue
            if x1 != 0 and y1 != 0:
                alist.append(1)
                continue
            if x0 != 0 and y0 != 0:
                alist.append(0)
                continue
            if x0 == 0 and x1 == 0 and x2 == 0 and x4 == 0 and x5 == 0:
                # print(i, '已攻破')
                alist.append(-1)
        """
        for i in range (5, -1, -1):
            if i == 0:
                print(i, '勋章', alist.count(i) - 1, '个')
            else:
                print(i, '勋章', alist.count(i), '个')
        """
        list_xunzhang = '勋章数：['
        for i in range(1, 10):
            if i == 1:
                list_xunzhang = list_xunzhang + str(alist[i])
            else:
                list_xunzhang = list_xunzhang + ',' + str(alist[i])
        list_xunzhang = list_xunzhang + ']'
        ms.text_print_update.emit(list_xunzhang)
        return alist

    def fighting(self):
        """战斗"""
        for i in range(5, -1, -1):
            if self.list_xunzhang.count(i):
                k = 1
                for j in range(1, self.list_xunzhang.count(i) + 1):
                    k = self.list_xunzhang.index(i, k)
                    ms.text_print_update.emit(f'{k} 可进攻')
                    x, y = self.get_coor_info_picture_tupo(self.tupo_geren_x[(k + 2) % 3 + 1],
                                                           self.tupo_geren_y[(k + 2) // 3],
                                                           'fail.png')
                    if x != 0 and y != 0:
                        ms.text_print_update.emit(f'{k} 已失败')
                        k += 1
                        continue
                    self.fighting_tupo(self.tupo_geren_x[(k + 2) % 3 + 1], self.tupo_geren_y[(k + 2) // 3])
                    # 待优化，利用时间戳的间隔判断
                    # time.sleep(4)
                    # if self.judge_click('zhunbei.png',click=False):
                    #     self.judge_click('zhunbei.png')
                    if self.result():
                        flag_victory = True
                        self.m += 1
                        ms.text_num_update.emit(f'{self.m}/{self.n}')
                    else:
                        flag_victory = False
                    time.sleep(1)
                    # 结束界面
                    x, y = self.random_finish_left_right()
                    time.sleep(2)
                    # 3胜奖励
                    if self.tupo_victory == 2 and flag_victory:
                        time.sleep(2)
                        while 1:
                            self.judge_click('victory.png')
                            self.random_sleep(1, 2)
                            x, y = self.get_coor_info_picture('victory.png')
                            if x == 0 or y == 0:
                                break
                        ms.text_print_update.emit('成功攻破3次')
                    time.sleep(3)
                    if flag_victory:
                        return

    def refresh(self):
        """刷新"""
        flag_refresh = False  # 刷新提醒
        self.random_sleep(4, 8)  # 强制等待
        while 1:
            # 第一次刷新 或 冷却时间已过
            timenow = time.perf_counter()
            print('time_refresh', self.time_refresh)
            print('timenow', timenow)
            if self.time_refresh == 0 or self.time_refresh + 5 * 60 < timenow:
                ms.text_print_update.emit('刷新中')
                self.random_sleep(3, 6)
                self.judge_click(f'{self.picpath}/shuaxin.png', sleeptime=2)
                self.random_sleep(2, 4)
                self.judge_click(f'{self.picpath}/queding.png', sleeptime=0.5)
                self.time_refresh = timenow
                self.random_sleep(2, 6)
                break
            elif not flag_refresh:
                time_wait = math.ceil(self.time_refresh + 5 * 60 - timenow)
                ms.text_print_update.emit(f'等待刷新冷却，约{time_wait}秒')
                flag_refresh = True
                time.sleep(time_wait)

    def run(self, n: int):
        time.sleep(2)
        self.n = n
        time_progarm = self.TimeProgram()  # 程序计时
        time_progarm.start()
        if self.title():
            ms.text_num_update.emit(f'0/{self.n}')
            self.random_sleep(1, 3)
            while self.m < self.n:
                self.random_sleep(2, 4)
                self.list_xunzhang = self.list_num_xunzhang()
                # 胜利次数
                self.tupo_victory = self.list_xunzhang.count(-1)
                # 刷新
                if self.tupo_victory == 3:
                    self.refresh()
                # 挑战
                elif self.tupo_victory < 3:
                    ms.text_print_update.emit(f'已攻破{self.tupo_victory}个')
                    self.fighting()
                elif self.tupo_victory > 3:
                    ms.text_print_update.emit('[WARN] 暂不支持大于3个，请自行处理')
                    break
                time.sleep(3)
        text = f"已完成 个人突破{self.m}次"
        time_progarm.end()
        text = text + " " + time_progarm.print()
        ms.text_print_update.emit(text)
        # 启用按钮
        ms.is_fighting_update.emit(False)


class JieJieTuPoYinYangLiao(JieJieTuPo):
    """阴阳寮突破"""
    '''
    阴阳寮突破相对坐标
    宽185
    高90
    间隔宽115
    间隔高40
    '''

    def __init__(self):
        super().__init__()
        self.tupo_yinyangliao_x = {
            1: 460,
            2: 760
        }
        self.tupo_yinyangliao_y = {
            1: 170,
            2: 300,
            3: 430,
            4: 560
        }
        self.m = 0  # 当前次数
        self.n = None  # 总次数

    def title(self):
        """场景"""
        flag_title = True  # 场景提示
        while 1:
            if self.judge_scene(f'{self.picpath}/title.png', '[SCENE] 结界突破'):
                while 1:
                    if self.judge_scene(f'{self.picpath}/tupojilu.png', '[SCENE] 阴阳寮突破'):
                        return True
                    else:
                        time.sleep(1)
                        self.judge_click(f'{self.picpath}/yinyangliao.png', dura=0.5)
                        time.sleep(4)
            elif flag_title:
                flag_title = False
                ms.text_print_update.emit('[WARN] 请检查游戏场景')

    def jibaicishu(self):
        """剩余次数判断"""
        # 无法生效，待废除，或使用OpenCv
        if self.title():
            while 1:
                try:
                    button_location = pyautogui.locateOnScreen(f'./pic/{self.picpath}/jibaicishu.png', region=(
                        window.window_left, window.window_top, window.window_width, window.window_height))
                    print('find')
                    return False
                except:
                    print('not found')
                    print('仍有剩余次数')
                    return True

    def fighting(self):
        """战斗"""
        i = 1
        while 1:
            x, y = self.get_coor_info_picture_tupo(self.tupo_yinyangliao_x[(i + 1) % 2 + 1],
                                                   self.tupo_yinyangliao_y[(i + 1) // 2],
                                                   'fail.png')
            if x == 0 or y == 0:
                ms.text_print_update.emit(f'{i} 可进攻')
                self.fighting_tupo(self.tupo_yinyangliao_x[(i + 1) % 2 + 1], self.tupo_yinyangliao_y[(i + 1) // 2])
                if self.result():
                    # 胜利
                    flag = 1
                else:
                    # 失败
                    flag = 0
                time.sleep(2)
                # 结束界面
                x, y = self.random_finish_left_right()
                return flag
            else:
                ms.text_print_update.emit(f'{i} 已失败')
                i += 1
                if i == 8:
                    # 单页上限8个
                    ms.text_print_update.emit('当前页全部失败')
                    flag = -1
                    return flag

    def run(self, n: int):
        time.sleep(2)
        self.n = n
        time_progarm = self.TimeProgram()  # 程序计时
        time_progarm.start()
        if self.title():
            ms.text_num_update.emit(f'0/{self.n}')
            self.random_sleep(1, 3)
            while self.m < self.n:
                time.sleep(1)
                flag = JieJieTuPoYinYangLiao.fighting(self)
                if flag:
                    self.m += 1
                    ms.text_num_update.emit(f'{self.m}/{self.n}')
                elif flag == -1:
                    break
                time.sleep(3)
        text = f"已完成 阴阳寮突破{self.m}次"
        time_progarm.end()
        text = text + " " + time_progarm.print()
        ms.text_print_update.emit(text)
        # 启用按钮
        ms.is_fighting_update.emit(False)
