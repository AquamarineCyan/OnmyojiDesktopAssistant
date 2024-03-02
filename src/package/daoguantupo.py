from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import (
    check_scene_multiple_once,
    click,
    finish_random_left_right,
    get_coor_info,
    random_sleep
)
from ..utils.log import logger
from .utils import Package


class DaoGuanTuPo(Package):
    """道馆突破"""
    scene_name = "道馆突破"
    resource_path = "daoguantupo"
    resource_list = [
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
        "zhanbao",  # 战报
    ]
    description = "目前仅支持正在进行中的道馆突破，无法实现跳转道馆场景"

    @log_function_call
    def __init__(self, flag_guanzhan: bool = False) -> None:
        super().__init__()
        self.flag_guanzhan = flag_guanzhan  # 是否观战
        self.flag_fighting = False  # 是否进行中

    def check_title(self) -> None:
        """场景"""
        _flag_title_msg = True
        self.flag_fighting = False  # 进行中
        _flag_daojishi = True  # 倒计时
        while True:
            if event_thread.is_set():
                return
            coor_title = self.get_coor_info("title")
            coor_fighting = self.get_coor_info("button_zhuwei")

            if coor_title.is_effective:
                logger.scene(self.scene_name)
                self.current_resource_list = [
                    f"{self.resource_path}/daojishi",
                    f"{self.resource_path}/shengyutuposhijian",
                    f"{self.resource_path}/guanzhuzhan",
                    f"{self.resource_path}/button_zhuwei",
                ]
                self.log_current_scene_list()
                while True:
                    if event_thread.is_set():
                        return
                    scene, _ = check_scene_multiple_once(self.current_resource_list)
                    if scene is None:
                        continue
                    scene = self.scene_handle(scene)

                    match scene:
                        case "daojishi":  # 等待倒计时自动进入
                            if _flag_daojishi:
                                logger.ui("等待倒计时自动进入")
                                _flag_daojishi = False
                            self.flag_fighting = True
                            return
                        case "shengyutuposhijian":  # 可进攻
                            self.flag_fighting = False
                            return
                        case "guanzhuzhan":  # 馆主战
                            logger.ui("馆主战，待开发", "warn")
                            return

            # 道馆突破进行中
            elif coor_fighting.is_effective:
                logger.ui("道馆突破进行中")
                self.flag_fighting = True
                return True
            elif _flag_title_msg:
                _flag_title_msg = False
                logger.ui("请检查游戏场景", "warn")

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
            self.check_click("zhanbao")
            random_sleep()
        # 前往按钮
        while True:
            if event_thread.is_set():
                return
            coor = self.get_coor_info("jijie")
            if coor.is_effective:
                break
            self.check_click("qianwang")
            random_sleep()

        self.current_resource_list = [
            f"{self.resource_path}/zhuwei",
            f"{self.resource_path}/test_zhuwei_gray",
            f"{self.global_resource_path}/finish",
            f"{self.global_resource_path}/fail",
        ]
        _flag_zhuwei_disable = False  # 是否能够助威

        while True:
            if event_thread.is_set():
                return
            scene, coor = self.check_scene_multiple_once()
            if scene is None:
                continue
            logger.info(f"current scene: {scene}")
            if "/" in scene:
                scene = scene.split("/")[-1]

            match scene:
                case "zhuwei":
                    click(coor)
                    logger.ui("助威成功")
                    _flag_zhuwei_disable = True
                case "test_zhuwei_gray":
                    if _flag_zhuwei_disable:
                        logger.ui("无法助威")
                        _flag_zhuwei_disable = False
                case "finish":
                    self.ensure_finish()
                case "fail":
                    logger.ui("失败", "warn")
                    random_sleep(0.4, 0.8)
                    finish_random_left_right()
                    while True:
                        if event_thread.is_set():
                            return
                        coor = get_coor_info(f"{self.global_resource_path}/fail")
                        # 未重复检测到，表示成功点击
                        if coor.is_zero:
                            self.done()
                            break
                        click()
                        random_sleep(0.4, 0.8)
            random_sleep(4)

    def guanzhuzhan(self) -> None:  # TODO
        """馆主战"""
        pass

    def run(self):
        self.check_title()
        logger.num(0)
        random_sleep(2, 4)
        if not self.flag_fighting:
            self.check_click("tiaozhan")
        random_sleep(2, 4)
        # TODO调整预设队伍
        # 开始
        while True:
            if event_thread.is_set():
                return
            self.current_resource_list = [
                f"{self.global_resource_path}/ready_old",
                f"{self.global_resource_path}/ready_new",
                f"{self.global_resource_path}/victory",
                f"{self.global_resource_path}/fail",
                f"{self.global_resource_path}/finish",
            ]
            scene, coor = self.check_scene_multiple_once()
            if scene is None:
                continue
            logger.info(f"coor: {coor.coor}")
            scene = self.scene_handle(scene)

            match scene:
                case "ready_old" | "ready_new":
                    logger.ui("准备")
                    click(coor)
                    self.n += 1
                    logger.num(str(self.n))
                    random_sleep()
                case "victory":
                    random_sleep()
                case "finish":
                    finish_random_left_right()
                    break
                case "fail":
                    logger.ui("失败，需要手动处理", "warn")
                    break

        if self.flag_guanzhan:
            self.guanzhan()
