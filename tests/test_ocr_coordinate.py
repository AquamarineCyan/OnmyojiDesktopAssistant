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
    from src.utils.rapidocr import OcrData

    monkeypatch.setattr(window_module.window_manager, "current", _MumuWin())
    fx, fy = 1393 / 1136, 784 / 640

    data = OcrData(_item(100, 200, 180, 230))
    data.to_reference()

    assert data.center.client_x == int(140 / fx)
    assert data.center.client_y == int(215 / fy)
    assert data.rect.x1 == 100 / fx
    assert data.rect.y2 == 230 / fy


def test_ocr_result_identity_for_pc(monkeypatch):
    from src.utils.rapidocr import OcrData

    monkeypatch.setattr(window_module.window_manager, "current", _PcWin())

    data = OcrData(_item(100, 200, 180, 230))
    data.to_reference()

    assert data.center.client_x == 140
    assert data.center.client_y == 215


def test_ocr_region_scaled_for_mumu(monkeypatch):
    """显式 OCR region 是基准空间坐标，检测区域要放大到实际客户区。"""
    from src.utils.rapidocr import RuleOcr

    monkeypatch.setattr(window_module.window_manager, "current", _MumuWin())
    fx, fy = 1393 / 1136, 784 / 640

    rule = RuleOcr(keyword="确认", region=(40, 600, 940, 35))

    assert rule.region == (round(40 * fx), round(600 * fy), round(940 * fx), round(35 * fy))
