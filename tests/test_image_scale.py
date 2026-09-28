"""模板按模拟器分辨率缩放 - TDD RED 测试"""

import cv2
import numpy as np


def _make_template(w=65, h=35):
    img = np.full((h, w, 3), 255, dtype=np.uint8)
    cv2.rectangle(img, (2, 2), (w - 3, h - 3), (0, 0, 0), 2)
    cv2.putText(img, "AB", (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    return img


def test_template_scale_factor():
    """1386x780 相对 1136x640 的缩放系数"""
    from src.utils.image import get_template_scale

    fx, fy = get_template_scale(1386, 780)
    assert fx == 1386 / 1136
    assert fy == 780 / 640


def test_scaled_template_matches_scaled_screenshot():
    """1.22 倍截图上，缩放后模板必须比原模板分数高且超过阈值"""
    from src.utils.image import scale_template_image

    template = _make_template()
    fx, fy = 1386 / 1136, 780 / 640

    # 模拟 1.22 倍游戏窗口：模板放大后贴到大图上
    scaled = cv2.resize(template, None, fx=fx, fy=fy, interpolation=cv2.INTER_LINEAR)
    th, tw = scaled.shape[:2]
    screenshot = np.full((780, 1386, 3), 128, dtype=np.uint8)
    screenshot[100 : 100 + th, 200 : 200 + tw] = scaled

    res_raw = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, raw_score, _, _ = cv2.minMaxLoc(res_raw)

    auto_scaled = scale_template_image(template, fx, fy)
    res_scaled = cv2.matchTemplate(screenshot, auto_scaled, cv2.TM_CCOEFF_NORMED)
    _, scaled_score, _, _ = cv2.minMaxLoc(res_scaled)

    assert scaled_score >= 0.9
    assert scaled_score > raw_score


def test_ruleimage_match_uses_scaled_template(tmp_path):
    """RuleImage 在 1386x780 窗口下必须匹配上 1.22 倍截图"""
    from PIL import Image as PILImage

    from src.utils import window as window_module
    from src.utils.image import RuleImage

    template = _make_template()
    template_path = tmp_path / "title.png"
    cv2.imwrite(str(template_path), template)

    fx, fy = 1386 / 1136, 780 / 640
    scaled = cv2.resize(template, None, fx=fx, fy=fy, interpolation=cv2.INTER_LINEAR)
    th, tw = scaled.shape[:2]
    shot_bgr = np.full((780, 1386, 3), 128, dtype=np.uint8)
    shot_bgr[100 : 100 + th, 200 : 200 + tw] = scaled
    shot_rgb = cv2.cvtColor(shot_bgr, cv2.COLOR_BGR2RGB)
    shot_pil = PILImage.fromarray(shot_rgb)

    # 模拟 1386x780 模拟器窗口（family=mumu 才启用模板缩放；content=shot 帧尺寸）
    class _FakeWindow:
        family = "mumu"
        client_width = 1386
        client_height = 780
        content_width = 1386
        content_height = 780

    old = window_module.window_manager.current
    window_module.window_manager.current = _FakeWindow()
    try:
        rule = RuleImage(
            name="title",
            file=str(template_path),
            region=(0, 0, 1136, 640),  # region 按基准空间给
            score=0.7,
        )
        ok = rule.match(image=shot_pil, normal=False, logger_lever="NONE")
    finally:
        window_module.window_manager.current = old

    assert ok is True
    # 识别结果是基准空间坐标：实际像素尺寸要除回系数
    x1, y1, x2, y2 = rule.match_result
    assert abs((x2 - x1) - tw / fx) <= 2
    assert abs((y2 - y1) - th / fy) <= 2


def test_ruleimage_explicit_region_scales_for_mumu():
    """显式 region 是基准空间坐标，搜索时必须按系数放大到实际客户区。"""
    from src.utils import window as window_module
    from src.utils.image import RuleImage

    class _FakeWindow:
        family = "mumu"
        client_width = 1386
        client_height = 780
        content_width = 1386
        content_height = 780

    fx, fy = 1386 / 1136, 780 / 640
    old = window_module.window_manager.current
    window_module.window_manager.current = _FakeWindow()
    try:
        rule = RuleImage(name="title", file="not-exists.png", region=(470, 40, 250, 150), score=0.7)
        assert rule.actual_region() == (
            round(470 * fx),
            round(40 * fy),
            round(250 * fx),
            round(150 * fy),
        )
        # 全窗默认 region 已是实际尺寸，不重复放大
        full = RuleImage(name="title", file="not-exists.png", region=(0, 0, 0, 0), score=0.7)
        assert full.actual_region() == (0, 0, 1386, 780)
    finally:
        window_module.window_manager.current = old


def test_template_scale_uses_shot_content_size_for_mumu():
    """C3: mumu 模板缩放基准必须是 shot(nemudisplay) 客户区，而不是 root 客户区。"""
    from src.utils import window as window_module
    from src.utils.image import get_template_scale

    class _FakeMumu:
        family = "mumu"
        client_width = 1084
        client_height = 650  # root 客户区（含播放器工具条）
        content_width = 1084
        content_height = 610  # shot 客户区 = 实际帧尺寸

    old = window_module.window_manager.current
    window_module.window_manager.current = _FakeMumu()
    try:
        fx, fy = get_template_scale()
    finally:
        window_module.window_manager.current = old

    assert fx == 1084 / 1136
    assert fy == 610 / 640  # 用 shot，而不是 650/640


def test_template_scale_disabled_for_pc():
    """决策：模板缩放仅 mumu 生效，PC 保持原有裸匹配（非 1136x640 也不缩放）。"""
    from src.utils import window as window_module
    from src.utils.image import get_template_scale

    class _FakePC:
        family = "pc"
        client_width = 1152
        client_height = 679

    old = window_module.window_manager.current
    window_module.window_manager.current = _FakePC()
    try:
        assert get_template_scale() == (1.0, 1.0)
    finally:
        window_module.window_manager.current = old
