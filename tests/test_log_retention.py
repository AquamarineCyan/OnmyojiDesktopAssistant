"""日志保留策略

两条规则：超过保留天数的轮转日志删除；目录总量超上限时从最旧开始删；
轮转日志删完仍超限（当日日志本身就过大）则截断当前日志保留尾部。
当前正在写入的日志永远不被前两条规则删除。
"""
import os
import time
from pathlib import Path

import pytest

from src.utils import log as log_module

APP = "OnmyojiDesktopAssistant"


def _mk(path: Path, size: int, age_days: float = 0.0) -> Path:
    path.write_bytes(b"x" * size)
    if age_days:
        t = time.time() - age_days * 86400
        os.utime(path, (t, t))
    return path


@pytest.fixture
def log_dir(tmp_path, monkeypatch):
    d = tmp_path / "log"
    d.mkdir()
    monkeypatch.setattr(log_module, "LOG_DIR_PATH", d)
    return d


def test_removes_expired_rotated_logs(log_dir):
    _mk(log_dir / f"{APP}.log.2026-01-01", 100, age_days=30)
    _mk(log_dir / f"{APP}.log.2026-01-02", 100, age_days=1)
    active = _mk(log_dir / f"{APP}.log", 100)

    log_module.cleanup_logs(retention_days=7, max_size_mb=0)

    assert not (log_dir / f"{APP}.log.2026-01-01").exists()
    assert (log_dir / f"{APP}.log.2026-01-02").exists()
    assert active.exists(), "当前日志不能被时间规则删掉"


def test_never_removes_active_log_by_age(log_dir):
    active = _mk(log_dir / f"{APP}.log", 100, age_days=999)
    log_module.cleanup_logs(retention_days=7, max_size_mb=0)
    assert active.exists()


def test_retention_zero_disables_time_rule(log_dir):
    old = _mk(log_dir / f"{APP}.log.old", 100, age_days=365)
    log_module.cleanup_logs(retention_days=0, max_size_mb=0)
    assert old.exists()


def test_size_cap_deletes_oldest_first(log_dir):
    kb = 1024
    old = _mk(log_dir / f"{APP}.log.a", 400 * kb, age_days=5)
    mid = _mk(log_dir / f"{APP}.log.b", 400 * kb, age_days=4)
    new = _mk(log_dir / f"{APP}.log.c", 400 * kb, age_days=3)
    active = _mk(log_dir / f"{APP}.log", 400 * kb)

    # 总量 1600KB，上限 1MB(1024KB) → 删最旧两个(800KB)后剩 800KB，刚好达标
    log_module.cleanup_logs(retention_days=0, max_size_mb=1)
    total = sum(f.stat().st_size for f in log_dir.iterdir())

    assert total <= 1024 * kb, f"总量仍超限: {total}"
    assert active.exists(), "当前日志不参与删除"
    assert new.exists(), "最新的轮转日志应该被保留"
    assert not old.exists(), "最旧的轮转日志应该先被删"
    assert not mid.exists(), "次旧的也应该被删"


def test_size_cap_keeps_enough_just_under_budget(log_dir):
    kb = 1024
    old = _mk(log_dir / f"{APP}.log.a", 500 * kb, age_days=5)
    new = _mk(log_dir / f"{APP}.log.b", 400 * kb, age_days=4)
    _mk(log_dir / f"{APP}.log", 400 * kb)

    # 总量 1300KB，上限 1000KB → 只需删最旧的 500KB
    log_module.cleanup_logs(retention_days=0, max_size_mb=1)

    assert not old.exists()
    assert new.exists()


def test_size_cap_zero_disables_size_rule(log_dir):
    big = _mk(log_dir / f"{APP}.log.big", 5 * 1024 * 1024)
    log_module.cleanup_logs(retention_days=0, max_size_mb=0)
    assert big.exists()


def test_truncates_active_when_no_rotated_left(log_dir):
    """轮转日志删完仍超限 → 当日日志本身过大，截断保留尾部"""
    active = _mk(log_dir / f"{APP}.log", 4 * 1024 * 1024)
    active.write_bytes(b"HEADMARK" + b"y" * (4 * 1024 * 1024) + b"TAILMARK")

    log_module.cleanup_logs(retention_days=0, max_size_mb=1)

    data = active.read_bytes()
    assert len(data) <= 1024 * 1024, f"截断后仍超限: {len(data)}"
    assert data.endswith(b"TAILMARK"), "必须保留尾部，否则丢掉的是最新日志"
    assert b"HEADMARK" not in data, "应丢弃头部"
    assert b"earlier content trimmed" in data[:200]


def test_under_limit_changes_nothing(log_dir):
    files = [_mk(log_dir / f"{APP}.log.{i}", 10, age_days=i) for i in range(5)]
    _mk(log_dir / f"{APP}.log", 10)
    before = sorted(f.name for f in log_dir.iterdir())

    log_module.cleanup_logs(retention_days=7, max_size_mb=100)

    assert sorted(f.name for f in log_dir.iterdir()) == before
    assert all(f.exists() for f in files)


def test_ignores_unrelated_files(log_dir):
    other = _mk(log_dir / "其他程序.log", 10 * 1024 * 1024, age_days=999)
    _mk(log_dir / f"{APP}.log", 10)

    log_module.cleanup_logs(retention_days=1, max_size_mb=1)

    assert other.exists(), "只应清理本程序的日志"


def test_missing_log_dir_is_tolerated(tmp_path, monkeypatch):
    monkeypatch.setattr(log_module, "LOG_DIR_PATH", tmp_path / "nope")
    log_module.cleanup_logs()  # 不能抛异常


def test_config_exposes_retention_defaults():
    from src.utils.config import UserConfig

    u = UserConfig()
    assert u.log_retention_days == 7
    assert u.log_max_size_mb == 100
