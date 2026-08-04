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
    keyword: str = ""
    """关键词"""
    description: str = ""
    """描述"""
    region: tuple[int, int, int, int] = (0, 0, 0, 0)
    """区域"""
    score: float = 0.7
    """匹配分数"""
    method: Literal["PERFACT", "INCLUDE"] = "PERFACT"
    """匹配方法  PERFECT: 完全匹配  INCLUDE: 包含匹配"""
