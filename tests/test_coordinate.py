"""坐标空间换算：基准空间 1136x640 ↔ 实际客户区。

约定：业务代码（region / Point 常量 / OCR 结果）一律用基准空间，
只有截图、识别、鼠标注入使用实际客户区空间，换算集中在 coordinate 模块。
"""
import pytest

from src.utils import window as window_module


class _MumuWin:
    family = "mumu"
    client_width = 1393
    client_height = 784
    content_width = 1393
    content_height = 784


class _PcWin:
    family = "pc"
    client_width = 1136
    client_height = 640


@pytest.fixture
def mumu(monkeypatch):
    monkeypatch.setattr(window_module.window_manager, "current", _MumuWin())


@pytest.fixture
def pc(monkeypatch):
    monkeypatch.setattr(window_module.window_manager, "current", _PcWin())


@pytest.fixture
def none_window(monkeypatch):
    monkeypatch.setattr(window_module.window_manager, "current", None)


def test_scale_for_mumu(mumu):
    from src.utils.coordinate import get_scale

    fx, fy = get_scale()
    assert fx == 1393 / 1136
    assert fy == 784 / 640


def test_scale_identity_for_pc(pc):
    from src.utils.coordinate import get_scale

    assert get_scale() == (1.0, 1.0)


def test_scale_identity_without_window(none_window):
    from src.utils.coordinate import get_scale

    assert get_scale() == (1.0, 1.0)


def test_conversions_are_identity_for_pc(pc):
    from src.utils.coordinate import scale_region, to_actual, to_reference

    assert to_actual(100, 200) == (100, 200)
    assert to_reference(100, 200) == (100, 200)
    assert scale_region((10, 20, 30, 40)) == (10, 20, 30, 40)


def test_conversions_for_mumu(mumu):
    from src.utils.coordinate import scale_region, to_actual, to_reference

    fx, fy = 1393 / 1136, 784 / 640
    assert to_actual(100, 200) == (100 * fx, 200 * fy)
    assert to_reference(100 * fx, 200 * fy) == pytest.approx((100, 200))

    x, y, w, h = scale_region((470, 40, 250, 150))
    assert (x, y, w, h) == (round(470 * fx), round(40 * fy), round(250 * fx), round(150 * fy))


def test_reference_size_is_standard(pc):
    from src.utils.coordinate import reference_size

    assert reference_size() == (1136, 640)
