#!usr/bin/env python3
# daoguantupo.py
"""
道馆突破
"""

import time
import pyautogui

from utils.function import Function
from utils.log import log

"""
标题
title.png
挑战
tiaozhan.png
倒计时
daojishi.png
预设1
yushe1.png
出战
chuzhan.png
准备
zhunbei.png
助威开关
button_zhuwei.png
剩余突破时间
shengyutuposhijian.png
观战
zhanbao.png
战报
guanzhan.png
前往
jijie.png
集结
qianwang.png
助威
zhuwei.png
馆主战
guanzhuzhan.png
胜利
victory.png
"""


class DaoGuanTuPo(Function):
    """道馆突破"""

    def __init__(self):
        self.scene_name = "道馆突破"
        self.picpath = "daoguantupo"  # 图片路径
        self.m = 0  # 当前次数
        self.flag_fighting = False  # 是否进行中

    def title(self):
        """场景"""
        flag_title = True  # 场景提示
        self.flag_fighting = False  # 进行中
        flag_daojishi = True  # 倒计时
        while True:
            if self.judge_scene(f"{self.picpath}/title.png", self.scene_name):
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

    def judge_scene_daoguantupo(self):
        """场景判断"""
        scene = {
            "daojishi.png": "倒计时",
            "shengyutuposhijian.png": "可进攻",
            "guanzhuzhan.png": "馆主战",
            "button_zhuwei.png": "进行中"
        }  # "可进攻"未实现
        for item in scene.keys():
            x, y = self.get_coor_info_picture(f"{self.picpath}/{item}")
            if x != 0 and y != 0:
                return scene[item]

    def guanzhan(self):
        """观战"""
        time.sleep(2)
        log.info("观战中，暂无法自动退出，可手动退出", True)
        # 战报按钮
        while True:
            x, y = self.get_coor_info_picture(f"{self.picpath}/qianwang.png")
            if x != 0 and y != 0:
                break
            self.judge_click(f"{self.picpath}/zhanbao.png")
            self.random_sleep(1, 2)
        # 前往按钮
        while True:
            x, y = self.get_coor_info_picture(f"{self.picpath}/jijie.png")
            if x != 0 and y != 0:
                break
            self.judge_click(f"{self.picpath}/qianwang.png")
            self.random_sleep(1, 2)
        flag_zhuwei = False  # 是否能够助威
        while True:
            x1, y1 = self.get_coor_info_picture(f"{self.picpath}/zhuwei.png")
            x2, y2 = self.get_coor_info_picture(
                f"{self.picpath}/test_zhuwei_gray.png")
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
                x, y = self.get_coor_info_picture("victory.png")
                if x != 0 and y != 0:
                    log.info("胜利", True)
                    self.random_finish_left_right()
                    break
                x, y = self.get_coor_info_picture("fail.png")
                if x != 0 and y != 0:
                    log.info("失败", True)
                    self.random_finish_left_right()
                    break
            time.sleep(2)

    def guanzhuzhan(self):
        """馆主战"""

    def run(self, flag_guanzhan: bool = False):
        time.sleep(2)
        flag_result = False  # 结束
        time_progarm = self.TimeProgram()  # 程序计时
        time_progarm.start()
        if self.title():
            log.num(0)
            self.random_sleep(2, 4)
            if not self.flag_fighting:
                self.judge_click(f"{self.picpath}/tiaozhan.png")
            self.random_sleep(2, 4)
            # 调整预设队伍
            # 开始
            while 1:
                scene = {
                    f"{self.picpath}/zhunbei.png": "准备",
                    "victory.png": "胜利",
                    "fail.png": "失败"
                }
                for item in scene.keys():
                    x, y = self.get_coor_info_picture(item)
                    if x != 0 and y != 0:
                        if item == f"{self.picpath}/zhunbei.png":
                            self.m += 1
                            log.num(str(self.m))
                        if item == "victory.png" or item == "fail.png":
                            time.sleep(2)
                            flag_result = True
                        log.info(scene[item], True)
                        pyautogui.moveTo(x, y, duration=0.5)
                        pyautogui.click()
                        break
                self.random_sleep(4, 6)
                if flag_result:
                    break
            if flag_guanzhan:
                self.guanzhan()
        text = f"已完成 道馆突破 胜利{self.m}次"
        time_progarm.end()
        text = text + " " + time_progarm.print()
        log.info(text, True)
        # 启用按钮
        log.is_fighting(False)
