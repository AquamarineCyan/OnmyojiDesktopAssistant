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


def test_ocr_result_point_order_clockwise(monkeypatch):
    """RapidOCR 的 box 是 [左上, 右上, 右下, 左下]，取 [0]/[2] 才是对角点。

    旋转的四边形同样成立：对角线中点就是矩形中心。
    """
    from src.utils.rapidocr import OcrData

    monkeypatch.setattr(window_module.window_manager, "current", _PcWin())

    # 倾斜文本框（顺时针四点），不是轴对齐矩形
    item = {
        "Text": "确认",
        "Score": 0.9,
        "BoxPoints": [
            {"X": 100, "Y": 200},
            {"X": 140, "Y": 190},
            {"X": 150, "Y": 230},
            {"X": 110, "Y": 240},
        ],
    }
    data = OcrData(item)

    assert (data.x1, data.y1) == (100, 200)
    assert (data.x2, data.y2) == (150, 230)
    # 中心 = 对角线中点
    assert data.center.client_x == 125
    assert data.center.client_y == 215


def test_ocr_detector_adds_region_origin(monkeypatch):
    """截图按 region 裁剪，OCR 返回的是 region 局部坐标，必须加回原点。

    否则带 region 的素材点击位置会整体偏到窗口左上角。
    """
    from src.utils import rapidocr as rapidocr_module

    monkeypatch.setattr(window_module.window_manager, "current", _PcWin())

    region = (360, 600, 100, 50)

    class _FakeScreenshot:
        is_valid = True

        def get_array(self):
            return None

        def get_image(self):  # pragma: no cover - SAVE_SCREENSHOT 为 False
            return None

    monkeypatch.setattr(rapidocr_module, "ScreenShot", lambda rect: _FakeScreenshot())
    monkeypatch.setattr(rapidocr_module.ocr_manager, "is_initialized", lambda: True)
    # RapidOCR 在裁剪后的 100x50 图里返回 (10, 5, 60, 25)
    monkeypatch.setattr(
        rapidocr_module.ocr_manager,
        "detect",
        lambda img: [
            {
                "Text": "十连召唤",
                "Score": 0.95,
                "BoxPoints": [
                    {"X": 10, "Y": 5},
                    {"X": 60, "Y": 5},
                    {"X": 60, "Y": 25},
                    {"X": 10, "Y": 25},
                ],
            }
        ],
    )

    detector = rapidocr_module.OcrDetector(region)
    result = detector.get_raw_result()

    assert len(result) == 1
    data = result[0]
    # 局部 (10, 5) + region 原点 (360, 600) = (370, 605)
    assert data.x1 == 370
    assert data.y1 == 605
    assert data.center.client_x == 395
    assert data.center.client_y == 615


def test_ocr_detector_zero_region_no_offset(monkeypatch):
    """region 为 (0, 0, 0, 0) 时不应产生额外偏移。"""
    from src.utils import rapidocr as rapidocr_module

    monkeypatch.setattr(window_module.window_manager, "current", _PcWin())

    class _FakeScreenshot:
        is_valid = True

        def get_array(self):
            return None

    monkeypatch.setattr(rapidocr_module, "ScreenShot", lambda rect: _FakeScreenshot())
    monkeypatch.setattr(rapidocr_module.ocr_manager, "is_initialized", lambda: True)
    monkeypatch.setattr(
        rapidocr_module.ocr_manager,
        "detect",
        lambda img: [
            {
                "Text": "确定",
                "Score": 0.95,
                "BoxPoints": [
                    {"X": 100, "Y": 200},
                    {"X": 180, "Y": 200},
                    {"X": 180, "Y": 230},
                    {"X": 100, "Y": 230},
                ],
            }
        ],
    )

    detector = rapidocr_module.OcrDetector((0, 0, 0, 0))
    data = detector.get_raw_result()[0]

    assert data.x1 == 100
    assert data.center.client_x == 140


def test_ocr_detector_returns_empty_when_screenshot_failed(monkeypatch):
    """截图失败不能把 None 喂给 OCR，要给出明确结果。"""
    from src.utils import rapidocr as rapidocr_module

    monkeypatch.setattr(window_module.window_manager, "current", _PcWin())

    class _FailedScreenshot:
        is_valid = False

        def get_array(self):  # pragma: no cover - 不应被调用
            raise AssertionError("截图失败时不应调用 get_array")

    monkeypatch.setattr(rapidocr_module, "ScreenShot", lambda rect: _FailedScreenshot())
    monkeypatch.setattr(rapidocr_module.ocr_manager, "is_initialized", lambda: True)

    assert rapidocr_module.OcrDetector((0, 0, 100, 100)).get_raw_result() == []
