from ..utils.adapter import Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from ..utils.paddleocr import RuleOcr
from .base_package import BasePackage


class DaoGuanTuPo(BasePackage):
    """道馆突破"""

    scene_name = "道馆突破"
    resource_path = "daoguantupo"
    resource_list = [
        "chuzhan",  # 出战-选队伍
        "daojishi",  # 倒计时
        "guanzhan",  # 观战
        "jijie",  # 集结
        "qianwang",  # 前往-助威
        "shengyutuposhijian",  # 剩余突破时间
        "tiaozhan",  # 挑战
        "title",  # 标题
        "zhanbao",  # 战报
        "zhuwei",  # 助威
        "zhuwei_gray",  # 助威-灰色
    ]
    STATE_IDLE = 1  # 准备界面
    STATE_WAIT_AUTO_ENTER = 2  # 等待主动进入
    STATE_WAIT_START = 3  # 手动开始
    STATE_FIGHTING = 4  # 进行中

    @log_function_call
    def __init__(self, flag_guanzhan: bool = False) -> None:
        super().__init__()
        self.flag_guanzhan = flag_guanzhan  # 是否观战
        self.flag_fighting = False  # 是否进行中
        self.state = self.STATE_IDLE

    @staticmethod
    def description() -> None:
        logger.ui("目前仅支持正在进行中的道馆突破，无法实现跳转道馆场景")

    def load_asset(self):
        self.IMAGE_CHUZHAN = self.get_image_asset("chuzhan")
        self.IMAGE_GUANZHAN = self.get_image_asset("guanzhan")
        # self.IMAGE_JIJIE = self.get_image_asset("jijie")  # no idea what it is
        self.IMAGE_QIANWANG = self.get_image_asset("qianwang")
        self.IMAGE_TIAOZHAN = self.get_image_asset("tiaozhan")
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_ZHANBAO = self.get_image_asset("zhanbao")
        self.IMAGE_ZHUWEI = self.get_image_asset("zhuwei")
        self.IMAGE_ZHUWEI_GRAY = self.get_image_asset("zhuwei_gray")

        self.OCR_TITLE = self.get_ocr_asset("title")
        self.OCR_DAOJISHI = self.get_ocr_asset("daojishi")
        self.OCR_REMAINTIME = self.get_ocr_asset("shengyutuposhijian")

    @log_function_call
    def check_title(self) -> None:
        msg_title = True
        while True:
            if bool(event_thread):
                raise GUIStopException

            sleep()
            result = RuleOcr().get_raw_result()
            for item in result:
                if self.OCR_TITLE.keyword == item.text:
                    logger.scene(self.scene_name)

                if self.OCR_DAOJISHI.keyword in item.text:
                    self.state = self.STATE_WAIT_AUTO_ENTER
                    logger.ui("等待倒计时自动进入")
                    return

                if self.OCR_REMAINTIME.keyword in item.text:
                    logger.ui("可进攻")
                    self.state = self.STATE_WAIT_START
                    return

                if self.global_assets.OCR_AUTO_FIGHT.keyword in item.text:
                    logger.ui("战斗中")
                    return

            if msg_title:
                msg_title = False
                self.title_error_msg()

    def guanzhan(self):
        """观战"""
        logger.ui_warn("观战中，暂无法自动退出，可手动退出")
        # TODO 记录总时长

        # 战报按钮
        while True:
            if bool(event_thread):
                raise GUIStopException

            if RuleImage(self.IMAGE_TITLE).match():
                self.check_click(self.IMAGE_ZHANBAO, timeout=5)
                self.check_click(self.IMAGE_QIANWANG, timeout=5)
                break
        sleep(2)

        self.current_asset_list = [
            self.IMAGE_ZHUWEI,
            self.IMAGE_ZHUWEI_GRAY,
            self.global_assets.IMAGE_FINISH,
            self.global_assets.IMAGE_FAIL,
        ]
        _flag_zhuwei_disable = False  # 是否能够助威

        while True:
            if bool(event_thread):
                raise GUIStopException

            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            logger.info(f"current result name: {result.name}")
            match result.name:
                case self.IMAGE_ZHUWEI.name:
                    Mouse.click(result.random_point())
                    logger.ui("助威成功")
                    _flag_zhuwei_disable = True

                case self.IMAGE_ZHUWEI_GRAY.name:
                    if _flag_zhuwei_disable:
                        logger.ui("无法助威")
                        _flag_zhuwei_disable = False

                case self.global_assets.IMAGE_FINISH.name:
                    self.ensure_finish()

                case self.global_assets.IMAGE_FAIL.name:
                    logger.ui_warn("失败")
                    sleep(0.4, 0.8)
                    finish_random_left_right()

            sleep(4)

    def done(self):
        self.n += 1
        logger.progress(self.n)

    def run(self):
        self.check_title()
        sleep(2)
        if self.state == self.STATE_WAIT_START:
            self.check_click(self.IMAGE_TIAOZHAN, timeout=3)

        sleep(4)  # 等待过场动画

        # 开始
        self.current_asset_list = [
            self.global_assets.IMAGE_READY_OLD,
            self.global_assets.IMAGE_READY_NEW,
            # self.global_image.IMAGE_VICTORY,
            self.global_assets.IMAGE_FAIL,
            self.global_assets.IMAGE_FINISH,
        ]

        while True:
            if bool(event_thread):
                raise GUIStopException

            result = check_image_once(self.current_asset_list)
            if result is None:
                continue

            logger.info(f"current result name: {result.name}")
            match result.name:
                case self.global_assets.IMAGE_READY_OLD.name | self.global_assets.IMAGE_READY_NEW.name:
                    logger.ui("准备")
                    sleep()
                    Mouse.click(result.center_point())
                    self.done()
                    sleep(5)  # 避免间隔过短影响绿标

                case self.global_assets.IMAGE_FINISH.name:
                    sleep()
                    finish_random_left_right()
                    break

                case self.global_assets.IMAGE_FAIL.name:
                    sleep()
                    finish_random_left_right()
                    logger.ui_warn("失败")
                    break

        if self.flag_guanzhan:
            sleep(2)
            self.guanzhan()
