"""check_click / check_title 的挂死兜底

这两个方法默认 `timeout=0`（永不超时）。设计上依赖「目标一定会出现」，
但 UI 改版、分辨率变化、额外弹窗时目标永远不出现，任务线程会永久挂死：
停止按钮依赖的 `event_thread` 检查执行不到，`prevent_sleep(False)` 也不执行。

兜底策略：连续匹配不到超过 `STALL_TIMEOUT`（默认 10 分钟）即抛 CustomException，
让任务显式失败并给出可读报错，而不是无声挂死。
"""
import pytest

from src.package.base_package import BasePackage
from src.utils.assets import AssetImage, AssetOcr
from src.utils.exception import CustomException, GUIStopException


class _AlwaysMiss(BasePackage):
    """永远匹配不到的目标；用最小 sleep 让循环能推进"""

    scene_name = "测试场景"

    def __init__(self):
        self.n = 0
        self.max = 1
        self.slept = 0.0

    def sleep_interval(self):
        self.slept += 0.01

    def title_error_msg(self):
        pass

    def done(self):
        self.n += 1


class _AlwaysHit(_AlwaysMiss):
    def __init__(self):
        super().__init__()
        self.hits = 0


@pytest.fixture
def patch_rule(monkeypatch):
    """替换 RuleImage / RuleOcr 的 match 结果"""
    return monkeypatch


def _asset_image(name="目标"):
    return AssetImage(name=name, file="__not_exist__.png", region=(0, 0, 10, 10), score=0.9)


def _asset_ocr(name="目标"):
    return AssetOcr(name=name, keyword="目标", region=(0, 0, 10, 10), score=0.9)


# ------------------------------------------------------------------ 兜底生效


def test_check_click_raises_after_stall_timeout(patch_rule):
    from src.package import base_package as bp

    pkg = _AlwaysMiss()
    monkey_result = {"n": 0}

    class _NeverMatch:
        def __init__(self, *a, **k):
            pass

        def match(self, *a, **k):
            monkey_result["n"] += 1
            return False

        def random_point(self):  # pragma: no cover
            raise AssertionError("未匹配时不应取点")

    patch_rule.setattr(bp, "RuleImage", _NeverMatch)

    # 用极短的 stall_timeout 触发，不必真等 10 分钟
    with pytest.raises(CustomException) as exc:
        pkg.check_click(_asset_image(), timeout=0, stall_timeout=0.05)

    assert monkey_result["n"] > 1, "应循环多次后才中断"
    assert "目标" in str(exc.value), "报错要带上目标名字，否则用户不知道卡在哪"
    assert bp.STALL_TIMEOUT == 600.0


def test_check_title_raises_after_stall_timeout(patch_rule):
    from src.package import base_package as bp

    pkg = _AlwaysMiss()
    pkg.IMAGE_TITLE = _asset_image("场景标题")

    class _NeverMatch:
        def __init__(self, *a, **k):
            pass

        def match(self, *a, **k):
            return False

    patch_rule.setattr(bp, "RuleImage", _NeverMatch)

    with pytest.raises(CustomException) as exc:
        pkg.check_title(stall_timeout=0.05)

    assert "场景标题" in str(exc.value)


# ------------------------------------------------------------------ 不误伤


def test_stall_timeout_zero_disables_guard(patch_rule):
    """显式传 0 表示关闭兜底，恢复旧的无限等待语义"""
    from src.package import base_package as bp
    from src.utils.event import event_thread

    pkg = _AlwaysMiss()
    asset = _asset_image()

    class _MatchThenStop:
        def __init__(self, *a, **k):
            pass

        def match(self, *a, **k):
            event_thread.set()  # 下一轮检查时退出
            return False

    patch_rule.setattr(bp, "RuleImage", _MatchThenStop)
    event_thread.clear()

    with pytest.raises(GUIStopException):
        pkg.check_click(asset, timeout=0, stall_timeout=0)

    event_thread.clear()


def test_timeout_path_is_unaffected_by_stall_guard(patch_rule):
    """有 timeout 时本来就会退出，不应再叠加 stall 判定"""
    from src.package import base_package as bp

    pkg = _AlwaysMiss()

    class _NeverMatch:
        def __init__(self, *a, **k):
            pass

        def match(self, *a, **k):
            return False

    patch_rule.setattr(bp, "RuleImage", _NeverMatch)

    # timeout=0.02 远小于默认 stall，但 timeout 分支先命中，返回 False 而非抛异常
    assert pkg.check_click(_asset_image(), timeout=0.02) is False


def test_invalid_asset_returns_false_instead_of_looping(patch_rule):
    """asset 类型非法时原先会永久空转（两个 isinstance 都不命中）"""

    pkg = _AlwaysMiss()
    assert pkg.check_click(object(), timeout=0, stall_timeout=0.05) is False


def test_str_asset_still_raises_type_error():
    pkg = _AlwaysMiss()
    with pytest.raises(TypeError):
        pkg.check_click("素材")


def test_stop_event_takes_priority_over_stall_guard():
    """用户点停止必须立即生效，不能被 stall 判定抢先"""
    from src.package import base_package as bp
    from src.utils.event import event_thread

    pkg = _AlwaysMiss()
    asset = _asset_image()

    class _NeverMatch:
        def __init__(self, *a, **k):
            pass

        def match(self, *a, **k):
            event_thread.set()
            return False

    bp.RuleImage = _NeverMatch
    event_thread.clear()
    try:
        with pytest.raises(GUIStopException):
            pkg.check_click(asset, timeout=0, stall_timeout=0.02)
    finally:
        event_thread.clear()
        bp.RuleImage = __import__("src.utils.image", fromlist=["RuleImage"]).RuleImage
