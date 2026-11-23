"""每周秘闻提醒：配置默认值、周判定、忽略、完成记录，以及设置卡片的「重置」按钮。"""

import os
from datetime import date, datetime, timedelta
from types import SimpleNamespace

# offscreen 仅用于本进程创建 QApplication；创建后立刻还原，避免泄漏给子进程
_PLATFORM_KEY = "QT_QPA_PLATFORM"
_prev_platform = os.environ.get(_PLATFORM_KEY)
os.environ[_PLATFORM_KEY] = "offscreen"

import pytest

try:
    qt_widgets = pytest.importorskip("PySide6.QtWidgets")
    QApplication = qt_widgets.QApplication
    _APP = QApplication.instance() or QApplication([])
finally:
    if _prev_platform is None:
        os.environ.pop(_PLATFORM_KEY, None)
    else:
        os.environ[_PLATFORM_KEY] = _prev_platform

from src.package.miwen import MiWen
from src.ui import setting_widget
from src.ui.setting_widget import SettingPackageMiWenReminderCard
from src.utils.config import (
    UserConfig,
    config,
    default_config,
    ignore_miwen_reminder_this_week,
    package_miwen_completed_this_week,
    should_show_miwen_reminder,
)
from src.utils.signals import signal_manager


def _today() -> date:
    return datetime.now().astimezone().date()


@pytest.fixture
def isolated_config(monkeypatch):
    """隔离真实 config.yaml：update 只修改内存中的 UserConfig。"""
    monkeypatch.setattr(config, "user", UserConfig())

    def _update(key: str, value):
        target = config.user
        keys = key.split(".")
        for k in keys[:-1]:
            target = getattr(target, k)
        setattr(target, keys[-1], value)

    monkeypatch.setattr(config, "update", _update)
    return config


def test_default_config_values():
    user = UserConfig()
    assert user.package_miwen_reminder is False
    assert user.package_miwen_completed_date == "1970-01-01"


def test_completed_today_counts_as_this_week(isolated_config):
    config.update("package_miwen_completed_date", _today().isoformat())
    assert package_miwen_completed_this_week() is True


def test_completed_last_week_not_counted(isolated_config):
    last_week = _today() - timedelta(days=7)
    config.update("package_miwen_completed_date", last_week.isoformat())
    assert package_miwen_completed_this_week() is False


def test_default_date_not_counted(isolated_config):
    assert config.user.package_miwen_completed_date == "1970-01-01"
    assert package_miwen_completed_this_week() is False


def test_invalid_date_not_counted(isolated_config):
    config.update("package_miwen_completed_date", "not-a-date")
    assert package_miwen_completed_this_week() is False


def test_reminder_requires_switch_on(isolated_config):
    assert should_show_miwen_reminder() is False

    config.update("package_miwen_reminder", True)
    assert should_show_miwen_reminder() is True


def test_completed_week_suppresses_reminder(isolated_config):
    config.update("package_miwen_reminder", True)
    config.update("package_miwen_completed_date", _today().isoformat())
    assert should_show_miwen_reminder() is False


def test_ignore_records_today_and_suppresses_reminder(isolated_config):
    config.update("package_miwen_reminder", True)
    ignore_miwen_reminder_this_week()

    assert config.user.package_miwen_completed_date == _today().isoformat()
    assert package_miwen_completed_this_week() is True
    assert should_show_miwen_reminder() is False


def test_ignored_last_week_prompts_again(isolated_config):
    config.update("package_miwen_reminder", True)
    config.update("package_miwen_completed_date", (_today() - timedelta(days=7)).isoformat())

    assert package_miwen_completed_this_week() is False
    assert should_show_miwen_reminder() is True


def _make_miwen(n: int, max_n: int = 10) -> MiWen:
    miwen = object.__new__(MiWen)
    miwen.n = n
    miwen.max = max_n
    return miwen


def test_done_records_date_at_ninth_layer(isolated_config):
    config.update("package_miwen_reminder", True)

    miwen = _make_miwen(8)
    miwen.done()

    assert miwen.n == 9
    assert config.user.package_miwen_completed_date == _today().isoformat()


def test_done_records_date_after_ten_layers(isolated_config):
    config.update("package_miwen_reminder", True)

    miwen = _make_miwen(9)
    miwen.done()

    assert miwen.n == 10
    assert config.user.package_miwen_completed_date == _today().isoformat()


def test_done_before_nine_layers_does_not_record(isolated_config):
    config.update("package_miwen_reminder", True)

    miwen = _make_miwen(7)
    miwen.done()

    assert config.user.package_miwen_completed_date == "1970-01-01"


def test_done_does_not_record_when_switch_off(isolated_config):
    miwen = _make_miwen(9)
    miwen.done()

    assert config.user.package_miwen_completed_date == "1970-01-01"


@pytest.fixture
def info_bars():
    """收集 InfoBar 请求，测试结束后断开连接。"""
    bars: list[tuple[str, str, str, int]] = []

    def _on_bar(title: str, content: str, level: str, duration: int):
        bars.append((title, content, level, duration))

    signal_manager.main.info_bar_requested.connect(_on_bar)
    try:
        yield bars
    finally:
        signal_manager.main.info_bar_requested.disconnect(_on_bar)


def test_done_at_ninth_layer_does_not_notify(isolated_config, info_bars):
    config.update("package_miwen_reminder", True)

    _make_miwen(8).done()

    assert info_bars == []


def test_done_at_tenth_layer_notifies_info_bar(isolated_config, info_bars):
    config.update("package_miwen_reminder", True)

    _make_miwen(9).done()

    assert info_bars == [("秘闻提醒", "本周秘闻已完成", "success", 5)]


def test_done_notifies_only_once(isolated_config, info_bars):
    config.update("package_miwen_reminder", True)

    miwen = _make_miwen(8)
    miwen.done()
    miwen.done()

    assert miwen.n == 10
    assert len(info_bars) == 1


_EXPECTED_BAR = ("秘闻提醒", "已重置本周完成记录", "success", 5)


@pytest.fixture
def card_env(monkeypatch):
    """隔离配置写盘，并记录 InfoBar 请求与 update 调用。"""
    monkeypatch.setattr(config, "user", UserConfig())

    writes: list[tuple[str, str]] = []
    monkeypatch.setattr(config, "update", lambda key, value: writes.append((key, value)))

    bars: list[tuple[str, str, str, int]] = []

    def _on_bar(title: str, content: str, level: str, duration: int):
        bars.append((title, content, level, duration))

    signal_manager.main.info_bar_requested.connect(_on_bar)
    try:
        yield SimpleNamespace(writes=writes, bars=bars)
    finally:
        signal_manager.main.info_bar_requested.disconnect(_on_bar)


def test_reset_button_left_of_switch():
    card = SettingPackageMiWenReminderCard()
    reset_index = card.hBoxLayout.indexOf(card.reset_button)
    switch_index = card.hBoxLayout.indexOf(card.switch)
    assert 0 <= reset_index < switch_index


def test_reset_writes_default_and_shows_info_bar(card_env):
    config.user.package_miwen_completed_date = "2026-11-23"
    card = SettingPackageMiWenReminderCard()

    card.reset_button.click()

    assert card_env.writes == [("package_miwen_completed_date", default_config.package_miwen_completed_date)]
    assert card_env.bars == [_EXPECTED_BAR]


def test_reset_when_already_default_skips_write(card_env):
    assert config.user.package_miwen_completed_date == default_config.package_miwen_completed_date
    card = SettingPackageMiWenReminderCard()

    card.reset_button.click()

    assert card_env.writes == []
    assert card_env.bars == [_EXPECTED_BAR]


def test_reset_when_already_default_logs_info(card_env, monkeypatch):
    logs: list[str] = []
    monkeypatch.setattr(setting_widget.logger, "info", lambda msg, *args, **kwargs: logs.append(msg))
    card = SettingPackageMiWenReminderCard()

    card.reset_button.click()

    assert logs == ["秘闻完成日期已是默认值，跳过写入"]
