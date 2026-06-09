import subprocess
import time
from contextlib import contextmanager
from typing import Literal

import numpy as np
from PIL import Image

from .assets import AssetOcr
from .log import logger
from .point import Point, Rectangle
from .screenshot import ScreenShot
from .window import window_manager


@contextmanager
def paddle_hide_window_context():
    """
    进入该上下文时隐藏所有子进程黑框，离开时（包括发生异常）自动恢复正常控制台行为
    如果不关闭，会在PaddleOCR初始化时显示黑框，短暂停留后消失，造成闪屏效果
    """
    orig_popen = subprocess.Popen

    def _patched_popen(*args, **kwargs):
        """隐藏 PaddleOCR 进程窗口"""
        if "startupinfo" not in kwargs:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
            kwargs["startupinfo"] = startupinfo
        else:
            kwargs["startupinfo"].dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"].wShowWindow = 0

        if "creationflags" not in kwargs:
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        else:
            kwargs["creationflags"] |= subprocess.CREATE_NO_WINDOW

        return orig_popen(*args, **kwargs)

    try:
        subprocess.Popen = _patched_popen
        logger.info("控制台黑框拦截已开启")
        yield
    finally:
        # 恢复
        subprocess.Popen = orig_popen
        logger.info("控制台黑框拦截已关闭")


def check_ocr_folder():
    return True


class OCRManager:
    """OCR 引擎管理器

    负责 PaddleOCR 的初始化、资源管理和检测调用。
    通过模块级 ocr_manager 实例全局共享，避免重复初始化。
    """

    def __init__(self):
        self.paddleocr = None  # PaddleOCR 引擎实例，非 None 表示已初始化

    def is_initialized(self) -> bool:
        """检查OCR是否已初始化"""
        return self.paddleocr is not None

    def init(self) -> bool:
        """初始化OCR

        Returns:
            bool: 初始化成功/已初始化返回 True
        """
        if self.is_initialized():
            return True

        try:
            logger.ui("开始初始化 PaddleOCR v3...")
            from paddleocr import PaddleOCR

            with paddle_hide_window_context():
                logger.info("正在拦截控制台黑框")
                self.paddleocr = PaddleOCR(
                    text_detection_model_name="PP-OCRv3_mobile_det",
                    text_recognition_model_name="PP-OCRv3_mobile_rec",
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False,
                    use_textline_orientation=False,
                    det_db_thresh=0.3,
                    det_db_box_thresh=0.5,
                    det_db_unclip_ratio=1.5,
                )

            logger.info("OCR初始化成功")
            return True

        except Exception as e:
            logger.error(f"OCR初始化失败: {e}")
            raise

    def detect(self, image: Image.Image) -> list:
        """执行OCR检测

        Args:
            image: PIL Image 对象

        Returns:
            list: OCR检测结果
        """
        if not self.is_initialized():
            logger.ui_error("模型未初始化成功，请重启后再试")
            return []

        try:
            t1 = time.perf_counter()
            img_np = np.array(image)
            result = self.paddleocr.predict(input=img_np)
            t2 = time.perf_counter()
            logger.debug(f"OCR总耗时: {(t2 - t1) * 1000:.2f} ms")
            return result
        except Exception as e:
            logger.error(f"OCR检测失败: {e}")
            return []


ocr_manager = OCRManager()
"""全局OCR管理器实例"""


def get_ocrdata_from_result(raw_result):
    """从 PaddleOCR 原始结果中提取结构化数据

    将 PaddleOCR predict() 返回的 dict 结构转换为统一的中间格式，
    便于后续 OcrData 封装。BoxPoints 为矩形四角坐标 [左上, 右上, 右下, 左下]。

    Args:
        raw_result: PaddleOCR predict() 返回的单帧结果 dict，
                    包含 rec_texts / rec_scores / rec_boxes

    Returns:
        list[dict]: 格式化后的结果列表，每项含 Text / Score / BoxPoints
    """
    rec_texts = raw_result["rec_texts"]
    rec_scores = raw_result["rec_scores"]
    rec_boxes = raw_result["rec_boxes"]
    result_list = []
    for text, score, box in zip(rec_texts, rec_scores, rec_boxes):
        item = {
            "Text": text,
            "Score": score,
            "BoxPoints": [
                {"X": int(box[0]), "Y": int(box[1])},
                {"X": int(box[2]), "Y": int(box[1])},
                {"X": int(box[2]), "Y": int(box[3])},
                {"X": int(box[0]), "Y": int(box[3])},
            ],
        }
        result_list.append(item)
    return result_list


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

    def __repr__(self) -> str:
        return f"text: {self.text}, score: {self.score}, rect: {self.rect.get_box()}, center: {self.center}"


class OcrDetector:
    """OCR检测器，负责截图、OCR调用和结果处理"""

    def __init__(self, region: tuple | None = None):
        """
        Args:
            region: 检测区域，格式为 (x, y, width, height)
        """
        self.region = region or window_manager.current.client_rect

    def get_raw_result(self) -> list[OcrData]:
        """执行截图 + OCR 识别，返回结构化结果

        流程：截图 → PaddleOCR 检测 → 格式转换 → 过滤无效数据

        Returns:
            list[OcrData]: 过滤后的 OCR 识别结果列表
        """
        start_time = time.time()
        screenshot = ScreenShot(rect=self.region)
        image = screenshot.get_image()

        ocr_result = ocr_manager.detect(image)
        data_result: list[OcrData] = []
        try:
            formatted_result = []
            for res in ocr_result:
                formatted_result.extend(get_ocrdata_from_result(res))
        except Exception as e:
            logger.error(f"Failed to parse OCR result: {str(e)}")
            logger.error(f"Raw OCR result: {ocr_result}")
            return data_result

        for item in formatted_result:
            # 过滤无效数据
            if not isinstance(item, dict):
                logger.warning(f"OCR item is not a dict: {item}")
                continue
            if item.get("Score", 0.0) == 0.0:
                continue
            if item.get("Text", "") == "":
                continue
            ocr_data = OcrData(item)
            logger.info(f"result: {ocr_data}")
            data_result.append(ocr_data)

        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000
        logger.debug(f"OCR detection took {elapsed_ms:.2f} ms")
        return data_result


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
        region: tuple = None,  # 暂未用上
        score: float = 0.7,
        method: Literal["PERFACT", "INCLUDE"] = "PERFACT",
    ) -> None:
        """
        Args:
            assetocr (AssetOcr):  文字识别资源
            name (str): 名称
            keyword (str): 关键词
            region (tuple): 区域
            score (float): 识别阈值
            method (Literal["PERFACT", "INCLUDE"]): 匹配方式，PERFACT：完全匹配，INCLUDE：包含匹配
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

        self.match_result: OcrData = None
        self.detector = OcrDetector(self.region)

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
        if not ocr_manager.is_initialized():
            ocr_manager.init()

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
            if self.method == "PERFACT":
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
    detector = OcrDetector()
    ocr_result = detector.get_raw_result()

    for item in asset_list:
        rule = RuleOcr(item)
        result = rule.match(ocr_result)
        if result:
            return rule

    return None
