import time

from ..utils.adapter import Mouse
from ..utils.application import SCREENSHOT_DIR_PATH
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import GUIStopException
from ..utils.function import finish_random_left_right, sleep
from ..utils.image import RuleImage, check_image_once
from ..utils.log import logger
from ..utils.ocr_engine import RuleOcr
from .base_package import BasePackage


class DaoGuanTuPo(BasePackage):
    """道馆突破"""

    scene_name = "道馆突破"
    resource_path = "daoguantupo"
    resource_list = (
        "daojishi",  # 倒计时
        "guanzhan",  # 观战
        "qianwang",  # 前往-助威
        "shengyutuposhijian",  # 剩余突破时间
        "tiaozhan",  # 挑战
        "title",  # 标题
        "zhanbao",  # 战报
        "zhuwei",  # 助威
        "zhuwei_gray",  # 助威-灰色
    )

    @log_function_call
    def __init__(self, n: int = 0, flag_guanzhan: bool = False, flag_screenshot: bool = False) -> None:
        super().__init__(n)
        self.flag_guanzhan: bool = flag_guanzhan  # 是否观战
        self.flag_screenshot: bool = flag_screenshot  # 是否结束后截图
        self.need_challenge: bool = False  # 检测到「可进攻」后需点击挑战

    @staticmethod
    def description() -> None:
        logger.ui("目前仅支持正在进行中的道馆突破，无法实现跳转道馆场景")

    def load_asset(self) -> None:
        self.IMAGE_GUANZHAN = self.get_image_asset("guanzhan")
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
        msg_title: bool = True
        self.need_challenge: bool = False
        rule_title = RuleOcr(self.OCR_TITLE)
        rule_daojishi = RuleOcr(self.OCR_DAOJISHI)
        rule_remaintime = RuleOcr(self.OCR_REMAINTIME)
        while True:
            if bool(event_thread):
                raise GUIStopException

            self.sleep_interval()
            result = RuleOcr().get_raw_result()

            # 标题
            if rule_title.match(ocr_result=result):
                logger.ui_hint(self.scene_name)

            # 倒计时自动进入
            if rule_daojishi.match(ocr_result=result):
                logger.ui("等待倒计时自动进入")
                return

            # 剩余突破时间
            if rule_remaintime.match(ocr_result=result):
                self.need_challenge = True
                logger.ui("可进攻")
                return

            if any(self.global_assets.OCR_AUTO_FIGHT.keyword in item.text for item in result):
                logger.ui("战斗中")
                return

            if msg_title:
                msg_title = False
                self.title_error_msg()

    def guanzhan(self) -> None:
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

            self.sleep_interval()
        sleep(2)

        self.current_asset_list = [
            self.IMAGE_ZHUWEI,
            self.IMAGE_ZHUWEI_GRAY,
            self.global_assets.IMAGE_FINISH,
        ]
        self.current_asset_list.extend(self.global_assets.ALL_FAIL_IMAGES)
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
                    if self.flag_screenshot:
                        sleep()
                        self.screenshot()
                        logger.ui("「战斗结算」已截图")
                    self.ensure_finish()

                case name if name in self.global_assets.ALL_FAIL_NAMES:
                    logger.ui_warn(f"失败{('（' + result.description + '）') if result.description else ''}")
                    sleep(0.4, 0.8)
                    finish_random_left_right()

            sleep(4)

    def done(self) -> None:
        self.n += 1
        logger.progress(self.n)

    def task_finish_info(self) -> None:
        if self.flag_screenshot:
            logger.ui(f"截图保存在\n{SCREENSHOT_DIR_PATH / self.resource_path}")

    def check_and_enter_battle(self) -> None:
        """检查标题并进入战斗场景"""
        self.check_title()
        sleep(2)
        if self.need_challenge:
            self.check_click(self.IMAGE_TIAOZHAN, timeout=3)
        sleep(4)  # 等待过场动画

    def click_ready(self, timeout: float = 5) -> bool:
        """点击准备按钮直到消失

        Args:
            timeout (float): 总超时时间，单位秒，默认5秒。

        Returns:
            bool: 准备成功返回 True，超时返回 False
        """
        start_time = time.time()
        ready_images = [
            self.global_assets.IMAGE_READY_OLD,
            self.global_assets.IMAGE_READY_NEW,
        ]
        rule = None  # 首次检测到的准备按钮，后续只检测该按钮
        while time.time() - start_time < timeout:
            if bool(event_thread):
                raise GUIStopException

            if rule is None:
                # 首次检测全部准备按钮
                for image in ready_images:
                    _rule = RuleImage(image)
                    if _rule.match():
                        rule = _rule
                        break
                if rule is None:
                    # 未检测到准备按钮，视为准备完成
                    logger.ui("准备完成")
                    return True

            Mouse.click(rule.center_point())
            sleep(0.1)  # 点击后等待100毫秒再次检测

            if not rule.match():
                # 该按钮已消失，准备完成
                logger.ui("准备完成")
                return True

        logger.warning("准备超时")
        return False

    def wait_for_battle_ready(self) -> bool:
        """等待战斗准备界面并处理"""
        self.current_asset_list = [
            self.global_assets.IMAGE_READY_OLD,
            self.global_assets.IMAGE_READY_NEW,
            self.global_assets.IMAGE_FINISH,
        ]
        self.current_asset_list.extend(self.global_assets.ALL_FAIL_IMAGES)

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
                    self.click_ready()
                    self.done()

                case self.global_assets.IMAGE_FINISH.name:
                    sleep()
                    if self.flag_screenshot:
                        self.screenshot()
                        logger.ui("「战斗结算」已截图")
                    sleep()
                    finish_random_left_right()
                    return True

                case name if name in self.global_assets.ALL_FAIL_NAMES:
                    sleep()
                    finish_random_left_right()
                    logger.ui_warn(f"失败{('（' + result.description + '）') if result.description else ''}")
                    return False

    def run(self) -> None:
        for i in range(self.max):
            if bool(event_thread):
                raise GUIStopException

            logger.ui(f"第{i + 1}次战斗")

            self.check_and_enter_battle()
            self.wait_for_battle_ready()

            if self.flag_guanzhan:
                sleep(2)
                self.guanzhan()
