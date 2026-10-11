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


def test_size_cap_truncates_oldest_rotated_log(log_dir):
    """超限时截断最旧的轮转日志（保留尾部），而不是删除它"""
    kb = 1024
    old = _mk(log_dir / f"{APP}.log.a", 900 * kb, age_days=5)
    new = _mk(log_dir / f"{APP}.log.b", 400 * kb, age_days=4)
    active = _mk(log_dir / f"{APP}.log", 400 * kb)

    # 总量 1700KB，上限 1MB → 需释放约 700KB，全部由最旧的 a 承担
    log_module.cleanup_logs(retention_days=0, max_size_mb=1)

    assert old.exists(), "最旧的轮转日志应被截断保留，而不是直接删除"
    assert new.exists(), "更新的轮转日志不应被动"
    assert active.exists(), "当日日志不应被动"
    assert old.stat().st_size < 900 * kb, "应被截断"
    assert old.stat().st_size >= kb, "不该被砍到只剩零头"
    total = sum(f.stat().st_size for f in log_dir.iterdir())
    assert total <= 1024 * kb, f"总量仍超限: {total}"


def test_size_cap_truncation_keeps_tail(log_dir):
    """截断必须保留尾部（最新的内容），丢的是头部"""
    kb = 1024
    old = _mk(log_dir / f"{APP}.log.old", 900 * kb, age_days=5)
    old.write_bytes(b"HEADMARK" + b"m" * (900 * 1024) + b"TAILMARK")
    _mk(log_dir / f"{APP}.log", 400 * kb)

    log_module.cleanup_logs(retention_days=0, max_size_mb=1)

    data = old.read_bytes()
    assert old.stat().st_size < 900 * kb, "应被截断"
    assert data.endswith(b"TAILMARK"), "必须保留尾部"
    assert b"HEADMARK" not in data, "应丢弃头部"
    assert b"earlier content trimmed" in data[:200]


def test_size_cap_never_touches_active_log(log_dir):
    """当日日志既不会被删除，也不会被截断 —— 它是排障时唯一有用的那份"""
    active = _mk(log_dir / f"{APP}.log", 4 * 1024 * 1024)
    before = active.read_bytes()
    for i in range(5):
        _mk(log_dir / f"{APP}.log.{i}", 900 * 1024, age_days=9 - i)

    log_module.cleanup_logs(retention_days=0, max_size_mb=1)

    assert active.exists()
    assert active.read_bytes() == before, "当日日志内容不得被改动"


def test_size_cap_respects_min_keep_floor(log_dir):
    """保底值：旧日志不会被砍到只剩几 KB

    实际生效的保底值是 min(MIN_KEEP_BYTES, 预算/10) —— 固定 1MB 的保底
    在小预算下会把所有旧日志都判成「砍不动」，清理直接失效。
    """
    from src.utils.log import MIN_KEEP_BYTES

    kb = 1024
    budget = 1 * 1024 * kb
    effective_floor = min(MIN_KEEP_BYTES, budget // 10)

    old = _mk(log_dir / f"{APP}.log.a", 1500 * kb, age_days=5)
    _mk(log_dir / f"{APP}.log.b", 1500 * kb, age_days=4)
    _mk(log_dir / f"{APP}.log", 1500 * kb)

    log_module.cleanup_logs(retention_days=0, max_size_mb=1)

    assert old.exists()
    assert old.stat().st_size >= effective_floor, "不应低于保底值"
    # 保底值是预算的 1/10，而不是固定 1MB
    assert effective_floor == budget // 10


def test_size_cap_zero_disables_size_rule(log_dir):
    big = _mk(log_dir / f"{APP}.log.big", 5 * 1024 * 1024)
    log_module.cleanup_logs(retention_days=0, max_size_mb=0)
    assert big.exists()


def test_active_log_untouched_when_no_rotated_logs(log_dir, capsys):
    """只剩当日日志且它本身就超上限时：不动它，只告警"""
    active = _mk(log_dir / f"{APP}.log", 4 * 1024 * 1024)
    active.write_bytes(b"HEADMARK" + b"y" * (4 * 1024 * 1024) + b"TAILMARK")
    before = active.read_bytes()

    log_module.cleanup_logs(retention_days=0, max_size_mb=1)

    assert active.read_bytes() == before, "当日日志绝不能被截断"
    assert b"HEADMARK" in active.read_bytes()
    out = capsys.readouterr().out
    assert "当日日志不会被截断" in out, "应给出可操作的告警而不是静默失败"


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
