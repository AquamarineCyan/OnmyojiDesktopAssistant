import contextlib
import time
from enum import Enum
from typing import Literal

from ..utils.adapter import KeyBoard, Mouse
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.exception import CustomException, GUIStopException
from ..utils.function import finish_random_left_right, random_point, sleep
from ..utils.image import RuleImage
from ..utils.log import logger
from ..utils.paddleocr import RuleOcr
from ..utils.point import RelativePoint
from .utils import Package


class LineupState(Enum):
    """阵容锁定状态"""

    NONE = 0
    LOCK = 1
    UNLOCK = 2


class LiaoTuPoFullException(CustomException):
    """寮突破已满"""

    def __init__(self, *args):
        super().__init__(*args)
        logger.ui_warn("异常捕获：寮突破已满")


class JieJieTuPo(Package):
    """结界突破"""

    scene_name: str = "结界突破"
    resource_path: str = "jiejietupo"
    resource_list: list = [
        "fail",  # 失败
        "fangshoujilu",  # 防守记录-个人突破
        "geren",  # 个人突破
        "jingong",  # 进攻
        "lock",  # 阵容锁定
        "queding",  # 刷新-确定
        "shuaxin",  # 刷新-个人突破
        "title",  # 突破界面
        "tupojilu",  # 突破记录-阴阳寮突破
        "unlock",  # 阵容解锁
        "xunzhang_0",  # 勋章数0
        "xunzhang_1",  # 勋章数1
        "xunzhang_2",  # 勋章数2
        "xunzhang_3",  # 勋章数3
        "xunzhang_4",  # 勋章数4
        "xunzhang_5",  # 勋章数5
        "yinyangliao",  # 阴阳寮突破
    ]

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    def load_asset(self):
        self.IMAGE_FAIL = self.get_image_asset("fail")
        self.IMAGE_FANGSHOUJILU = self.get_image_asset("fangshoujilu")
        self.IMAGE_GEREN = self.get_image_asset("geren")
        self.IMAGE_JINGONG = self.get_image_asset("jingong")
        self.IMAGE_LOCK = self.get_image_asset("lock")
        self.IMAGE_TITLE = self.get_image_asset("title")
        self.IMAGE_TUPOJILU = self.get_image_asset("tupojilu")
        self.IMAGE_UNLOCK = self.get_image_asset("unlock")
        self.IMAGE_XUNZHANG_0 = self.get_image_asset("xunzhang_0")
        self.IMAGE_XUNZHANG_1 = self.get_image_asset("xunzhang_1")
        self.IMAGE_XUNZHANG_2 = self.get_image_asset("xunzhang_2")
        self.IMAGE_XUNZHANG_3 = self.get_image_asset("xunzhang_3")
        self.IMAGE_XUNZHANG_4 = self.get_image_asset("xunzhang_4")
        self.IMAGE_XUNZHANG_5 = self.get_image_asset("xunzhang_5")
        self.IMAGE_YINYANGLIAO = self.get_image_asset("yinyangliao")

    def get_lineup_state(self) -> tuple[LineupState, RelativePoint | None]:
        result = RuleImage(self.IMAGE_LOCK)
        if result.match():
            logger.ui("阵容已锁定")
            return LineupState.LOCK, result.center_point()
        result = RuleImage(self.IMAGE_UNLOCK)
        if result.match():
            logger.ui("阵容未锁定")
            return LineupState.UNLOCK, result.center_point()
        return LineupState.NONE, None

    def check_title(self) -> None:
        _msg_title = True
        while True:
            if bool(event_thread):
                raise GUIStopException

            if RuleImage(self.IMAGE_TITLE).match():
                logger.scene(JieJieTuPo.scene_name)
                if isinstance(self, JieJieTuPoGeRen):
                    file_1 = self.IMAGE_FANGSHOUJILU
                    file_2 = self.IMAGE_GEREN
                elif isinstance(self, JieJieTuPoYinYangLiao):
                    file_1 = self.IMAGE_TUPOJILU
                    file_2 = self.IMAGE_YINYANGLIAO
                while True:
                    if RuleImage(file_1).match():
                        logger.scene(self.scene_name)
                        return
                    sleep(0.4, 0.8)
                    self.check_click(file_2)
                    sleep()
            elif _msg_title:
                _msg_title = False
                self.title_error_msg()

    def fighting_into(self, x0: int, y0: int) -> None:
        """点击进入战斗

        参数:
            x0 (int): 左侧横坐标
            y0 (int): 顶部纵坐标
        """
        # 优先使用中心坐标
        _x = x0 + 185 // 2
        _y = y0 + 80 // 2
        Mouse.click(RelativePoint(_x, _y))
        if self.check_click(self.IMAGE_JINGONG, timeout=3):
            return

        for k in range(3):
            # 失败表示没有点到结界
            logger.ui_warn(f"未点到结界，重试第{k + 1}次")
            point = random_point(x0, x0 + 185, y0, y0 + 80)
            Mouse.click(point)
            if self.check_click(self.IMAGE_JINGONG, timeout=3):
                return

        # 三次都没有点到结界
        raise Exception("未点到结界")

    def fighting_proactive_failure_once(self):
        """主动失败一次"""
        KeyBoard.esc()
        sleep()
        KeyBoard.enter()
        logger.ui("手动退出")


class JieJieTuPoGeRen(JieJieTuPo):
    """个人突破
    相对坐标
    宽185
    高90
    间隔宽115
    间隔高30
    """

    scene_name = "个人突破"
    tupo_geren_x = {
        1: 215,
        2: 515,
        3: 815,
    }
    tupo_geren_y = {
        1: 175,
        2: 295,
        3: 415,
    }

    @log_function_call
    def __init__(
        self,
        n: int = 0,
        flag_refresh_rule: int = 3,
        flag_current_level: int = 57,
        flag_target_level: int = 57,
        flag_first_round_failure: bool = True,
    ) -> None:
        super().__init__(n)
        self.list_xunzhang: list = None  # 勋章列表
        self.tupo_victory: int = None  # 攻破次数
        self.time_refresh: int = 0  # 记录刷新时间
        self.flag_refresh_rule: int = flag_refresh_rule
        self.flag_current_level: int = flag_current_level
        self.flag_target_level: int = flag_target_level
        self.flag_keep_level: bool = flag_first_round_failure  # 首轮失败标志

    @staticmethod
    def description():
        logger.ui("默认3胜刷新，保级第一轮将会刷新，请注意当前的胜利次数")

    def load_asset(self):
        super().load_asset()
        self.IMAGE_REFRESH = self.get_image_asset("shuaxin")
        self.IMAGE_REFRESH_TRUE = self.get_image_asset("queding")
        self.IMAGE_FIGHT_AGAIN = self.get_image_asset("zaicitiaozhan")

    def list_num_xunzhang(self) -> list[int]:
        """
        创建列表，返回每个结界的勋章数

        返回:
            勋章个数列表
        """
        logger.ui("正在遍历结界勋章")
        alist = [0]  # 第一个数固定为0，方便后续9个计数
        for i in range(1, 10):
            if bool(event_thread):
                raise GUIStopException

            x = self.tupo_geren_x[(i + 2) % 3 + 1]
            y = self.tupo_geren_y[(i + 2) // 3]
            region = (x - 25, y + 40, 185 + 20, 90 - 20)
            if RuleImage(self.IMAGE_XUNZHANG_5, region=region, score=0.9).match():
                alist.append(5)
                continue
            if RuleImage(self.IMAGE_XUNZHANG_4, region=region, score=0.9).match():
                alist.append(4)
                continue
            if RuleImage(self.IMAGE_XUNZHANG_3, region=region, score=0.9).match():
                alist.append(3)
                continue
            if RuleImage(self.IMAGE_XUNZHANG_2, region=region, score=0.9).match():
                alist.append(2)
                continue
            if RuleImage(self.IMAGE_XUNZHANG_1, region=region, score=0.9).match():
                alist.append(1)
                continue
            if RuleImage(self.IMAGE_XUNZHANG_0, region=region, score=0.9).match():
                alist.append(0)
                continue
            alist.append(-1)  # 未识别到勋章，说明已攻破

        list_xunzhang = "勋章数：["
        for i in range(1, 10):
            if i == 1:
                list_xunzhang += str(alist[i])
            else:
                list_xunzhang = f"{list_xunzhang},{str(alist[i])}"
        list_xunzhang += "]"
        logger.ui(list_xunzhang)
        return alist

    def fighting(self) -> None:
        """战斗"""
        for i in range(5, -1, -1):  # 按勋章数排序
            if bool(event_thread):
                raise GUIStopException

            if not self.list_xunzhang.count(i):
                # 没有对应勋章数的结界，跳过
                continue

            k = 1
            for _ in range(1, self.list_xunzhang.count(i) + 1):
                if bool(event_thread):
                    raise GUIStopException

                k = self.list_xunzhang.index(i, k)
                logger.ui(f"{k} 可进攻")
                x = self.tupo_geren_x[(k + 2) % 3 + 1]
                y = self.tupo_geren_y[(k + 2) // 3]
                if RuleImage(self.IMAGE_FAIL, region=(x, y - 40, 185 + 40, 90)).match():
                    logger.ui(f"{k} 已失败")
                    k += 1
                    continue

                self.fighting_into(x, y)

                if self.check_finish():
                    flag_victory = True
                    self.done()
                else:
                    flag_victory = False

                sleep()
                finish_random_left_right()

                # 3胜奖励
                if self.tupo_victory == 2 and flag_victory:
                    sleep(2)
                    while True:
                        if bool(event_thread):
                            raise GUIStopException

                        self.check_click(self.global_assets.IMAGE_FINISH, timeout=3)
                        sleep()
                        if not RuleImage(self.global_assets.IMAGE_FINISH).match():
                            break
                    logger.ui("成功攻破3次")

                sleep(2)
                if flag_victory:
                    return

    def fighting_proactive_failure(self, count_max) -> None:
        """主动失败

        参数:
            count_max (int): 次数
        """
        count = 0
        # 解锁阵容
        state, point = self.get_lineup_state()
        if state == LineupState.LOCK:
            Mouse.click(point)
        logger.ui("已解锁阵容")
        sleep()

        # 获得每个结界的勋章数
        self.list_xunzhang = self.list_num_xunzhang()
        for i in range(1, len(self.list_xunzhang)):
            if self.list_xunzhang[i] != -1:
                logger.ui(f"{i} 可进攻")
                break

        self.fighting_into(self.tupo_geren_x[(i + 2) % 3 + 1], self.tupo_geren_y[(i + 2) // 3])

        sleep(2)
        while True:
            if bool(event_thread):
                raise GUIStopException

            if (not self.check_scene(self.global_assets.IMAGE_READY_NEW)) and (
                not self.check_scene(self.global_assets.IMAGE_READY_OLD)
            ):
                continue

            sleep()
            self.fighting_proactive_failure_once()
            count += 1
            logger.ui(f"失败次数: {count}")
            sleep(2)
            if count >= count_max:
                if self.check_scene(self.IMAGE_FIGHT_AGAIN):
                    finish_random_left_right()
                break

            self.check_click(self.IMAGE_FIGHT_AGAIN, timeout=5)
            sleep()
            KeyBoard.enter()

        sleep(2)
        self.check_scene(self.IMAGE_FANGSHOUJILU)
        state, point = self.get_lineup_state()
        if state == LineupState.UNLOCK:
            Mouse.click(point)
        logger.ui("已锁定阵容")

    def refresh(self) -> None:
        """刷新"""
        flag_refresh = False  # 刷新提醒
        sleep(4, 8)  # 强制等待
        import math

        while True:
            if bool(event_thread):
                raise GUIStopException

            # 第一次刷新 或 冷却时间已过
            timenow = time.perf_counter()
            if self.time_refresh == 0 or self.time_refresh + 5 * 60 < timenow:
                logger.ui("刷新中")
                sleep(3, 6)
                self.check_click(self.IMAGE_REFRESH, wait=2)
                sleep(2, 4)
                self.check_click(self.IMAGE_REFRESH_TRUE, wait=0.5)
                self.time_refresh = timenow
                sleep(2, 6)
                break
            elif not flag_refresh:
                time_wait = math.ceil(self.time_refresh + 5 * 60 - timenow)
                logger.ui(f"等待刷新冷却，约{time_wait}秒")
                flag_refresh = True
                sleep(time_wait, time_wait + 5)

    def lower_level(self):
        """降级，退九刷新"""
        logger.ui("开始降级")
        logger.ui("退九")
        self.fighting_proactive_failure(9)
        logger.ui("开始刷新")
        self.refresh()
        logger.ui("降级完成")

    def keep_level(self):
        """保级，退四打九，只进行退出操作"""
        self.fighting_proactive_failure(4)

    def refresh_task(self):
        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            self.list_xunzhang = self.list_num_xunzhang()
            self.tupo_victory = self.list_xunzhang.count(-1)
            if self.tupo_victory == 3:
                self.refresh()
            elif self.tupo_victory < 3:
                logger.ui(f"已攻破{self.tupo_victory}个")
                self.fighting()
            elif self.tupo_victory > 3:
                logger.ui_warn("暂不支持大于3个，请自行处理")
                return

    def level_task(self, lower_level_count: int):
        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            # 降级次数由输入给定
            for _ in range(lower_level_count):
                lower_level_count -= 1
                logger.ui(f"第{_}次降级")
                self.lower_level()

            # 保级
            if self.flag_keep_level:
                self.keep_level()
            else:
                self.flag_keep_level = True

            # 获得每个结界的勋章数
            if self.list_xunzhang is None:
                self.list_xunzhang = self.list_num_xunzhang()    
            self.tupo_victory = self.list_xunzhang.count(-1)  # 已经攻破的次数

            # 按顺序打九
            for i in range(1, len(self.list_xunzhang)):
                if self.n >= self.max:
                    return

                if self.list_xunzhang[i] == -1:
                    continue

                self.check_scene(self.IMAGE_FANGSHOUJILU)
                logger.ui(f"{i} 可进攻")
                self.fighting_into(
                    self.tupo_geren_x[(i + 2) % 3 + 1],
                    self.tupo_geren_y[(i + 2) // 3],
                )

                # 只有成功才会退出
                while True:
                    if bool(event_thread):
                        raise GUIStopException

                    # TODO 失败超过一定次数视为打不过
                    if self.check_finish():
                        self.done()
                        self.tupo_victory += 1
                        sleep()
                        finish_random_left_right()
                        break
                    else:
                        self.check_click(self.IMAGE_FIGHT_AGAIN)
                        sleep()
                        KeyBoard.enter()

                sleep(4)
                if self.tupo_victory in [3, 6, 9]:
                    self.check_click(self.global_assets.IMAGE_FINISH)
                    sleep(2)

    def run(self):
        # 卡57级和刷新规则互斥
        if self.flag_refresh_rule:
            logger.info("只刷新")
        else:
            logger.info("保级")
            lower_level_count = self.flag_current_level - self.flag_target_level
            if lower_level_count < 0:
                logger.ui_error("当前等级低于目标等级")
                return

        self.check_title()

        if self.flag_refresh_rule:  # 只需要刷新
            self.refresh_task()
        else:
            self.level_task(lower_level_count)


class JieJieTuPoYinYangLiao(JieJieTuPo):
    """阴阳寮突破
    相对坐标
    宽185
    高90
    间隔宽115
    间隔高40
    """

    scene_name = "阴阳寮突破"
    tupo_yinyangliao_x = {1: 460, 2: 760}
    tupo_yinyangliao_y = {1: 170, 2: 290, 3: 410, 4: 530}

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)
        self.process: float = 0  # 突破进度

    @staticmethod
    def description() -> Literal[100, 6]:
        now = time.strftime("%H:%M:%S")
        if now >= "21:00:00" or now < "05:00:00":
            logger.ui_warn("CD无限，桌面版单账号上限100次")
            return 100
        else:
            logger.ui_warn("CD 6次，可在每日21时后无限挑战")
            return 6

    @log_function_call
    def fighting(self) -> int:
        i = 1  # 1-8
        while True:
            if bool(event_thread):
                raise GUIStopException

            # 当前页结界全部失效
            if i > 8:
                self.page_down(4)
                i = 1
            x = self.tupo_yinyangliao_x[(i + 1) % 2 + 1]
            y = self.tupo_yinyangliao_y[(i + 1) // 2]
            region = (x, y - 40, 185 + 40, 90)
            if not RuleImage(self.IMAGE_FAIL, region=region).match():
                logger.ui(f"{i} 可进攻")
                _y = y + 35
                if i in [7, 8]:  # 最后一排坐标上移
                    _y -= 20
                    logger.ui(f"{i} 坐标修正")
                self.fighting_into(x, _y)
                # 延迟等待，判断当前寮突是否有效
                sleep(3)
                if RuleImage(self.IMAGE_JINGONG).match():
                    logger.ui_warn("当前结界已被攻破")
                    i += 1
                    KeyBoard.esc()
                    continue
                flag = 1 if self.check_finish() else 0
                sleep()
                # 结束界面
                finish_random_left_right()
                return flag
            else:
                logger.ui(f"{i} 已失败")
                if i < 8:
                    i += 1
                else:
                    # 单页上限8个
                    logger.ui_warn("当前页全部失败")
                    sleep()
                    self.page_down(4)
                    i = 1

    def page_down(self, rows: int = 1):
        """向下翻页

        参数:
            rows (int): 行数，默认1行
        """
        # TODO 操作滚轮需要鼠标在当前区域，目前来说调用该方法时，鼠标在当前区域
        Mouse.scroll(-rows * 240)  # 2*pis(pis=2*120)

    @log_function_call
    def get_current_process(self):
        result = RuleOcr().get_raw_result()
        for item in result:
            if "%" not in item.text:
                continue

            with contextlib.suppress(Exception):
                _process = float(item.text.split("%")[0])
                if _process > 100:  # 防止识别错误
                    continue
                self.process = _process
                logger.ui(f"当前进度：{self.process}%")

            if self.process > 90:
                raise LiaoTuPoFullException

            return

    def run(self):
        self.check_title()
        while self.n < self.max:
            if bool(event_thread):
                raise GUIStopException

            sleep()
            self.get_current_process()
            if flag := self.fighting():
                self.done()
            elif flag == -1:
                break
            sleep()
