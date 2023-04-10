#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# daoguantupo.py
"""道馆突破"""

import pyautogui

from utils.decorator import *
from utils.function import function
from utils.log import log


class DaoGuanTuPo:
    """道馆突破"""
    
    @log_function_call
    def __init__(self, flag_guanzhan: bool = False):
        self.scene_name = "道馆突破"
        self.n = 0  # 当前次数
        self.resource_path = "daoguantupo"  # 路径
        self.resource_list: list = [
            "button_zhuwei",  # TODO 助威开关
            "chuzhan",  # 出战
            "daojishi",  # 倒计时
            "guanzhan",  # 观战
            "guanzhuzhan",  # TODO 馆主战
            "jijie",  # 集结
            "qianwang",  # 前往-助威
            "shengyutuposhijian",  # 剩余突破时间
            "tiaozhan",  # 挑战
            "title",  # 标题
            "victory",  # 胜利-道馆
            "zhunbei",  # 准备
            "zhanbao"  # 战报
        ]

        self.flag_guanzhan = flag_guanzhan  # 是否观战
        self.flag_fighting = False  # 是否进行中

    def get_coor_info_picture(self, file: str) -> tuple[int, int]:
        return function.get_coor_info_picture(f"{self.resource_path}/{file}")

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        self.flag_fighting = False  # 进行中
        flag_daojishi = True  # 倒计时
        while True:
            if function.judge_scene(f"{self.resource_path}/title.png", self.scene_name):
                while True:
                    # 等待倒计时自动进入
                    if self.judge_scene_daoguantupo() == "倒计时":
                        if flag_daojishi:
                            log.info("等待倒计时自动进入", True)
                            flag_daojishi = False
                        self.flag_fighting = True
                        break
                    elif self.judge_scene_daoguantupo() == "可进攻":
                        self.flag_fighting = False
                        break
                    # 馆主战
                    elif self.judge_scene_daoguantupo() == "馆主战":
                        log.warn("待开发", True)
                        break
                return True
            # 已进入道馆进攻状态
            elif self.judge_scene_daoguantupo() == "进行中":
                log.info("道馆突破进行中", True)
                self.flag_fighting = True
                return True
            elif flag_title:
                flag_title = False
                log.warn("请检查游戏场景", True)

    def judge_scene_daoguantupo(self) -> str:
        """场景判断"""
        scene = {
            "daojishi.png": "倒计时",
            "shengyutuposhijian.png": "可进攻",
            "guanzhuzhan.png": "馆主战",
            "button_zhuwei.png": "进行中"
        }  # TODO"可进攻"未实现
        for item in scene.keys():
            x, y = self.get_coor_info_picture(item)
            if x != 0 and y != 0:
                return scene[item]

    def guanzhan(self):
        """观战"""
        log.ui("观战中，暂无法自动退出，可手动退出")
        # 战报按钮
        while True:
            x, y = self.get_coor_info_picture("qianwang.png")
            if x != 0 and y != 0:
                break
            function.judge_click(f"{self.resource_path}/zhanbao.png")
            function.random_sleep(1, 2)
        # 前往按钮
        while True:
            x, y = self.get_coor_info_picture("jijie.png")
            if x != 0 and y != 0:
                break
            function.judge_click(f"{self.resource_path}/qianwang.png")
            function.random_sleep(1, 2)
        flag_zhuwei = False  # 是否能够助威
        while True:
            x1, y1 = self.get_coor_info_picture("zhuwei.png")
            x2, y2 = self.get_coor_info_picture("test_zhuwei_gray.png")
            # 可助威
            if x1 != 0 and y1 != 0:
                pyautogui.moveTo(x1, y1, duration=0.5)
                pyautogui.click()
                log.info("助威成功", True)
                flag_zhuwei = True
            # 不可助威
            elif x2 != 0 and y2 != 0:
                if flag_zhuwei:
                    log.info("无法助威", True)
                    flag_zhuwei = False
            # 结束观战
            else:
                x, y = function.get_coor_info_picture("victory.png")
                if x != 0 and y != 0:
                    log.info("胜利", True)
                    function.random_finish_left_right()
                    break
                x, y = function.get_coor_info_picture("fail.png")
                if x != 0 and y != 0:
                    log.info("失败", True)
                    function.random_finish_left_right()
                    break
            function.random_sleep(1, 2)

    # TODO 馆主战
    def guanzhuzhan(self) -> None:
        """馆主战"""
        pass

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        flag_result = False  # 结束
        if self.title():
            log.num(0)
            function.random_sleep(2, 4)
            if not self.flag_fighting:
                function.judge_click(f"{self.resource_path}/tiaozhan.png")
            function.random_sleep(2, 4)
            # 调整预设队伍
            # 开始
            while 1:
                scene = {
                    f"{self.resource_path}/zhunbei.png": "准备",
                    "victory.png": "胜利",
                    "fail.png": "失败"
                }
                for item in scene.keys():
                    x, y = function.get_coor_info_picture(item)
                    if x != 0 and y != 0:
                        if item == f"{self.resource_path}/zhunbei.png":
                            self.n += 1
                            log.num(str(self.n))
                        if item == "victory.png" or item == "fail.png":
                            function.random_sleep(1, 2)
                            flag_result = True
                        log.info(scene[item], True)
                        pyautogui.moveTo(x, y, duration=0.5)
                        pyautogui.click()
                        break
                function.random_sleep(4, 6)
                if flag_result:
                    break
            if self.flag_guanzhan:
                self.guanzhan()
        log.ui(f"已完成 {self.scene_name} 胜利{self.n}次")
