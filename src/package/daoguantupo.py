#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# daoguantupo.py
"""道馆突破"""

from src.utils.event import event_thread
from ..utils.decorator import log_function_call, run_in_thread, time_count
from ..utils.function import (
    RESOURCE_FIGHT_PATH,
    check_click,
    check_scene,
    check_scene_multiple_once,
    click,
    finish_random_left_right,
    get_coor_info,
    random_sleep
)
from ..utils.log import logger


class DaoGuanTuPo:
    """道馆突破"""

    @log_function_call
    def __init__(self, flag_guanzhan: bool = False) -> None:
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

    def get_coor_info(self, file: str):
        return get_coor_info(f"{self.resource_path}/{file}")

    def title(self) -> bool:
        """场景"""
        flag_title = True  # 场景提示
        self.flag_fighting = False  # 进行中
        flag_daojishi = True  # 倒计时
        while True:
            if event_thread.is_set():
                return
            if check_scene(f"{self.resource_path}/title", self.scene_name):
                while True:
                    if event_thread.is_set():
                        return
                    # 等待倒计时自动进入
                    if self.judge_scene_daoguantupo() == "倒计时":
                        if flag_daojishi:
                            logger.ui("等待倒计时自动进入")
                            flag_daojishi = False
                        self.flag_fighting = True
                        break
                    elif self.judge_scene_daoguantupo() == "可进攻":
                        self.flag_fighting = False
                        break
                    # 馆主战
                    elif self.judge_scene_daoguantupo() == "馆主战":
                        logger.ui("待开发", "warn")
                        break
                return True
            # 已进入道馆进攻状态
            elif self.judge_scene_daoguantupo() == "进行中":
                logger.ui("道馆突破进行中")
                self.flag_fighting = True
                return True
            elif flag_title:
                flag_title = False
                logger.ui("请检查游戏场景", "warn")

    def judge_scene_daoguantupo(self) -> str:
        """场景判断"""
        scene = {
            "daojishi.png": "倒计时",
            "shengyutuposhijian.png": "可进攻",
            "guanzhuzhan.png": "馆主战",
            "button_zhuwei.png": "进行中"
        }  # TODO"可进攻"未实现
        for item in scene:
            if event_thread.is_set():
                return
            coor = self.get_coor_info(item)
            if coor.is_effective:
                return scene[item]

    def guanzhan(self):
        """观战"""
        logger.ui("观战中，暂无法自动退出，可手动退出", "warn")
        # 战报按钮
        while True:
            if event_thread.is_set():
                return
            coor = self.get_coor_info("qianwang")
            if coor.is_effective:
                break
            check_click(f"{self.resource_path}/zhanbao")
            random_sleep(1, 2)
        # 前往按钮
        while True:
            if event_thread.is_set():
                return
            coor = self.get_coor_info("jijie")
            if coor.is_effective:
                break
            check_click(f"{self.resource_path}/qianwang")
            random_sleep(1, 2)
        flag_zhuwei = False  # 是否能够助威
        while True:
            if event_thread.is_set():
                return
            coor1 = self.get_coor_info("zhuwei")
            coor2 = self.get_coor_info("test_zhuwei_gray")
            # 可助威
            if coor1.is_effective:
                click(coor)
                logger.ui("助威成功")
                flag_zhuwei = True
            # 不可助威
            elif coor2.is_effective:
                if flag_zhuwei:
                    logger.ui("无法助威")
                    flag_zhuwei = False
            # 结束观战
            else:
                coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")
                if coor.is_effective:
                    logger.ui("胜利")
                    finish_random_left_right()
                    break
                coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/fail")
                if coor.is_effective:
                    logger.ui("失败", "warn")
                    finish_random_left_right()
                    break
            random_sleep(1, 2)

    # TODO 馆主战
    def guanzhuzhan(self) -> None:
        """馆主战"""
        pass

    @run_in_thread
    @time_count
    @log_function_call
    def run(self) -> None:
        if self.title():
            logger.num(0)
            random_sleep(2, 4)
            if not self.flag_fighting:
                check_click(f"{self.resource_path}/tiaozhan")
            random_sleep(2, 4)
            # TODO调整预设队伍
            # 开始
            while True:
                if event_thread.is_set():
                    return
                _resource_list = [
                    f"{self.resource_path}/zhunbei",
                    f"{RESOURCE_FIGHT_PATH}/victory",
                    f"{RESOURCE_FIGHT_PATH}/fail",
                    f"{RESOURCE_FIGHT_PATH}/finish"
                ]
                scene, coor = check_scene_multiple_once(_resource_list)
                if scene == f"{self.resource_path}/zhunbei":
                    logger.ui("准备")
                    click(coor)
                    self.n += 1
                    logger.num(str(self.n))
                    random_sleep(1, 2)
                elif scene == f"{RESOURCE_FIGHT_PATH}/victory":
                    random_sleep(1, 2)
                elif scene == f"{RESOURCE_FIGHT_PATH}/finish":
                    logger.ui("失败", "warn")
                    finish_random_left_right()
                    break
                elif scene == f"{RESOURCE_FIGHT_PATH}/fail":
                    logger.ui("失败", "warn")
                    finish_random_left_right()
                    break

            if self.flag_guanzhan:
                self.guanzhan()
        logger.ui(f"已完成 {self.scene_name} 胜利{self.n}次")
