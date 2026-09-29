"""设置页「MuMu 安装目录」行：显隐联动 / 两行布局 / 选择目录（offscreen Qt）。

回归背景（2026-09-28 决策）：
- 目录行位于「启用 MuMu 模拟器支持」开关下方，仅开关开启时显示；关闭时整行移除
  （含分隔线，卡片高度收拢），已填路径保留。
- 单行排布会让本行最小宽度超出设置页默认窗口宽度而被裁切，故改为两行
  （路径独占一行、按钮另起一行），并把 GroupWidget 最小高度抬到实际高度。
"""
import os

# offscreen 仅用于本进程创建 QApplication；创建后立刻还原，避免泄漏给子进程：
# 测试会真实调用 mumu-cli.exe（MuMu 自带 Qt 程序），继承 Qt 环境变量会让它
# 找不到 offscreen 插件而弹「no Qt platform plugin could be initialized」并卡住。
_PLATFORM_KEY = "QT_QPA_PLATFORM"
_prev_platform = os.environ.get(_PLATFORM_KEY)
os.environ[_PLATFORM_KEY] = "offscreen"

import pytest

try:
    qt_widgets = pytest.importorskip("PySide6.QtWidgets")
    QApplication = qt_widgets.QApplication
    QFileDialog = qt_widgets.QFileDialog
    _APP = QApplication.instance() or QApplication([])
finally:
    # 无论成功失败都还原（QApplication 的平台在构造时已选定，不受影响）
    if _prev_platform is None:
        os.environ.pop(_PLATFORM_KEY, None)
    else:
        os.environ[_PLATFORM_KEY] = _prev_platform

from PySide6.QtTest import QTest

from src.ui.setting_widget import SettingInteractionModeCard
from src.utils.config import InteractionMode, config


@pytest.fixture
def card(monkeypatch):
    monkeypatch.setattr(config, "update", lambda *a, **k: None)
    monkeypatch.setattr(config.user.interaction_mode.backend, "enable_mumu", True)
    c = SettingInteractionModeCard()
    c.mode_combobox.setCurrentText(InteractionMode.BACKEND)  # 前台模式后台控件整体禁用
    c.show()
    c.setExpand(True)
    QTest.qWait(350)  # 等展开动画结算
    yield c
    c.deleteLater()


def test_folder_row_follows_enable_switch(card):
    grp = card.backend_mumu_folder_group
    assert not grp.isHidden() and grp in card.widgets and card.widgets[-1] is grp
    h_on = card.height()

    card.backend_enable_mumu_switch.setChecked(False)
    QTest.qWait(50)
    assert grp.isHidden() and grp not in card.widgets
    assert card.height() < h_on

    card.backend_enable_mumu_switch.setChecked(True)
    QTest.qWait(50)
    assert not grp.isHidden() and grp in card.widgets and card.widgets[-1] is grp
    assert card.height() == h_on


def test_folder_row_initially_hidden_when_disabled(monkeypatch):
    monkeypatch.setattr(config, "update", lambda *a, **k: None)
    monkeypatch.setattr(config.user.interaction_mode.backend, "enable_mumu", False)
    c = SettingInteractionModeCard()
    c.show()
    c.setExpand(True)
    QTest.qWait(350)

    grp = c.backend_mumu_folder_group
    assert grp.isHidden() and grp not in c.widgets

    c.backend_enable_mumu_switch.setChecked(True)
    QTest.qWait(50)
    assert not grp.isHidden() and grp in c.widgets and c.widgets[-1] is grp
    c.deleteLater()


def test_folder_row_two_line_layout_not_squeezed(card):
    grp = card.backend_mumu_folder_group
    box = card.backend_mumu_box
    assert grp.minimumHeight() >= grp.sizeHint().height() >= 90
    assert box.height() == box.sizeHint().height() >= 60  # 第二行按钮未被压扁
    bottom = card.backend_browse_button.mapTo(grp, card.backend_browse_button.rect().bottomLeft()).y()
    assert bottom <= grp.height()


def test_browse_button_saves_picked_folder(card, tmp_path, monkeypatch):
    root = tmp_path / "MuMuPlayer"
    (root / "nx_main").mkdir(parents=True)
    (root / "nx_main" / "mumu-cli.exe").write_bytes(b"")
    saved = []
    monkeypatch.setattr(config, "update", lambda path, value: saved.append((path, value)))
    monkeypatch.setattr(
        QFileDialog, "getExistingDirectory",
        staticmethod(lambda *a, **k: str(root).replace("\\", "/")),
    )

    card.backend_browse_button.click()

    expected = os.path.normpath(str(root))
    assert card.backend_mumu_folder_edit.text() == expected
    assert saved[-1] == ("interaction_mode.backend.mumu_folder", expected)


def test_browse_cancel_keeps_value(card, monkeypatch):
    before = card.backend_mumu_folder_edit.text()
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: ""))
    card.backend_browse_button.click()
    assert card.backend_mumu_folder_edit.text() == before


def test_backend_row_disabled_in_frontend_mode(card):
    """前台模式下 MuMu 目录行与其它后台项一样禁用（不再可交互）。"""
    card.mode_combobox.setCurrentText(InteractionMode.BACKEND)
    assert card.backend_mumu_folder_edit.isEnabled()
    assert card.backend_browse_button.isEnabled()
    assert card.backend_detect_button.isEnabled()

    card.mode_combobox.setCurrentText(InteractionMode.FRONTEND)
    assert not card.backend_enable_mumu_switch.isEnabled()
    assert not card.backend_mumu_folder_edit.isEnabled()
    assert not card.backend_browse_button.isEnabled()
    assert not card.backend_detect_button.isEnabled()
