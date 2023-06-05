#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# jiejietupo.py
"""结界突破"""

import math
import time
from pathlib import Path

import pyautogui

from ..utils.application import RESOURCE_DIR_PATH
from ..utils.coordinate import Coor
from ..utils.decorator import run_in_thread, time_count, log_function_call
from ..utils.function import (
    RESOURCE_FIGHT_PATH,
    check_click,
    check_scene,
    click,
    finish,
    finish_random_left_right,
    get_coor_info,
    image_file_format,
    random_coor,
    random_sleep
)
from ..utils.log import log
from ..utils.window import window


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

    def get_coor_info_tupo(self, x1: int, y1: int, file: Path | str) -> Coor:
        """图像识别，返回图像的局部相对坐标

        参数:
            x1 (int): 识别区域左侧横坐标
            y1 (int): 识别区域顶部纵坐标
            file (Path | str): 图像名称

        返回:
            Coor: 坐标
        """
        _file_name = image_file_format(RESOURCE_DIR_PATH / self.resource_path / file)
        log.info(f"looking for file: {_file_name}")
        if "xunzhang" in file:
            # 个人突破
            try:
                button_location = pyautogui.locateOnScreen(
                    _file_name,
                    region=(
                        x1 + window.window_left - 25,
                        y1 + window.window_top + 40,
                        185 + 20,
                        90 - 20
                    ),
                    confidence=0.9
                )
                x, y = random_coor(
                    button_location[0],
                    button_location[0] + button_location[2],
                    button_location[1],
                    button_location[1] + button_location[3]
                )
            except Exception:
                x = y = 0
        else:
            # 阴阳寮突破
            try:
                button_location = pyautogui.locateOnScreen(
                    _file_name,
                    region=(
                        x1 + window.window_left,
                        y1 - 40 + window.window_top,
                        185 + 40,
                        90
                    ),
                    confidence=0.8
                )
                x, y = random_coor(
                    button_location[0],
                    button_location[0] + button_location[2],
                    button_location[1],
                    button_location[1] + button_location[3]
                )
            except Exception:
                x = y = 0
        return Coor(x, y)

    def fighting_tupo(self, x0: int, y0: int) -> None:
        """结界突破战斗        

        参数:
            x0 (int): 左侧横坐标
            y0 (int): 顶部纵坐标
        """
        coor = random_coor(x0, x0 + 185, y0, y0 + 80)
        pyautogui.moveTo(
            coor.x + window.window_left,
            coor.y + window.window_top,
            duration=0.5
        )
        click()
        while True:
            coor = get_coor_info(f"{self.resource_path}/jingong")
            if coor.is_effective:
                click(coor)
                break

    def fighting_fail_again(self):
        # TODO 主动失败
        random_sleep(1, 2)
        while True:
            pyautogui.press("esc")
            if check_scene(f"{self.resource_path}/fighting_fail"):
                pyautogui.press("enter")
                log.ui("手动退出")
                break
            random_sleep(0, 1)


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
            if check_scene(f"{self.resource_path}/title", "结界突破"):
                while True:
                    if check_scene(f"{self.resource_path}/fangshoujilu.png", "个人突破"):
                        return True
                    random_sleep(0, 1)
                    check_click(f"{self.resource_path}/geren.png")
                    random_sleep(3, 4)
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
            coor5 = self.get_coor_info_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_5.png"
            )
            coor4 = self.get_coor_info_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_4.png"
            )
            coor3 = self.get_coor_info_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_3.png"
            )
            coor2 = self.get_coor_info_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_2.png"
            )
            coor1 = self.get_coor_info_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_1.png"
            )
            coor0 = self.get_coor_info_tupo(
                self.tupo_geren_x[(i + 2) % 3 + 1],
                self.tupo_geren_y[(i + 2) // 3],
                "xunzhang_0.png"
            )
            if coor5.is_effective:
                alist.append(5)
                continue
            if coor4.is_effective:
                alist.append(4)
                continue
            if coor3.is_effective:
                alist.append(3)
                continue
            if coor2.is_effective:
                alist.append(2)
                continue
            if coor1.is_effective:
                alist.append(1)
                continue
            if coor0.is_effective:
                alist.append(0)
                continue
            if coor5.is_zero \
                    and coor4.is_zero \
                    and coor3.is_zero \
                    and coor2.is_zero \
                    and coor1.is_zero \
                    and coor0.is_zero:
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
                list_xunzhang = f"{list_xunzhang},{str(alist[i])}"
        list_xunzhang = f"{list_xunzhang}]"
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
                    coor = self.get_coor_info_tupo(
                        self.tupo_geren_x[(k + 2) % 3 + 1],
                        self.tupo_geren_y[(k + 2) // 3],
                        "fail.png"
                    )
                    if coor.is_effective:
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
                    if finish():
                        flag_victory = True
                        self.n += 1
                        log.num(f"{self.n}/{self.max}")
                    else:
                        flag_victory = False
                    random_sleep(0, 1)
                    # 结束界面
                    coor = finish_random_left_right()
                    random_sleep(1, 2)
                    # 3胜奖励
                    if self.tupo_victory == 2 and flag_victory:
                        random_sleep(1, 2)
                        while True:
                            check_click(f"{RESOURCE_FIGHT_PATH}/finish")
                            random_sleep(1, 2)
                            coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")
                            if coor.is_zero:
                                break
                        log.ui("成功攻破3次")
                    random_sleep(2, 3)
                    if flag_victory:
                        return

    def refresh(self) -> None:
        """刷新"""
        flag_refresh = False  # 刷新提醒
        random_sleep(4, 8)  # 强制等待
        while True:
            # 第一次刷新 或 冷却时间已过
            timenow = time.perf_counter()
            if self.time_refresh == 0 or self.time_refresh + 5 * 60 < timenow:
                log.ui("刷新中")
                random_sleep(3, 6)
                check_click(f"{self.resource_path}/shuaxin", sleeptime=2)
                random_sleep(2, 4)
                check_click(f"{self.resource_path}/queding", sleeptime=0.5)
                self.time_refresh = timenow
                random_sleep(2, 6)
                break
            elif not flag_refresh:
                time_wait = math.ceil(self.time_refresh + 5 * 60 - timenow)
                log.ui(f"等待刷新冷却，约{time_wait}秒")
                flag_refresh = True
                random_sleep(time_wait, time_wait+5)

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        if self.title():
            log.num(f"0/{self.max}")
            while self.n < self.max:
                random_sleep(2, 4)
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
                    log.warn("暂不支持大于3个，请自行处理")
                    break
                random_sleep(2, 3)
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
            if check_scene(f"{self.resource_path}/title", "结界突破"):
                while True:
                    if check_scene(f"{self.resource_path}/tupojilu", "阴阳寮突破"):
                        return True
                    random_sleep(0, 1)
                    check_click(f"{self.resource_path}/yinyangliao.png")
                    random_sleep(3, 4)
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景")

    def jibaicishu(self) -> bool:
        """剩余次数判断"""
        # TODO 无法生效，待废除，或使用OpenCv
        if self.title():
            while True:
                try:
                    filename = RESOURCE_DIR_PATH / self.resource_path / "jibaicishu.png"
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
                except Exception:
                    print("not found")
                    print("仍有剩余次数")
                    return True

    def fighting(self) -> int:
        """战斗"""
        i = 1
        while True:
            coor = self.get_coor_info_tupo(
                self.tupo_yinyangliao_x[(i + 1) % 2 + 1],
                self.tupo_yinyangliao_y[(i + 1) // 2],
                "fail.png"
            )
            if coor.is_zero:
                log.info(f"{i} 可进攻", True)
                self.fighting_tupo(
                    self.tupo_yinyangliao_x[(i + 1) % 2 + 1],
                    self.tupo_yinyangliao_y[(i + 1) // 2]
                )
                if finish():
                    # 胜利
                    flag = 1
                else:
                    # 失败
                    flag = 0
                random_sleep(1, 2)
                # 结束界面
                coor = finish_random_left_right()
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
            random_sleep(1, 3)
            while self.n < self.max:
                random_sleep(0, 1)
                if flag := self.fighting():
                    self.n += 1
                    log.num(f"{self.n}/{self.max}")
                elif flag == -1:
                    break
                random_sleep(2, 3)
        log.ui(f"已完成 阴阳寮突破 {self.n}次")
