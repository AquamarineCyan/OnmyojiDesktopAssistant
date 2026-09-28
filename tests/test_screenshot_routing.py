"""Task 8: family=mumu 时后台截图走 MumuBackend，pc 走原路径。"""
import numpy as np

from src.utils.screenshot import ScreenShot


def test_mumu_routes_to_backend(monkeypatch):
    import src.utils.screenshot as ss
    import src.utils.emulator as E

    backend = _FakeBackend()
    monkeypatch.setattr(E, "get_backend", lambda *a, **k: backend)
    monkeypatch.setattr(ss.config.user.interaction_mode, "mode",
                        ss.InteractionMode.BACKEND)

    class _Win:
        family = "mumu"
        handle = 100
        instance_index = 1
        client_rect = (0, 0, 700, 400)

    monkeypatch.setattr(ss.window_manager, "current", _Win())
    # is_alive 是只读 property（无 setter），不能对实例 setattr，改打 class 级
    monkeypatch.setattr(type(ss.window_manager), "is_alive", True)

    shot = ScreenShot(_log=False)
    img = shot.get_image()
    assert img is not None and img.size == (700, 400)
    assert backend.captured


def _pattern_frame(h=400, w=700):
    """带标签的全帧：像素值随 (x, y) 变化，三通道相同（BGR→RGB 恒等，便于断言）。"""
    ys, xs = np.indices((h, w))
    return ((xs + ys * 7) % 256).astype(np.uint8)[..., None].repeat(3, axis=2)


def _patch_mumu_env(monkeypatch, backend, win):
    import src.utils.screenshot as ss
    import src.utils.emulator as E
    monkeypatch.setattr(E, "get_backend", lambda *a, **k: backend)
    monkeypatch.setattr(ss.config.user.interaction_mode, "mode",
                        ss.InteractionMode.BACKEND)
    monkeypatch.setattr(ss.window_manager, "current", win)
    # is_alive 是只读 property（无 setter），不能对实例 setattr，改打 class 级
    monkeypatch.setattr(type(ss.window_manager), "is_alive", True)


def test_mumu_screenshot_crops_to_rect(monkeypatch):
    """Crit #1: mumu 路径返回帧必须裁剪到 rect（否则 match 坐标双重偏移/OCR 全窗）。"""
    backend = _FakeBackend(_pattern_frame())
    _patch_mumu_env(monkeypatch, backend, _Win())
    shot = ScreenShot(rect=(10, 20, 100, 80), _log=False)
    img = shot.get_image()
    frame = backend.captured_frame
    assert img.size == (100, 80)
    # 像素内容 == 全帧的 (l,t,w,h) 子矩形
    assert np.array_equal(np.asarray(img), frame[20:100, 10:110])


def test_mumu_screenshot_full_rect_passthrough(monkeypatch):
    """Crit #1: rect == 全帧时必须原样通过（不得二次裁剪/缩放）。"""
    backend = _FakeBackend(_pattern_frame())
    _patch_mumu_env(monkeypatch, backend, _Win())
    shot = ScreenShot(rect=(0, 0, 700, 400), _log=False)
    img = shot.get_image()
    frame = backend.captured_frame
    assert img.size == (700, 400)
    assert np.array_equal(np.asarray(img), frame)


def test_mumu_screenshot_clips_rect_to_frame_bounds(monkeypatch):
    """Crit #1: 越界 rect 裁剪到帧边界（镜像 _screenshot_backend 的裁剪语义）。"""
    backend = _FakeBackend(_pattern_frame())
    _patch_mumu_env(monkeypatch, backend, _Win())
    shot = ScreenShot(rect=(650, 350, 200, 200), _log=False)
    img = shot.get_image()
    frame = backend.captured_frame
    assert img.size == (50, 50)  # 700-650=50, 400-350=50
    assert np.array_equal(np.asarray(img), frame[350:400, 650:700])


class _Win:
    family = "mumu"
    handle = 100
    instance_index = 1
    client_rect = (0, 0, 700, 400)


class _FakeBackend:
    def __init__(self, frame=None):
        self.captured = False
        self.captured_frame = None
        self._frame = frame if frame is not None else np.full((400, 700, 3), 80, np.uint8)

    def screenshot(self):
        self.captured = True
        self.captured_frame = self._frame
        return self.captured_frame  # BGR