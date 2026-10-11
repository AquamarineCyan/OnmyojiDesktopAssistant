from typing import Literal

from pydantic import BaseModel


class AssetImage(BaseModel):
    name: str = ""
    """名称"""
    file: str = ""
    """文件路径"""
    description: str = ""
    """描述"""
    region: tuple[int, int, int, int] = (0, 0, 0, 0)
    """区域"""
    score: float = 0.7
    """匹配分数"""
    method: Literal["COLOR", "GRAYSCALE"] = "COLOR"
    """匹配方法  COLOR: 颜色匹配  GRAYSCALE: 灰度匹配"""


class AssetOcr(BaseModel):
    name: str = ""
    """名称"""
    keyword: str | list[str] = ""
    """关键词。

    可以是单个字符串，也可以是字符串列表 —— 列表表示「任一命中即可」，
    用于容忍 OCR 的同形字混淆（典型如 `挑` 被识别成 `桃`）。

    单个字符串的素材无需改动，老配置完全兼容。
    """
    description: str = ""
    """描述"""
    region: tuple[int, int, int, int] = (0, 0, 0, 0)
    """区域"""
    score: float = 0.7
    """匹配分数"""
    method: Literal["PERFECT", "INCLUDE"] = "PERFECT"
    """匹配方法  PERFECT: 完全匹配  INCLUDE: 包含匹配"""


def normalize_keywords(keyword: str | list[str] | tuple | None) -> tuple[str, ...]:
    """把 keyword 规整成去掉首尾空白的字符串元组

    空值统一成空元组，这样 `item.text in keywords` 恒为 False，不会误命中。
    """
    if keyword is None:
        return ()
    if isinstance(keyword, str):
        keyword = (keyword,)
    return tuple(k.strip() for k in keyword if isinstance(k, str) and k.strip())


def match_keyword(text: str, keyword: str | list[str] | tuple | None, method: str = "PERFECT") -> bool:
    """判断 OCR 文本 `text` 是否命中 `keyword`

    `keyword` 支持字符串列表（任一命中即可，用于容忍同形字混淆）。
    业务脚本里手写的 `item.text == asset.keyword` / `keyword in item.text`
    都要走这里：keyword 变成列表后，前者恒为 False、后者会抛
    `TypeError: 'in <string>' requires string as left operand`。
    """
    keywords = normalize_keywords(keyword)
    if method == "INCLUDE":
        return any(k in text for k in keywords)
    return text in keywords
