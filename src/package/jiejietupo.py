from pathlib import Path

import pyautogui

from ..utils.application import RESOURCE_DIR_PATH
from ..utils.coordinate import Coor, RelativeCoor
from ..utils.decorator import log_function_call
from ..utils.event import event_thread
from ..utils.function import (
    RESOURCE_FIGHT_PATH,
    KeyBoard,
    check_click,
    click,
    finish,
    finish_random_left_right,
    get_coor_info,
    image_file_format,
    random_coor,
    random_sleep
)
from ..utils.log import logger
from ..utils.window import window
from .utils import Package

from enum import Enum


class LineupState(Enum):
    """阵容锁定状态"""
    NONE = 0
    LOCK = 1
    UNLOCK = 2


class JieJieTuPo(Package):
    """结界突破"""
    scene_name: str = "结界突破"
    resource_path: str = "jiejietupo"
    resource_list: list = [
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
        "yinyangliao",  # 阴阳寮突破
    ]

    def get_lineup_state(self):
        coor = self.get_coor_info("lock")
        if coor.is_effective:
            logger.ui("阵容已锁定")
            return LineupState.LOCK, coor
        coor = self.get_coor_info("unlock")
        if coor.is_effective:
            logger.ui("阵容未锁定")
            return LineupState.UNLOCK, coor
        return LineupState.NONE, None

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
        logger.info(f"looking for file: {_file_name}")  # TODO
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
                coor = random_coor(
                    button_location[0],
                    button_location[0] + button_location[2],
                    button_location[1],
                    button_location[1] + button_location[3]
                )
            except Exception:
                coor = Coor(0, 0)
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
                coor = random_coor(
                    button_location[0],
                    button_location[0] + button_location[2],
                    button_location[1],
                    button_location[1] + button_location[3]
                )
            except Exception:
                coor = Coor(0, 0)
        return coor

    def check_title(self) -> None:
        """场景"""
        _flag_title_msg = True
        while True:
            if event_thread.is_set():
                return
            coor = self.get_coor_info("title")
            if coor.is_effective:
                logger.scene(JieJieTuPo.scene_name)
                if isinstance(self, JieJieTuPoGeRen):
                    file_1 = "fangshoujilu"
                    file_2 = "geren"
                if isinstance(self, JieJieTuPoYinYangLiao):
                    file_1 = "tupojilu"
                    file_2 = "yinyangliao"
                while True:
                    coor = self.get_coor_info(file_1)
                    if coor.is_effective:
                        logger.scene(self.scene_name)
                        return
                    random_sleep(0.4, 0.8)
                    self.check_click(file_2)
                    random_sleep()
            elif _flag_title_msg:
                _flag_title_msg = False
                logger.ui("请检查游戏场景", "warn")

    def fighting_tupo(self, x0: int, y0: int) -> None:
        """结界突破战斗        

        参数:
            x0 (int): 左侧横坐标
            y0 (int): 顶部纵坐标
        """
        coor = random_coor(x0, x0 + 185, y0, y0 + 80)
        coor = RelativeCoor(coor.x, coor.y)
        click(coor)
        self.check_click("jingong")
        return

    def fighting_proactive_failure_once(self):
        """主动失败一次"""
        KeyBoard.esc()
        random_sleep()
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
    description = "默认3胜刷新，保级第一轮将会刷新，请注意当前的胜利次数"
    tupo_geren_x = {
        1: 215,
        2: 515,
        3: 815,
    }
    tupo_geren_y = {
        1: 175,
        2: 295,
        3: 415
    }

    @log_function_call
    def __init__(
        self,
        n: int = 0,
        flag_refresh_rule: int = 3,
        flag_current_level: int = 60,
        flag_target_level: int = 60
    ) -> None:
        super().__init__(n)
        self.list_xunzhang: list = None  # 勋章列表
        self.tupo_victory: int = None  # 攻破次数
        self.time_refresh: int = 0  # 记录刷新时间
        self.flag_refresh_rule: int = int(flag_refresh_rule)
        self.flag_current_level: int = int(flag_current_level)
        self.flag_target_level: int = int(flag_target_level)

    def list_num_xunzhang(self) -> list[int]:
        """
        创建列表，返回每个结界的勋章数

        返回:
            勋章个数列表
        """
        logger.ui("正在遍历结界勋章")
        alist = [0]  # 第一个数固定为0，方便后续9个计数
        for i in range(1, 10):
            if event_thread.is_set():
                return
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
        logger.ui(list_xunzhang)
        return alist

    def fighting(self) -> None:
        """战斗"""
        for i in range(5, -1, -1):  # 按勋章数排序
            if event_thread.is_set():
                return
            if self.list_xunzhang.count(i):
                k = 1
                for _ in range(1, self.list_xunzhang.count(i) + 1):
                    if event_thread.is_set():
                        return
                    k = self.list_xunzhang.index(i, k)
                    logger.ui(f"{k} 可进攻")
                    coor = self.get_coor_info_tupo(
                        self.tupo_geren_x[(k + 2) % 3 + 1],
                        self.tupo_geren_y[(k + 2) // 3],
                        "fail.png"
                    )
                    if coor.is_effective:
                        logger.ui(f"{k} 已失败")
                        k += 1
                        continue
                    self.fighting_tupo(
                        self.tupo_geren_x[(k + 2) % 3 + 1],
                        self.tupo_geren_y[(k + 2) // 3]
                    )
                    # TODO 待优化，利用时间戳的间隔判断
                    # random_sleep(4)
                    # if self.judge_click("zhunbei.png",click=False):
                    #     self.judge_click("zhunbei.png")
                    if finish():
                        flag_victory = True
                        self.done()
                    else:
                        flag_victory = False
                    random_sleep(0.4, 0.8)
                    # 结束界面
                    coor = finish_random_left_right()
                    random_sleep()
                    # 3胜奖励
                    if self.tupo_victory == 2 and flag_victory:
                        random_sleep()
                        while True:
                            if event_thread.is_set():
                                return
                            check_click(f"{RESOURCE_FIGHT_PATH}/finish")
                            random_sleep()
                            coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/finish")
                            if coor.is_zero:
                                break
                        logger.ui("成功攻破3次")
                    random_sleep(2)
                    if flag_victory:
                        return

    def fighting_proactive_failure(self, count_max) -> None:
        """主动失败

        参数:
            count_max (int): 次数
        """
        count = 0
        # 解锁阵容
        _state, _coor = self.get_lineup_state()
        if _state == LineupState.LOCK:
            click(_coor)
        logger.ui("已解锁阵容")

        # 获得每个结界的勋章数
        self.list_xunzhang = self.list_num_xunzhang()
        for i in range(1, len(self.list_xunzhang)):
            if self.list_xunzhang[i] != -1:
                logger.ui(f"{i} 可进攻")
                break

        self.fighting_tupo(
            self.tupo_geren_x[(i + 2) % 3 + 1],
            self.tupo_geren_y[(i + 2) // 3]
        )

        random_sleep(2)
        while True:
            if event_thread.is_set():
                return
            coor = get_coor_info(f"{RESOURCE_FIGHT_PATH}/fighting_back_default")
            if coor.is_zero:
                continue
            random_sleep(0.4, 0.8)
            self.fighting_proactive_failure_once()
            count += 1
            logger.ui(f"current count: {count}")
            if count >= count_max:
                self.check_click("zaicitiaozhan", is_click=False)
                finish_random_left_right()
                break

            self.check_click("zaicitiaozhan")
            random_sleep(0.4, 0.8)
            KeyBoard.enter()

        random_sleep(2)
        self.check_click("fangshoujilu", is_click=False)
        _state, _coor = self.get_lineup_state()
        if _state == LineupState.UNLOCK:
            click(_coor)
        logger.ui("已锁定阵容")

    def refresh(self) -> None:
        """刷新"""
        flag_refresh = False  # 刷新提醒
        random_sleep(4, 8)  # 强制等待
        import time
        import math
        while True:
            if event_thread.is_set():
                return
            # 第一次刷新 或 冷却时间已过
            timenow = time.perf_counter()
            if self.time_refresh == 0 or self.time_refresh + 5 * 60 < timenow:
                logger.ui("刷新中")
                random_sleep(3, 6)
                self.check_click("shuaxin", sleep_time=2)
                random_sleep(2, 4)
                self.check_click("queding", sleep_time=0.5)
                self.time_refresh = timenow
                random_sleep(2, 6)
                break
            elif not flag_refresh:
                time_wait = math.ceil(self.time_refresh + 5 * 60 - timenow)
                logger.ui(f"等待刷新冷却，约{time_wait}秒")
                flag_refresh = True
                random_sleep(time_wait, time_wait+5)

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

    def run(self):
        # 卡57级和刷新规则互斥
        self.current_counts = 0  # 当前一轮胜利次数
        if self.flag_refresh_rule:
            logger.info("只刷新")
        else:
            logger.info("保级")
            _lower_level_count = self.flag_current_level - self.flag_target_level
            if (_lower_level_count < 0):
                logger.ui("当前等级低于目标等级", "error")
                return
        self.check_title()
        logger.num(f"0/{self.max}")

        while self.n < self.max:
            if event_thread.is_set():
                return

            self.check_click("fangshoujilu", is_click=False)
            # 只需要刷新
            if self.flag_refresh_rule:
                self.list_xunzhang = self.list_num_xunzhang()
                self.tupo_victory = self.list_xunzhang.count(-1)
                if self.tupo_victory == 3:
                    self.refresh()
                elif self.tupo_victory < 3:
                    logger.ui(f"已攻破{self.tupo_victory}个")
                    self.fighting()
                elif self.tupo_victory > 3:
                    logger.ui("暂不支持大于3个，请自行处理", "warn")
                    break
            else:
                # 降级次数由输入给定
                for _ in range(_lower_level_count):
                    _lower_level_count -= 1
                    logger.ui(f"第{_}次降级")
                    self.lower_level()
                self.keep_level()
                self.tupo_victory = self.list_xunzhang.count(-1)
                # 按顺序打九
                for i in range(1, len(self.list_xunzhang)):
                    if self.n >= self.max:
                        break
                    if self.list_xunzhang[i] == -1:
                        continue
                    self.check_click("fangshoujilu", is_click=False)
                    logger.ui(f"{i} 可进攻")
                    self.fighting_tupo(
                        self.tupo_geren_x[(i + 2) % 3 + 1],
                        self.tupo_geren_y[(i + 2) // 3]
                    )
                    # 只有成功才会退出
                    while True:
                        if event_thread.is_set():
                            return
                        # TODO 失败超过一定次数视为打不过
                        if finish():
                            self.done()
                            self.tupo_victory += 1
                            random_sleep()
                            random_sleep()
                            finish_random_left_right()
                            break
                        else:
                            self.check_click("zaicitiaozhan")
                            random_sleep()
                            KeyBoard.enter()

                    random_sleep(4)

                    if self.tupo_victory in [3, 6, 9]:
                        check_click(f"{RESOURCE_FIGHT_PATH}/finish")


class JieJieTuPoYinYangLiao(JieJieTuPo):
    """阴阳寮突破
    相对坐标
    宽185
    高90
    间隔宽115
    间隔高40
    """
    scene_name = "阴阳寮突破"
    tupo_yinyangliao_x = {
        1: 460,
        2: 760
    }
    tupo_yinyangliao_y = {
        1: 170,
        2: 290,
        3: 410,
        4: 530
    }

    @log_function_call
    def __init__(self, n: int = 0) -> None:
        super().__init__(n)

    def jibaicishu(self) -> bool:
        """剩余次数判断"""
        # TODO 无法生效，待废除，或使用OpenCv
        if not self.title():
            return
        while True:
            try:
                filename = RESOURCE_DIR_PATH / self.resource_path / "jibaicishu.png"
                logger.info(filename)
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

    @log_function_call
    def fighting(self) -> int:
        """战斗"""
        i = 1  # 1-8
        while True:
            if event_thread.is_set():
                return 0
            # 当前页结界全部失效
            if i > 8:
                self.page_down(4)
                i = 1
            coor = self.get_coor_info_tupo(
                self.tupo_yinyangliao_x[(i + 1) % 2 + 1],
                self.tupo_yinyangliao_y[(i + 1) // 2],
                "fail.png"
            )
            if coor.is_zero:
                logger.ui(f"{i} 可进攻")
                self.fighting_tupo(
                    self.tupo_yinyangliao_x[(i + 1) % 2 + 1],
                    self.tupo_yinyangliao_y[(i + 1) // 2]
                )
                # TODO 多人攻破同一寮突后，无法再次进入，通过加定时器5秒判断当前是否还是寮突界面提前退出战斗循环
                # 延迟等待，判断当前寮突是否有效
                random_sleep(3)
                coor = self.get_coor_info("jingong")
                if coor.is_effective:
                    logger.ui("当前结界已被攻破", "warn")
                    i += 1
                    KeyBoard.esc()
                    continue

                flag = 1 if finish() else 0
                random_sleep()
                # 结束界面
                coor = finish_random_left_right()
                return flag
            else:
                logger.ui(f"{i} 已失败")
                i += 1
                if i == 8:
                    # 单页上限8个
                    logger.ui("当前页全部失败", "warn")
                    # return -1
                    self.page_down(4)
                    i = 1

    @log_function_call
    def page_down(self, rows: int = 1):
        """向下翻页

        参数:
            rows (int): 行数，默认1行
        """
        # TODO 操作滚轮需要鼠标在当前区域，目前来说调用该方法时，鼠标在当前区域
        import pyautogui
        pyautogui.scroll(-(rows * 240))  # 2*pis(pis=2*120)

    def run(self):
        self.check_title()
        logger.num(f"0/{self.max}")
        while self.n < self.max:
            if event_thread.is_set():
                break
            random_sleep(0.4, 0.8)
            if flag := self.fighting():
                self.done()
            elif flag == -1:
                break
            random_sleep()
