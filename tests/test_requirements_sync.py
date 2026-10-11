"""依赖清单一致性守卫

`pyproject.toml` 是唯一权威来源（CI 用 `uv sync` 读它），
但 README 也让 pip 用户 `pip install -r requirements.txt`，
所以两份 requirements 必须存在。三份清单手工维护必然漂移 ——
修复前 `pydantic>=2.1.0` vs `>=2.13.4`、`pywin32` vs `pywin32==312`
这类差异会长期静默存在，装出来的环境与 CI 不一致。

这里用与生成器同一份逻辑做校验，保证 `pytest` 单独跑也能抓到漂移，
不必依赖 CI 里的额外步骤。
"""
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import sync_requirements as sync


def _pyproject() -> dict:
    with open(sync.PYPROJECT, "rb") as f:
        return tomllib.load(f)


def test_requirements_matches_pyproject():
    pyproject = _pyproject()
    expected = sync.build_requirements(pyproject, gpu=False)

    assert sync.REQUIREMENTS.read_text(encoding="utf-8") == expected, (
        "requirements.txt 与 pyproject.toml 不一致，请运行：uv run python tools/sync_requirements.py"
    )


def test_requirements_gpu_matches_pyproject():
    pyproject = _pyproject()
    expected = sync.build_requirements(pyproject, gpu=True)

    assert sync.REQUIREMENTS_GPU.read_text(encoding="utf-8") == expected, (
        "requirements-gpu.txt 与 pyproject.toml 不一致，请运行：uv run python tools/sync_requirements.py"
    )


def test_every_runtime_dependency_is_listed():
    """两份 requirements 都必须覆盖 pyproject 的全部运行时依赖

    GPU 版按设计把 onnxruntime 换成 paddlepaddle-gpu，因此比对时先套用替换规则。
    """
    pyproject = _pyproject()
    expected = {_split_name(spec) for spec in pyproject["project"]["dependencies"]}

    cpu_listed = {_split_name(line) for line in _requirement_lines(sync.REQUIREMENTS)}
    assert not expected - cpu_listed, f"requirements.txt 缺少依赖: {sorted(expected - cpu_listed)}"

    gpu_expected = {_split_name(sync.GPU_ENGINE_SWAP.get(n, n)) for n in expected}
    gpu_listed = {_split_name(line) for line in _requirement_lines(sync.REQUIREMENTS_GPU)}
    assert not gpu_expected - gpu_listed, (
        f"requirements-gpu.txt 缺少依赖: {sorted(gpu_expected - gpu_listed)}"
    )


def test_gpu_variant_swaps_inference_engine_only():
    """GPU 版只允许替换推理引擎，其余依赖必须与 CPU 版完全一致"""
    cpu = _deps_by_name(_requirement_lines(sync.REQUIREMENTS))
    gpu = _deps_by_name(_requirement_lines(sync.REQUIREMENTS_GPU))

    swapped = set(sync.GPU_ENGINE_SWAP)
    for name in swapped:
        assert name in cpu, f"pyproject 中已无 {name}，GPU 替换规则应同步删除"
        assert name not in gpu, f"{name} 不应出现在 GPU 版里"
        assert _swap_target(name) in gpu, f"GPU 版缺少 {name} 的替代品"

    for name, spec in cpu.items():
        if name in swapped:
            continue
        assert gpu.get(name) == spec, f"{name} 在 CPU/GPU 两版间不一致: {spec} vs {gpu.get(name)}"


def test_gpu_variant_has_paddle_extra_index():
    """GPU 版需要 paddlepaddle 的专用 index，否则装不上"""
    text = sync.REQUIREMENTS_GPU.read_text(encoding="utf-8")
    assert "--extra-index-url https://www.paddlepaddle.org.cn/" in text
    assert "paddlepaddle-gpu" in text
    # CPU 版不应该带 paddle 的 index
    assert "paddlepaddle.org.cn" not in sync.REQUIREMENTS.read_text(encoding="utf-8")


def test_requirements_files_are_pure_ascii():
    """pip 用 locale 编码读 requirements 文件（非 UTF-8，除非有 BOM）

    中文 Windows 的 locale 是 cp936/GBK，文件里只要有一个非 ASCII 字符，
    `pip install -r` 就会直接抛 UnicodeDecodeError —— 注释也会导致失败。
    """
    for path in (sync.REQUIREMENTS, sync.REQUIREMENTS_GPU):
        text = path.read_text(encoding="utf-8")
        offenders = {c for c in text if ord(c) > 127}
        assert not offenders, f"{path.name} 含非 ASCII 字符 {sorted(offenders)}：pip 在 GBK locale 下会解析失败"


def test_requirements_have_no_utf8_bom():
    """带 BOM 时 pip 会把 BOM 当成第一行内容的一部分"""
    for path in (sync.REQUIREMENTS, sync.REQUIREMENTS_GPU):
        assert not path.read_bytes().startswith(b"\xef\xbb\xbf"), f"{path.name} 不应带 UTF-8 BOM"


# ---------------------------------------------------------------- helpers


def _split_name(spec: str) -> str:
    name, _ = sync._split_requirement(spec)
    return sync._normalize(name)


def _requirement_lines(path: Path) -> list[str]:
    """取出文件里真正的依赖行（跳过注释、空行）"""
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "-")):
            continue
        lines.append(line)
    return lines


def _deps_by_name(lines: list[str]) -> dict[str, str]:
    out = {}
    for line in lines:
        name, constraint = sync._split_requirement(line)
        out[sync._normalize(name)] = constraint
    return out


def _swap_target(name: str) -> str:
    """替换目标包名（要先拆出版本约束，否则 _normalize 会把 `==3.3.1` 一起改掉）"""
    target, _ = sync._split_requirement(sync.GPU_ENGINE_SWAP[name])
    return sync._normalize(target)
