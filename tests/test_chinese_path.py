"""中文路径检测：覆盖基本区、扩展 A/B 区与兼容区汉字"""

from pathlib import Path

import pytest

from src.utils import function as function_module


@pytest.mark.parametrize(
    "path",
    [
        r"D:\code\OnmyojiDesktopAssistant",
        r"C:\Users\Public\App",
    ],
)
def test_english_path(monkeypatch, path):
    monkeypatch.setattr(function_module, "APP_PATH", Path(path))
    assert function_module.is_Chinese_Path() is False


@pytest.mark.parametrize(
    "path",
    [
        "D:\\阴阳师\\OnmyojiDesktopAssistant",  # 基本区
        "D:\\\u4e00\\App",  # 基本区下边界 U+4E00
        "D:\\\u9fff\\App",  # 基本区上边界 U+9FFF
        "D:\\\u3400\\App",  # 扩展 A 区下边界 U+3400
        "D:\\\u4dbf\\App",  # 扩展 A 区上边界 U+4DBF
        "D:\\\uf900\\App",  # 兼容区 U+F900
        "D:\\\U00020000\\App",  # 扩展 B 区下边界 U+20000
        "D:\\\U0002a6df\\App",  # 扩展 B 区上边界 U+2A6DF
    ],
)
def test_chinese_path(monkeypatch, path):
    monkeypatch.setattr(function_module, "APP_PATH", Path(path))
    assert function_module.is_Chinese_Path() is True


@pytest.mark.parametrize(
    "path",
    [
        "D:\\こんにちは\\App",  # 日文假名不在检测范围
        "D:\\café\\App",  # 非汉字非 ASCII
    ],
)
def test_non_chinese_non_ascii_path(monkeypatch, path):
    monkeypatch.setattr(function_module, "APP_PATH", Path(path))
    assert function_module.is_Chinese_Path() is False
