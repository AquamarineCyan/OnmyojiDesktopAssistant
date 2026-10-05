"""C1 回归：旧版本配置缺少新增标量字段时，_check_outdated → UserConfig 不得崩溃。

旧配置典型形态：interaction_mode 子树里某个候选值缺失/越界（如更早版本无
screenshot_method），同时缺少本分支新增的 mumu_folder/ipc_dll_override。
修复前 _check_outdated 会把缺失标量写成 None，UserConfig(**data) 抛 ValidationError。
"""

import pytest
import yaml

from src.utils.config import Config


def _write(monkeypatch, tmp_path, data: dict) -> Config:
    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    monkeypatch.setattr(Config, "config_path", p)
    try:
        return Config()
    except Exception as e:  # 修复前在此失败（启动崩溃路径）
        pytest.fail(f"legacy config load raised: {e!r}")


def test_legacy_config_with_missing_scalar_fields_loads(tmp_path, monkeypatch):
    legacy = {
        "interaction_mode": {
            "mode": "前台",
            "frontend": {"force_window": True},
            "backend": {
                "prevent_sleep": True,
                # screenshot_method 缺失 → 触发子树整改
                # mumu_folder / ipc_dll_override 缺失（本分支新增）
            },
        },
    }
    cfg = _write(monkeypatch, tmp_path, legacy)

    backend = cfg.user.interaction_mode.backend
    assert backend.screenshot_method == "BitBlt"
    assert backend.prevent_sleep is True
    assert backend.mumu_folder == ""
    assert backend.ipc_dll_override == ""


def test_legacy_config_with_invalid_candidate_loads(tmp_path, monkeypatch):
    """候选值越界同样触发子树整改，缺失标量不得被写成 None。"""
    legacy = {
        "interaction_mode": {
            "mode": "后台",
            "backend": {"screenshot_method": "NotAMethod"},
        },
    }
    cfg = _write(monkeypatch, tmp_path, legacy)

    backend = cfg.user.interaction_mode.backend
    assert backend.screenshot_method == "BitBlt"
    assert backend.mumu_folder == ""
    assert backend.ipc_dll_override == ""


def test_legacy_config_with_explicit_null_scalars_loads(tmp_path, monkeypatch):
    """YAML 显式留空的键（`mumu_folder:`）解析为 None，必须回落默认值而非打崩 UserConfig。"""
    legacy = {
        "interaction_mode": {
            "backend": {"enable_mumu": None, "mumu_folder": None},
        },
    }
    cfg = _write(monkeypatch, tmp_path, legacy)

    backend = cfg.user.interaction_mode.backend
    assert backend.enable_mumu is False
    assert backend.mumu_folder == ""
