"""模拟器分支：BasePackage.confirm 走 OCR 点击「确认」，桌面版保持回车。"""
import src.package.base_package as bp
import src.utils.adapter as ad


class _MumuWin:
    family = "mumu"


class _PcWin:
    family = "pc"


def _make_pkg():
    return object.__new__(bp.BasePackage)


def test_confirm_uses_ocr_on_emulator(monkeypatch):
    pkg = _make_pkg()
    calls = []
    monkeypatch.setattr(bp.window_manager, "current", _MumuWin())
    monkeypatch.setattr(
        bp.BasePackage, "click_confirm", lambda self, timeout=0: calls.append(("ocr", timeout)) or True
    )
    monkeypatch.setattr(ad.KeyBoard, "enter", classmethod(lambda cls, delay=0: calls.append(("enter", delay))))

    assert pkg.confirm(timeout=3) is True
    assert calls == [("ocr", 3)]


def test_confirm_uses_enter_on_pc(monkeypatch):
    pkg = _make_pkg()
    calls = []
    monkeypatch.setattr(bp.window_manager, "current", _PcWin())
    monkeypatch.setattr(ad.KeyBoard, "enter", classmethod(lambda cls, delay=0: calls.append(("enter", delay))))

    pkg.confirm(delay=2)
    assert calls == [("enter", 2)]
