#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# jiejietupo.py
"""结界突破"""

import math
import pyautogui
import time

from pathlib import Path

from utils.config import config
from utils.decorator import *
from utils.function import function
from utils.log import log
from utils.window import window


class JieJieTuPo:
    """结界突破"""

    def __init__(self):
        self.scene_name: str = "结界突破"
        self.resource_path: str = "jiejietupo"  # 路径
        self.resource_list: list = [
            "fail",  # 失败
            "fangshoujilu",  # 防守记录-个人突破
            "fighting_fail",  # TODO 战斗失败
            "geren",  # 个人突破
            "jingong",  # 进攻
            "queding",
            "shuaxin",  # 刷新-个人突破
            "title",  # 突破界面
            "tupojilu",  # 突破记录-阴阳寮突破
            "victory",  # 攻破
            "xunzhang_0",  # 勋章数0
            "xunzhang_1",  # 勋章数1
            "xunzhang_2",  # 勋章数2
            "xunzhang_3",  # 勋章数3
            "xunzhang_4",  # 勋章数4
            "xunzhang_5",  # 勋章数5
            "yinyangliao"  # 阴阳寮突破
        ]

    def get_coor_info_picture_tupo(self, x1: int, y1: int, file: str) -> tuple[int, int]:
        """图像识别，返回图像的局部相对坐标

        参数:
            x1 (int): 识别区域左侧横坐标
            y1 (int): 识别区域顶部纵坐标
            file (str): 图像名称

        返回:
            tuple[int, int]: (x, y)
        """
        filename = config.resource_path / self.resource_path / file
        log.info(f"looking for file: {filename}")
        if isinstance(filename, Path):
            filename = filename.__str__()
        if "xunzhang" in file:
            # 个人突破
            try:
                button_location = pyautogui.locateOnScreen(
                    filename,
                    region=(
                        x1 + window.window_left - 25,
                        y1 + window.window_top + 40,
                        185 + 20,
                        90 - 20
                    ),
                    confidence=0.9
                )
                x, y = function.random_coor(
                    button_location[0],
                    button_location[0] + button_location[2],
                    button_location[1],
                    button_location[1] + button_location[3]
                )
            except:
                x = y = 0
        else:
            # 阴阳寮突破
            try:
                button_location = pyautogui.locateOnScreen(
                    filename,
                    region=(
                        x1 + window.window_left,
                        y1 - 40 + window.window_top,
                        185 + 40,
                        90
                    ),
                    confidence=0.8
                )
                x, y = function.random_coor(
                    button_location[0],
                    button_location[0] + button_location[2],
                    button_location[1],
                    button_location[1] + button_location[3]
                )
            except:
                x = y = 0
        return x, y

    def fighting_tupo(self, x0: int, y0: int) -> None:
        """结界突破战斗        

        参数:
            x0 (int): 左侧横坐标
            y0 (int): 顶部纵坐标
        """
        x, y = function.random_coor(x0, x0 + 185, y0, y0 + 80)
        pyautogui.moveTo(
            x + window.window_left,
            y + window.window_top,
            duration=0.5
        )
        pyautogui.click()
        while True:
            x, y = function.get_coor_info_picture(f"{self.resource_path}/jingong.png")
            if x != 0 and y != 0:
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                break

    def fighting_fail_again(self):
        # TODO 主动失败
        function.random_sleep(1, 2)
        while True:
            pyautogui.press("esc")
            if function.judge_scene(f"{self.resource_path}/fighting_fail.png"):
                pyautogui.press("enter")
                log.ui("手动退出")
                break
            function.random_sleep(0, 1)


class JieJieTuPoGeRen(JieJieTuPo):
    """个人突破
    相对坐标
    宽185
    高90
    间隔宽115
    间隔高30
    """
    
    @log_function_call
    def __init__(self, n: int = 0) -> None:
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
        self.n: int = 0  # 当前次数
        self.max: int = n  # 总次数
        self.list_xunzhang: list = None  # 勋章列表
        self.tupo_victory: int = None  # 攻破次数
        self.time_refresh: int = 0  # 记录刷新时间

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if function.judge_scene(f"{self.resource_path}/title.png", "结界突破"):
                while True:
                    if function.judge_scene(f"{self.resource_path}/fangshoujilu.png", "个人突破"):
                        return True
                    else:
                        function.random_sleep(0, 1)
                        function.judge_click(
                            f"{self.resource_path}/geren.png", dura=0.5)
                        function.random_sleep(3, 4)
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def list_num_xunzhang(self) -> list[int]:
        """
        创建列表，返回每个结界的勋章数

        返回:
            勋章个数列表
        """
        alist = [0]
        for i in range(1, 10):
            x5, y5 = self.get_coor_info_picture_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_5.png"
            )
            x4, y4 = self.get_coor_info_picture_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_4.png"
            )
            x3, y3 = self.get_coor_info_picture_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_3.png"
            )
            x2, y2 = self.get_coor_info_picture_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_2.png"
            )
            x1, y1 = self.get_coor_info_picture_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_1.png"
            )
            x0, y0 = self.get_coor_info_picture_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_0.png"
            )
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
                # print(i, "已攻破")
                alist.append(-1)
        """
        for i in range (5, -1, -1):
            if i == 0:
                print(i, "勋章", alist.count(i) - 1, "个")
            else:
                print(i, "勋章", alist.count(i), "个")
        """
        list_xunzhang = "勋章数：["
        for i in range(1, 10):
            if i == 1:
                list_xunzhang = list_xunzhang + str(alist[i])
            else:
                list_xunzhang = list_xunzhang + "," + str(alist[i])
        list_xunzhang = list_xunzhang + "]"
        log.ui(list_xunzhang)
        return alist

    def fighting(self) -> None:
        """战斗"""
        for i in range(5, -1, -1):
            if self.list_xunzhang.count(i):
                k = 1
                for _ in range(1, self.list_xunzhang.count(i) + 1):
                    k = self.list_xunzhang.index(i, k)
                    log.ui(f"{k} 可进攻")
                    x, y = self.get_coor_info_picture_tupo(
                        self.tupo_geren_x[(k + 2) % 3 + 1],
                        self.tupo_geren_y[(k + 2) // 3],
                        "fail.png"
                    )
                    if x != 0 and y != 0:
                        log.ui(f"{k} 已失败")
                        k += 1
                        continue
                    self.fighting_tupo(
                        self.tupo_geren_x[(k + 2) % 3 + 1],
                        self.tupo_geren_y[(k + 2) // 3]
                    )
                    # TODO 待优化，利用时间戳的间隔判断
                    # time.sleep(4)
                    # if self.judge_click("zhunbei.png",click=False):
                    #     self.judge_click("zhunbei.png")
                    if function.result():
                        flag_victory = True
                        self.n += 1
                        log.num(f"{self.n}/{self.max}")
                    else:
                        flag_victory = False
                    function.random_sleep(0, 1)
                    # 结束界面
                    x, y = function.random_finish_left_right()
                    function.random_sleep(1, 2)
                    # 3胜奖励
                    if self.tupo_victory == 2 and flag_victory:
                        function.random_sleep(1, 2)
                        while True:
                            function.judge_click("victory.png")
                            function.random_sleep(1, 2)
                            x, y = function.get_coor_info_picture("victory.png")
                            if x == 0 or y == 0:
                                break
                        log.ui("成功攻破3次")
                    function.random_sleep(2, 3)
                    if flag_victory:
                        return

    def refresh(self) -> None:
        """刷新"""
        flag_refresh = False  # 刷新提醒
        function.random_sleep(4, 8)  # 强制等待
        while True:
            # 第一次刷新 或 冷却时间已过
            timenow = time.perf_counter()
            if self.time_refresh == 0 or self.time_refresh + 5 * 60 < timenow:
                log.ui("刷新中")
                function.random_sleep(3, 6)
                function.judge_click(
                    f"{self.resource_path}/shuaxin.png", sleeptime=2)
                function.random_sleep(2, 4)
                function.judge_click(
                    f"{self.resource_path}/queding.png", sleeptime=0.5)
                self.time_refresh = timenow
                function.random_sleep(2, 6)
                break
            elif not flag_refresh:
                time_wait = math.ceil(self.time_refresh + 5 * 60 - timenow)
                log.ui(f"等待刷新冷却，约{time_wait}秒")
                flag_refresh = True
                function.random_sleep(time_wait, time_wait+5)

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        if self.title():
            log.num(f"0/{self.max}")
            function.random_sleep(1, 3)
            while self.n < self.max:
                function.random_sleep(2, 4)
                self.list_xunzhang = self.list_num_xunzhang()
                # 胜利次数
                self.tupo_victory = self.list_xunzhang.count(-1)
                # 刷新
                if self.tupo_victory == 3:
                    self.refresh()
                # 挑战
                elif self.tupo_victory < 3:
                    log.ui(f"已攻破{self.tupo_victory}个")
                    self.fighting()
                elif self.tupo_victory > 3:
                    log.warn("暂不支持大于3个，请自行处理", True)
                    break
                function.random_sleep(2, 3)
        log.ui(f"已完成 个人突破 {self.n}次")


class JieJieTuPoYinYangLiao(JieJieTuPo):
    """阴阳寮突破
    相对坐标
    宽185
    高90
    间隔宽115
    间隔高40
    """

    @log_function_call
    def __init__(self, n: int = 0) -> None:
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
        self.n: int = 0  # 当前次数
        self.max: int = n  # 总次数

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        while True:
            if function.judge_scene(f"{self.resource_path}/title.png", "结界突破"):
                while True:
                    if function.judge_scene(f"{self.resource_path}/tupojilu.png", "阴阳寮突破"):
                        return True
                    else:
                        function.random_sleep(0, 1)
                        function.judge_click(
                            f"{self.resource_path}/yinyangliao.png",
                            dura=0.5
                        )
                        function.random_sleep(3, 4)
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def jibaicishu(self) -> bool:
        """剩余次数判断"""
        # TODO 无法生效，待废除，或使用OpenCv
        if self.title():
            while True:
                try:
                    filename = config.resource_path / self.resource_path / "jibaicishu.png"
                    log.info(filename)
                    if isinstance(filename, Path):
                        filename = str(filename)
                    button_location = pyautogui.locateOnScreen(
                        filename,
                        region=(
                            window.window_left,
                            window.window_top,
                            window.window_width,
                            window.window_height
                        )
                    )
                    print("find")
                    return False
                except:
                    print("not found")
                    print("仍有剩余次数")
                    return True

    def fighting(self) -> int:
        """战斗"""
        i = 1
        while True:
            x, y = self.get_coor_info_picture_tupo(
                self.tupo_yinyangliao_x[(i + 1) % 2 + 1],
                self.tupo_yinyangliao_y[(i + 1) // 2],
                "fail.png"
            )
            if x == 0 or y == 0:
                log.info(f"{i} 可进攻", True)
                self.fighting_tupo(
                    self.tupo_yinyangliao_x[(i + 1) % 2 + 1],
                    self.tupo_yinyangliao_y[(i + 1) // 2]
                )
                if function.result():
                    # 胜利
                    flag = 1
                else:
                    # 失败
                    flag = 0
                function.random_sleep(1, 2)
                # 结束界面
                x, y = function.random_finish_left_right()
                return flag
            else:
                log.ui(f"{i} 已失败")
                i += 1
                if i == 8:
                    # 单页上限8个
                    log.ui("当前页全部失败")
                    flag = -1
                    return flag

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        if self.title():
            log.num(f"0/{self.max}")
            function.random_sleep(1, 3)
            while self.n < self.max:
                function.random_sleep(0, 1)
                flag = self.fighting()
                if flag:
                    self.n += 1
                    log.num(f"{self.n}/{self.max}")
                elif flag == -1:
                    break
                function.random_sleep(2, 3)
        log.ui(f"已完成 阴阳寮突破 {self.n}次")
