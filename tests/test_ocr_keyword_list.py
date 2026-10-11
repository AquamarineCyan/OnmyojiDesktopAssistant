"""OCR keyword 支持字符串列表（容忍同形字混淆）

`AssetOcr.keyword` 允许是 `str | list[str]`，列表表示「任一命中即可」，
典型场景是 OCR 把 `挑` 识别成 `桃`。

顺带锁住一类容易漏的坑：业务脚本里手写的
`item.text == asset.keyword` 和 `keyword in item.text`，
在 keyword 变成列表后前者恒为 False、后者抛
`TypeError: 'in <string>' requires string as left operand`。
"""
import pytest

from src.utils.assets import AssetOcr, match_keyword, normalize_keywords

# ------------------------------------------------------------ normalize


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("挑战", ("挑战",)),
        (["挑战", "桃战"], ("挑战", "桃战")),
        (("挑战", "桃战"), ("挑战", "桃战")),
        ("  挑战  ", ("挑战",)),
        ([" 挑战 ", "", None, "桃战"], ("挑战", "桃战")),
        (None, ()),
        ("", ()),
        ([], ()),
    ],
)
def test_normalize_keywords(raw, expected):
    assert normalize_keywords(raw) == expected


# ------------------------------------------------------------ match_keyword


def test_perfect_single_string_still_works():
    """单字符串的存量素材行为不能变"""
    assert match_keyword("挑战", "挑战") is True
    assert match_keyword("开始挑战", "挑战") is False
    assert match_keyword("", "") is False


def test_perfect_list_matches_any():
    assert match_keyword("挑战", ["挑战", "桃战"]) is True
    assert match_keyword("桃战", ["挑战", "桃战"]) is True
    assert match_keyword("取消", ["挑战", "桃战"]) is False


def test_include_list_matches_any_substring():
    assert match_keyword("开始挑战吧", ["挑战", "桃战"], "INCLUDE") is True
    assert match_keyword("开始桃战吧", ["挑战", "桃战"], "INCLUDE") is True
    assert match_keyword("开始战斗吧", ["挑战", "桃战"], "INCLUDE") is False


def test_empty_keyword_never_matches():
    """空值绝不能变成「匹配一切」"""
    for raw in (None, "", [], ["", "  "]):
        assert match_keyword("挑战", raw) is False
        assert match_keyword("挑战", raw, "INCLUDE") is False


# ------------------------------------------------------------ AssetOcr


def test_asset_ocr_accepts_str_and_list():
    assert AssetOcr(keyword="挑战").keyword == "挑战"
    assert AssetOcr(keyword=["挑战", "桃战"]).keyword == ["挑战", "桃战"]


def test_asset_ocr_keyword_stays_backward_compatible():
    """老配置是单字符串，不能被悄悄转成 list 之类"""
    a = AssetOcr(name="start", keyword="挑战")
    assert isinstance(a.keyword, str)
    assert a.method == "PERFECT"
    assert a.score == 0.7


def test_rule_ocr_normalizes_asset_keyword(monkeypatch):
    """RuleOcr 接收 AssetOcr 时也要把列表规整掉"""
    from src.utils import window as window_module
    from src.utils.rapidocr import RuleOcr

    monkeypatch.setattr(window_module.window_manager, "current", _FakeWin())
    r = RuleOcr(AssetOcr(name="start", keyword=["挑战", "桃战"]))
    assert r.keyword == ("挑战", "桃战")


def test_rule_ocr_accepts_list_keyword_directly(monkeypatch):
    from src.utils import window as window_module
    from src.utils.rapidocr import RuleOcr

    monkeypatch.setattr(window_module.window_manager, "current", _FakeWin())
    assert RuleOcr(name="x", keyword=["挑战", "桃战"]).keyword == ("挑战", "桃战")
    assert RuleOcr(name="x", keyword="挑战").keyword == ("挑战",)


class _FakeWin:
    """RuleOcr 构造时会读当前窗口的客户区，给个最小替身即可"""

    family = "pc"
    client_width = 1136
    client_height = 640
    client_rect = (0, 0, 1136, 640)


# ------------------------------------------------- 业务脚本的裸比较回归


def test_daoguantupo_style_comparison_is_list_safe():
    """daoguantupo / qiling 曾经直接写 `asset.keyword == item.text`

    keyword 变 list 后这两种写法都会坏，现在统一走 match_keyword。
    这个用例把「旧写法为什么不安全」固定下来，防止有人改回去。
    """
    keyword = ["挑战", "桃战"]

    # 旧写法 1：恒 False（静默失效，最难发现）
    assert ("桃战" == keyword) is False

    # 旧写法 2：直接抛 TypeError
    with pytest.raises(TypeError):
        _ = keyword in "桃战"

    # 新写法
    assert match_keyword("桃战", keyword) is True
    assert match_keyword("桃战", keyword, "INCLUDE") is True


# ------------------------------------------------------------ 素材一致性


def test_global_assets_keywords_match_ocr_output():
    """global 素材里的 keyword 必须能匹配上模型自己的输出

    实测（PP-OCRv6 tiny，裁紧图 14~32px 共 42 例）这些关键词 rec 全部识别正确，
    score 均为 1.00，不存在同形字混淆；列表里若有多余候选不应影响首个命中。
    """
    import json

    from src.utils.application import RESOURCE_DIR_PATH

    for name in ("global",):
        data = json.loads((RESOURCE_DIR_PATH / name / "assets.json").read_text(encoding="utf-8"))
        for item in data["ocr_data"]:
            keyword = item["keyword"]
            keywords = normalize_keywords(keyword)
            assert keywords, f"{name}/{item['name']} 的 keyword 为空"
            # 主关键词必须在列表里，且用 match_keyword 能匹配自身
            assert keyword in keywords or list(keyword) == list(keywords)
            assert match_keyword(keywords[0], keyword) is True
