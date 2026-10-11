"""
rapid_ocr.py —— RapidOCR 模块（与 benchmark 对齐的优化版）
优化点：
  [O1] OMP/线程环境变量在 import rapidocr 之前设置，绑定物理核
  [O2] 检测输入短边下限 736
  [O3] 关闭 CLS（文字方向固定场景）
  [O4] 预热用 720×1280 空图跑 2 次
  [O5] 走 ScreenShot.get_array()，避免每帧 PIL→NumPy 转换
  [O6] 截图落盘改为默认关闭、按需开启（避免每帧 I/O）
"""
import os
import threading
import time
from typing import Literal

import cv2
import numpy as np
from PIL import Image


# ==========================================================================
# [O1] 环境变量必须在 import onnxruntime / rapidocr 之前设置
# ==========================================================================

def _detect_physical_cores() -> int:
    """优先用 psutil 拿物理核；无 psutil 时用逻辑核数/2 估算"""
    try:
        import psutil  # type: ignore
        n = psutil.cpu_count(logical=False)
        if n:
            return int(n)
    except Exception:
        pass
    logical = os.cpu_count() or 1
    return max(1, logical // 2) if logical > 2 else logical


_PHYSICAL_CORES = _detect_physical_cores()
_LOGICAL_CORES = os.cpu_count() or 1
_INTRA_THREADS = max(1, min(8, _PHYSICAL_CORES))

os.environ.setdefault("OMP_NUM_THREADS", str(_INTRA_THREADS))
os.environ.setdefault("OMP_PROC_BIND", "true")
os.environ.setdefault("OMP_PLACES", "cores")
os.environ.setdefault("ONNXRUNTIME_INTRA_OP_NUM_THREADS", str(_INTRA_THREADS))
os.environ.setdefault("ONNXRUNTIME_INTER_OP_NUM_THREADS", "1")
os.environ.setdefault("ORT_DISABLE_ALL_LOGS", "1")


# ==========================================================================
# 正常 import
# ==========================================================================

from rapidocr.utils.typings import EngineType, ModelType, OCRVersion

from .application import SCREENSHOT_DIR_PATH
from .assets import AssetOcr
from .coordinate import get_scale, scale_region
from .log import logger
from .point import Point, Rectangle
from .rapid_model import LANG_TYPE, MODEL_TYPE, OCR_VERSION, ONNXRUNTIME_ENGINE, PADDLE_ENGINE, auto_download
from .screenshot import ScreenShot
from .window import window_manager


# ==========================================================================
# 检测参数
# ==========================================================================

DET_THRESH: float = 0.3
"""检测二值化阈值"""

DET_BOX_THRESH: float = 0.5
"""检测框置信度阈值"""
DET_UNCLIP_RATIO: float = 1.6
"""检测框扩张系数"""


DET_LIMIT_SIDE_LEN: int = 736
"""检测输入短边下限；配合 `Det.limit_type=min`，小于该值的短边会被放大"""

USE_CLS: bool = False
"""是否启用文字方向分类模型；固定朝向 UI 场景关闭可省一份推理"""

SAVE_SCREENSHOT: bool = False
"""[O6] 是否把每帧截图落盘；默认关闭，需要排障时改 True"""


# ==========================================================================
# 引擎参数
# ==========================================================================

def get_onnxruntime_engine_params() -> dict:
    """按物理核数组装 ONNX Runtime 引擎参数"""
    return {
        "EngineConfig.onnxruntime.enable_cpu_mem_arena": True,
        "EngineConfig.onnxruntime.intra_op_num_threads": _INTRA_THREADS,
        "EngineConfig.onnxruntime.inter_op_num_threads": 1,
    }


ONNXRUNTIME_ENGINE_PARAMS: dict = get_onnxruntime_engine_params()
"""ONNX Runtime 引擎参数"""

PADDLE_ENGINE_PARAMS: dict = {
    "EngineConfig.paddle.use_cuda": True,
    "EngineConfig.paddle.cuda_ep_cfg.device_id": 0,
    "EngineConfig.paddle.cuda_ep_cfg.gpu_mem": 500,
}
"""PaddlePaddle 引擎参数，GPU 版使用 CUDA 加速"""


def build_engine_params() -> dict:
    """按当前引擎组装 RapidOCR 推理参数"""
    from .rapid_model import ENGINE_TYPE

    engine_type = EngineType(ENGINE_TYPE)
    params = {
        "Global.use_det": True,
        "Global.use_cls": USE_CLS,       # [O3] 默认 False
        "Global.use_rec": True,

        "Det.engine_type": engine_type,
        "Det.ocr_version": OCRVersion(OCR_VERSION),
        "Det.model_type": ModelType(MODEL_TYPE),
        "Det.lang_type": LANG_TYPE,

        "Rec.engine_type": engine_type,
        "Rec.ocr_version": OCRVersion(OCR_VERSION),
        "Rec.model_type": ModelType(MODEL_TYPE),
        "Rec.lang_type": LANG_TYPE,

        "Det.thresh": DET_THRESH,
        "Det.box_thresh": DET_BOX_THRESH,
        "Det.unclip_ratio": DET_UNCLIP_RATIO,
        "Det.limit_type": "min",
        "Det.limit_side_len": DET_LIMIT_SIDE_LEN,   # [O2] = 736
    }

    if ENGINE_TYPE == PADDLE_ENGINE:
        params.update(PADDLE_ENGINE_PARAMS)
    elif ENGINE_TYPE == ONNXRUNTIME_ENGINE:
        params.update(ONNXRUNTIME_ENGINE_PARAMS)

    return params


def check_ocr_folder():
    """检查OCR资源是否存在，不存在则自动下载"""
    return auto_download()


# ==========================================================================
# OCRManager
# ==========================================================================

_INFER_LOCK = threading.Lock()
"""推理串行锁

全局任务线程（悬赏封印图像识别 + 点击）与玩法线程（OCR）会并发进入。
ONNX Runtime 的 `Run` 本身线程安全，但 PaddlePaddle 的 `PaddleInferSession`
复用同一个输入张量 handle，并发调用会互相覆盖输入数据、识别结果随机错乱。
推理本身不适合并发，串行化即可。
"""


class OCRManager:
    """OCR 引擎管理器"""

    def __init__(self):
        self.rapidocr = None
        self.engine_type: str = ""

    def is_initialized(self) -> bool:
        return self.rapidocr is not None

    def init(self) -> bool:
        if self.is_initialized():
            return True

        from .rapid_model import ENGINE_TYPE

        try:
            from rapidocr import RapidOCR
            from .application import MODEL_DIR_PATH

            self.engine_type = ENGINE_TYPE
            logger.ui(
                f"开始初始化文字识别模型[RapidOCR {OCR_VERSION} {MODEL_TYPE} / {ENGINE_TYPE}] "
                f"intra={_INTRA_THREADS} (物理核={_PHYSICAL_CORES}, 逻辑核={_LOGICAL_CORES})"
            )
            t_start = time.perf_counter()
            params = build_engine_params()
            params["Global.model_root_dir"] = str(MODEL_DIR_PATH)
            # logger.ui(params)

            self.rapidocr = RapidOCR(params=params)

            # [O4] 预热：必须用「有文字」的图。纯色空图过不了检测，
            #      RapidOCR 会以 "The text detection result is empty" 提前返回，
            #      rec 模型仍是懒加载，首次真实识别照样要付模型加载 + 算子编译的抖动。
            #      尺寸取接近真实截图的横屏比例（游戏为 1136x640 ~ 1393x784）。
            self._warmup()

            t_end = time.perf_counter()
            logger.ui(f"模型[RapidOCR {ENGINE_TYPE}]初始化成功，用时 {(t_end - t_start):.2f} 秒")
            return True

        except Exception as e:
            logger.error(f"模型[RapidOCR {OCR_VERSION} {MODEL_TYPE} / {ENGINE_TYPE}]初始化失败: {e}")
            raise

    def _warmup(self) -> None:
        """跑两次带文字的图，让 det/rec 两个模型都完成加载与算子预热"""
        warmup = np.full((640, 1136, 3), 24, dtype=np.uint8)
        cv2.putText(warmup, "WARMUP 12345", (80, 360), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (240, 240, 240), 4)
        for _ in range(2):
            self.rapidocr(warmup)

    def detect(self, image) -> list:
        """执行OCR检测

        Args:
            image: PIL.Image（RGB）或 np.ndarray（**BGR**，OpenCV 约定）

        Returns:
            list: 格式化后的OCR检测结果
        """
        if not self.is_initialized():
            logger.ui_error("模型未初始化成功，请重启后再试")
            return []

        try:
            t1 = time.perf_counter()
            if isinstance(image, np.ndarray):
                img_np = image
            elif isinstance(image, Image.Image):
                # RapidOCR 的 ndarray 入口是原样透传（不转通道），
                # 而 PIL 入口走 np.array() 得到 RGB，两者约定不一致：
                # 这里统一转成 BGR 再送进去，避免通道颠倒降低识别率
                img_np = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
            else:
                raise TypeError(f"不支持的图像类型: {type(image)}")

            with _INFER_LOCK:
                result = self.rapidocr(img_np)

            res_data = get_ocrdata_from_result(result)
            t4 = time.perf_counter()

            logger.debug(f"OCR inference: {(t4 - t1) * 1000:.2f} ms, {len(res_data)} items")
            return res_data
        except Exception as e:
            logger.error(f"OCR检测失败: {e}")
            return []


ocr_manager = OCRManager()
"""全局OCR管理器实例"""


# ==========================================================================
# 结果解析
# ==========================================================================

def get_ocrdata_from_result(result) -> list:
    boxes, txts, scores = result.boxes, result.txts, result.scores
    if boxes is None or txts is None or scores is None:
        return []

    result_list = []
    for text, score, box in zip(txts, scores, boxes):
        item = {
            "Text": text,
            "Score": float(score),
            "BoxPoints": [{"X": int(point[0]), "Y": int(point[1])} for point in box[:4]],
        }
        result_list.append(item)
    return result_list


class OcrData:
    text: str
    score: float
    rect: Rectangle
    center: Point

    def __init__(self, item: dict) -> None:
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
        fx, fy = get_scale()
        self.x1, self.y1 = self.x1 / fx, self.y1 / fy
        self.x2, self.y2 = self.x2 / fx, self.y2 / fy
        self.rect = Rectangle(self.x1, self.y1, x2=self.x2, y2=self.y2)
        self.center = self.rect.get_center_point()

    def __repr__(self) -> str:
        return f"text: {self.text}, score: {self.score}, rect: {self.rect.get_box()}, center: {self.center}"


# ==========================================================================
# OcrDetector —— 走 get_array，去掉每帧写盘
# ==========================================================================

class OcrDetector:
    """OCR检测器，负责截图、OCR调用和结果处理"""

    def __init__(self, region: tuple | None = None):
        self.region = region or window_manager.current.client_rect

    def get_raw_result(self) -> list[OcrData]:
        """截图 → OCR → 结构化结果

        [O5] 走 ScreenShot.get_array() 直接拿 ndarray，跳过 PIL 中间对象
        [O6] 截图落盘改为可选，默认不写盘，消除每帧 I/O
        """
        if not ocr_manager.is_initialized():
            ocr_manager.init()

        start_time = time.time()
        screenshot = ScreenShot(rect=self.region)
        if not screenshot.is_valid:
            logger.error(f"OCR 截图失败，region={self.region}")
            return []

        if SAVE_SCREENSHOT:
            screenshot_file = SCREENSHOT_DIR_PATH / f"{time.strftime('%Y%m%d%H%M%S')}.png"
            screenshot.get_image().save(screenshot_file)

        image = screenshot.get_array()          # ← 直接 ndarray（BGR）
        ocr_result = ocr_manager.detect(image)

        # 截图按 region 裁剪，RapidOCR 返回的框是 region 局部坐标，
        # 必须先加回 region 原点才是客户区坐标（与 image.py 的处理一致），
        # 否则带 region 的素材点击位置会整体偏移到窗口左上角
        offset_x, offset_y = int(self.region[0]), int(self.region[1])

        data_result: list[OcrData] = []
        for item in ocr_result:
            if not isinstance(item, dict):
                logger.warning(f"OCR item is not a dict: {item}")
                continue
            if item.get("Score", 0.0) == 0.0:
                continue
            if item.get("Text", "") == "":
                continue
            for point in item["BoxPoints"]:
                point["X"] += offset_x
                point["Y"] += offset_y
            ocr_data = OcrData(item)
            ocr_data.to_reference()
            logger.debug(f"result: {ocr_data}")
            data_result.append(ocr_data)

        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000
        logger.debug(f"OCR detection took {elapsed_ms:.2f} ms, {len(data_result)} items")
        return data_result


# ==========================================================================
# RuleOcr / ocr_match_once 保持不变
# ==========================================================================

class RuleOcr:
    """文字识别"""

    def __init__(
        self,
        assetocr: AssetOcr = None,
        name: str = None,
        keyword: str = None,
        region: tuple = None,
        score: float = 0.7,
        method: Literal["PERFECT", "INCLUDE"] = "PERFECT",
    ) -> None:
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
            self.region = scale_region(self.region)

        self.match_result: OcrData = None
        self.detector = OcrDetector(self.region)

    def get_raw_result(self) -> list[OcrData]:
        return self.detector.get_raw_result()

    def match(
        self,
        ocr_result: list[OcrData] = None,
        keyword: str = None,
        score: float = None,
        debug: bool = False,
    ) -> OcrData | None:
        if not ocr_manager.is_initialized():
            ocr_manager.init()

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
    """批量文字匹配（一次截图，多次匹配）"""
    detector = OcrDetector()
    ocr_result = detector.get_raw_result()

    for item in asset_list:
        rule = RuleOcr(item)
        result = rule.match(ocr_result)
        if result:
            return rule

    return None
