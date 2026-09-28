"""坐标空间换算：基准空间（1136x640） ↔ 实际客户区空间。

约定：
- 业务代码里出现的一切坐标（`AssetImage/AssetOcr.region`、`Point` 常量、随机点击范围）
  都是「基准空间」坐标；
- 截图、图像识别、OCR、鼠标注入使用窗口「实际客户区空间」；
- 两个空间只在**共享边界**换算，业务代码不要自己乘系数：
  - `RuleImage` / `RuleOcr`：region 基准→实际，识别结果 实际→基准
  - `Mouse.click/move/drag`：基准→实际；`Mouse.position`：实际→基准

桌面版：实际客户区即基准空间，全部换算为恒等（系数 1.0）。
模拟器：实际客户区 = MuMu 显示帧尺寸（窗口可自由缩放），系数 = 实际 / 1136x640。
"""

from __future__ import annotations

STANDARD_CLIENT_WIDTH = 1136
"""基准空间宽度"""

STANDARD_CLIENT_HEIGHT = 640
"""基准空间高度"""


def get_scale() -> tuple[float, float]:
    """(fx, fy)：基准空间 → 实际客户区。

    无窗口或桌面版（非 mumu）返回 (1.0, 1.0)，即两个空间重合。
    """
    from .window import window_manager

    try:
        cur = window_manager.current
        if cur is None or getattr(cur, "family", "pc") != "mumu":
            return (1.0, 1.0)
        w = getattr(cur, "content_width", 0) or cur.client_width
        h = getattr(cur, "content_height", 0) or cur.client_height
    except Exception:
        return (1.0, 1.0)
    if not w or not h:
        return (1.0, 1.0)
    return (w / STANDARD_CLIENT_WIDTH, h / STANDARD_CLIENT_HEIGHT)


def is_scaled() -> bool:
    """当前是否需要换算（模拟器且窗口不是 1136x640）"""
    fx, fy = get_scale()
    return abs(fx - 1.0) >= 0.01 or abs(fy - 1.0) >= 0.01


def to_actual(x: float, y: float) -> tuple[float, float]:
    """基准坐标 → 实际客户区坐标"""
    fx, fy = get_scale()
    return (x * fx, y * fy)


def to_reference(x: float, y: float) -> tuple[float, float]:
    """实际客户区坐标 → 基准坐标"""
    fx, fy = get_scale()
    return (x / fx, y / fy)


def scale_region(region: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """基准空间 region (x, y, w, h) → 实际客户区 region"""
    fx, fy = get_scale()
    if abs(fx - 1.0) < 0.01 and abs(fy - 1.0) < 0.01:
        return tuple(region)
    x, y, w, h = region
    return (
        int(round(x * fx)),
        int(round(y * fy)),
        int(round(w * fx)),
        int(round(h * fy)),
    )


def reference_size() -> tuple[int, int]:
    """基准空间的窗口尺寸（业务代码里做“屏幕范围”随机时应使用它）"""
    return (STANDARD_CLIENT_WIDTH, STANDARD_CLIENT_HEIGHT)
