import importlib.metadata
from typing import Literal

from ..assets import AssetOcr
from ..config import config
from ..coordinate import get_scale, scale_region
from ..point import Point, Rectangle
from ..window import window_manager

PADDLE_ENGINE: str = "paddle"
"""PaddlePaddle 引擎标识"""

ONNXRUNTIME_ENGINE: str = "onnxruntime"
"""ONNX Runtime 引擎标识"""

PADDLE_GPU_DIST: str = "paddlepaddle-gpu"
"""GPU 版 PaddlePaddle 的发行包名

CPU 版包名为 `paddlepaddle`，两者都提供 `paddle` 模块，故只能按包名区分。
仅在从源码直接运行（没有 `lib/nvidia` 目录）时作为 GPU 判据的补充。
"""


def detect_engine() -> str:
    """探测当前环境可用的推理引擎

    GPU 版走 PaddlePaddle + CUDA，CPU 版走 ONNX Runtime + CPU，判定顺序：

    1. **`config.is_gpu`** —— 打包后的 GPU 版（判据：`lib/nvidia` 目录存在）。
    2. **回退检查发行包名 `paddlepaddle-gpu`** —— 从源码直接运行时（未打包，
       没有 `lib/nvidia` 目录）靠它识别出 GPU 环境。

    注意不能用 `import paddle` 判断：CPU 版 `paddlepaddle` 同样提供 `paddle`
    模块，用它判断会把纯 CPU 的 PaddlePaddle 误判为 GPU 版，导致
    `EngineConfig.paddle.use_cuda=True` 下初始化失败。

    Returns:
        str: `paddle` 或 `onnxruntime`
    """
    if config.is_gpu:
        return PADDLE_ENGINE

    try:
        importlib.metadata.version(PADDLE_GPU_DIST)
    except importlib.metadata.PackageNotFoundError:
        return ONNXRUNTIME_ENGINE
    return PADDLE_ENGINE


ENGINE_TYPE: str = detect_engine()
"""实际使用的推理引擎，启动时根据环境自动判定"""


_detector_cls = None
"""当前引擎的 OcrDetector 实现类，由 bind_engine 注入"""

_ocr_manager = None
"""当前引擎的全局 OCR 管理器，由 bind_engine 注入"""


def bind_engine(detector_cls, ocr_manager) -> None:
    """绑定当前引擎的实现（OcrDetector 类 + 全局 ocr_manager）"""
    global _detector_cls, _ocr_manager
    _detector_cls = detector_cls
    _ocr_manager = ocr_manager


class OcrData:
    text: str
    """识别文本"""
    score: float
    """分数阈值"""
    rect: Rectangle
    """识别区域"""
    center: Point
    """识别区域中心坐标"""

    def __init__(self, item: dict) -> None:
        """
        Args:
            item: get_ocrdata_from_result 输出的单条识别结果，
                  dict 结构 {"Text": str, "Score": float, "BoxPoints": list[dict{X, Y}]}
        """
        self.score: float = round(item["Score"], 2)
        self.text: str = item["Text"]
        _BoxPoints = item["BoxPoints"]
        self.x1: int = _BoxPoints[0]["X"]
        self.y1: int = _BoxPoints[0]["Y"]
        self.x2: int = _BoxPoints[2]["X"]
        self.y2: int = _BoxPoints[2]["Y"]
        self.rect = Rectangle(self.x1, self.y1, x2=self.x2, y2=self.y2)
        self.center = self.rect.get_center_point()

    def to_reference(self) -> None:
        """实际客户区坐标 → 基准空间坐标（业务侧统一使用基准空间）"""
        fx, fy = get_scale()
        self.x1, self.y1 = self.x1 / fx, self.y1 / fy
        self.x2, self.y2 = self.x2 / fx, self.y2 / fy
        self.rect = Rectangle(self.x1, self.y1, x2=self.x2, y2=self.y2)
        self.center = self.rect.get_center_point()

    def __repr__(self) -> str:
        return f"text: {self.text}, score: {self.score}, rect: {self.rect.get_box()}, center: {self.center}"


class RuleOcr:
    """文字识别

    用法1：
    ```python
    ruleocr = RuleOcr(asset)
    if result := ruleocr.match():
        Mouse.click(result.center, *args, **kwargs)
    ```

    用法2：
    ```python
    result = RuleOcr().get_raw_result()
    for item in result:
        if target_text == item.text:
            do something
        if target_text in item.text:
            do something

    ```
    """

    def __init__(
        self,
        assetocr: AssetOcr = None,
        name: str = None,
        keyword: str = None,
        region: tuple = None,
        score: float = 0.7,
        method: Literal["PERFECT", "INCLUDE"] = "PERFECT",
    ) -> None:
        """
        Args:
            assetocr (AssetOcr):  文字识别资源
            name (str): 名称
            keyword (str): 关键词
            region (tuple): 区域
            score (float): 识别阈值
            method (Literal["PERFECT", "INCLUDE"]): 匹配方式，PERFECT：完全匹配，INCLUDE：包含匹配
        """
        if assetocr:
            self.keyword = assetocr.keyword
            self.name = assetocr.name
            self.region = assetocr.region
            self.score = assetocr.score
            self.method = assetocr.method
        else:
            self.keyword = keyword
            self.name = name
            self.region = region
            self.score = score
            self.method = method

        if self.region is None or self.region == (0, 0, 0, 0):
            self.region = window_manager.current.client_rect
        else:
            # 素材/显式 region 是基准空间坐标 → 实际客户区
            self.region = scale_region(self.region)

        self.match_result: OcrData = None
        self.detector = _detector_cls(self.region)

    def get_raw_result(self) -> list[OcrData]:
        """获取原始OCR检测结果

        Returns:
            list[OcrData]: OCR检测结果列表
        """
        return self.detector.get_raw_result()

    def match(
        self,
        ocr_result: list[OcrData] = None,
        keyword: str = None,
        score: float = None,
        debug: bool = False,
    ) -> OcrData | None:
        """执行文字匹配

        Args:
            ocr_result: 预计算的OCR结果，如果为None则自动计算
            keyword: 要匹配的关键词，如果为None则使用初始化时的关键词
            score: 匹配阈值，如果为None则使用初始化时的阈值
            debug: 是否开启调试模式

        Returns:
            OcrData | None: 匹配结果
        """
        if not _ocr_manager.is_initialized():
            _ocr_manager.init()

        # 重置匹配结果
        self.match_result = None

        if ocr_result is None:
            ocr_result = self.get_raw_result()

        if keyword is None:
            keyword = self.keyword
        if score is None:
            score = self.score

        for item in ocr_result:
            if item.score < score:
                continue
            if self.method == "PERFECT":
                if item.text == keyword:
                    self.match_result = item
                    return item
            elif self.method == "INCLUDE":
                if keyword in item.text:
                    self.match_result = item
                    return item

        return None


def ocr_match_once(asset_list: list[AssetOcr]) -> RuleOcr | None:
    """批量文字匹配（一次截图，多次匹配）

    对同一次截图结果执行多个关键词匹配，避免重复截图开销。
    返回第一个匹配成功的 RuleOcr 实例，调用者通过 .match_result 获取匹配结果。

    Args:
        asset_list (list[AssetOcr]): AssetOcr 列表，每个元素定义一组匹配规则（关键词、阈值、匹配方式）

    Returns:
        RuleOcr | None: 第一个匹配成功的 RuleOcr 实例，全部未匹配返回 None
    """
    # 使用OcrDetector获取一次OCR结果，避免重复截图
    detector = _detector_cls()
    ocr_result = detector.get_raw_result()

    for item in asset_list:
        rule = RuleOcr(item)
        result = rule.match(ocr_result)
        if result:
            return rule

    return None
