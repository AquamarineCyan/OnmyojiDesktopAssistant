"""OCR 结果统一换算回基准空间（1136x640）。"""

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


class _MumuFrameWin:
    """模拟器：客户区含播放器工具条，内容帧才是真实截图尺寸。"""

    family = "mumu"
    client_width = 1456
    client_height = 840
    content_width = 1393
    content_height = 784


def _item(x1, y1, x2, y2, text="确认"):
    return {
        "Text": text,
        "Score": 0.9,
        "BoxPoints": [
            {"X": x1, "Y": y1},
            {"X": x2, "Y": y1},
            {"X": x2, "Y": y2},
            {"X": x1, "Y": y2},
        ],
    }


def test_ocr_result_scaled_back_to_reference(monkeypatch):
    from src.utils.ocr_engine import OcrData

    monkeypatch.setattr(window_module.window_manager, "current", _MumuWin())
    fx, fy = 1393 / 1136, 784 / 640

    data = OcrData(_item(100, 200, 180, 230))
    data.to_reference()

    assert data.center.client_x == int(140 / fx)
    assert data.center.client_y == int(215 / fy)
    assert data.rect.x1 == 100 / fx
    assert data.rect.y2 == 230 / fy


def test_ocr_result_identity_for_pc(monkeypatch):
    from src.utils.ocr_engine import OcrData

    monkeypatch.setattr(window_module.window_manager, "current", _PcWin())

    data = OcrData(_item(100, 200, 180, 230))
    data.to_reference()

    assert data.center.client_x == 140
    assert data.center.client_y == 215


def test_ocr_region_scaled_for_mumu(monkeypatch):
    """显式 OCR region 是基准空间坐标，检测区域要放大到实际客户区。"""
    from src.utils.ocr_engine import RuleOcr

    monkeypatch.setattr(window_module.window_manager, "current", _MumuWin())
    fx, fy = 1393 / 1136, 784 / 640

    rule = RuleOcr(keyword="确认", region=(40, 600, 940, 35))

    assert rule.region == (round(40 * fx), round(600 * fy), round(940 * fx), round(35 * fy))


def test_ocr_region_clamped_to_window_width(monkeypatch):
    """x1+宽度超过窗口：宽度收到窗口右边界，不留黑边。"""
    from src.utils.ocr_engine import RuleOcr

    monkeypatch.setattr(window_module.window_manager, "current", _PcWin())

    rule = RuleOcr(keyword="确认", region=(900, 0, 940, 640))

    assert rule.region == (900, 0, 236, 640)


def test_ocr_region_clamped_to_window_height(monkeypatch):
    """y1+高度超过窗口：高度收到窗口下边界。"""
    from src.utils.ocr_engine import RuleOcr

    monkeypatch.setattr(window_module.window_manager, "current", _PcWin())

    rule = RuleOcr(keyword="确认", region=(40, 600, 940, 200))

    assert rule.region == (40, 600, 940, 40)


def test_ocr_region_negative_origin_clamped(monkeypatch):
    """负的原点收到 (0, 0)，宽高保持不变（区域整体平移进窗口）。"""
    from src.utils.ocr_engine import RuleOcr

    monkeypatch.setattr(window_module.window_manager, "current", _PcWin())

    rule = RuleOcr(keyword="确认", region=(-50, -20, 100, 100))

    assert rule.region == (0, 0, 100, 100)


def test_ocr_region_fully_outside_falls_back(monkeypatch):
    """区域整体落在窗口外：回退为整窗识别，避免空截图。"""
    from src.utils.ocr_engine import RuleOcr

    monkeypatch.setattr(window_module.window_manager, "current", _PcWin())

    rule = RuleOcr(keyword="确认", region=(1136, 0, 100, 100))

    assert rule.region == (0, 0, 1136, 640)


def test_ocr_region_untouched_without_window(monkeypatch):
    """窗口未就绪时不做边界处理，原样交给截图层。"""
    from src.utils.ocr_engine import RuleOcr

    monkeypatch.setattr(window_module.window_manager, "current", None)

    rule = RuleOcr(keyword="确认", region=(900, 0, 940, 640))

    assert rule.region == (900, 0, 940, 640)


def test_ocr_region_clamped_by_mumu_content_size(monkeypatch):
    """模拟器按内容帧尺寸收敛（不含播放器工具条）。"""
    from src.utils.ocr_engine import RuleOcr

    monkeypatch.setattr(window_module.window_manager, "current", _MumuFrameWin())

    rule = RuleOcr(keyword="确认", region=(100, 0, 1136, 640))

    x, y, w, h = rule.region
    assert x == round(100 * 1393 / 1136)
    assert (y, h) == (0, 784)
    assert w == 1393 - x  # 右边界贴住内容帧，而不是 1456 的客户区
