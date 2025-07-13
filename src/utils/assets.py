from typing import Literal

from pydantic import BaseModel


class AssetImage(BaseModel):
    name: str = None
    file: str = None
    region: tuple[int, int, int, int] = None
    score: float = 0.7
    method: Literal["COLOR", "GRAYSCALE"] = "COLOR"


class AssetOcr(BaseModel):
    name: str = None
    keyword: str = None
    region: tuple[int, int, int, int] = None
    score: float = 0.7
    method: Literal["PERFACT", "INCLUDE"] = "PERFACT"
