import os
import time

import numpy as np
from PIL.Image import Image


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


from rapidocr import RapidOCR
from rapidocr.utils.typings import EngineType, ModelType, OCRVersion

from ..application import MODEL_DIR_PATH
from ..image import convert_image_rgb_to_bgr
from ..log import logger
from ..screenshot import ScreenShot
from ..window import window_manager
from .base import ENGINE_TYPE, OcrData, ONNXRUNTIME_ENGINE, PADDLE_ENGINE
from .rapid_model import LANG_TYPE, MODEL_TYPE, OCR_VERSION, auto_download

DET_THRESH: float = 0.3
"""检测二值化阈值"""

DET_BOX_THRESH: float = 0.5
"""检测框置信度阈值"""

DET_UNCLIP_RATIO: float = 1.6
"""检测框扩张系数"""


DET_LIMIT_SIDE_LEN: int = 640
"""检测输入短边下限；配合 `Det.limit_type=min`，小于该值的短边会被放大"""

USE_CLS: bool = False
"""是否启用文字方向分类模型；固定朝向 UI 场景关闭可省一份推理"""


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
    engine_type = EngineType(ENGINE_TYPE)
    params = {
        "Global.use_det": True,
        "Global.use_cls": USE_CLS,  # [O3] 默认 False
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
        "Det.limit_side_len": DET_LIMIT_SIDE_LEN,  # [O2] = 736
    }

    if ENGINE_TYPE == PADDLE_ENGINE:
        params.update(PADDLE_ENGINE_PARAMS)
    elif ENGINE_TYPE == ONNXRUNTIME_ENGINE:
        params.update(ONNXRUNTIME_ENGINE_PARAMS)

    return params


def check_ocr_folder():
    """检查OCR资源是否存在，不存在则自动下载"""
    return auto_download()


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

        try:
            self.engine_type = ENGINE_TYPE
            logger.ui(
                f"开始初始化文字识别模型[RapidOCR {OCR_VERSION} {MODEL_TYPE} / {ENGINE_TYPE}] "
                f"intra={_INTRA_THREADS} (物理核={_PHYSICAL_CORES}, 逻辑核={_LOGICAL_CORES})"
            )
            t_start = time.perf_counter()
            params = build_engine_params()
            params["Global.model_root_dir"] = str(MODEL_DIR_PATH)

            self.rapidocr = RapidOCR(params=params)

            # 用接近真实截图尺寸(720×1280)的空图预热 2 次，触发算子编译 + 内存池稳定，避免首次真实推理抖动
            warmup = np.zeros((720, 1280, 3), dtype=np.uint8)
            self.rapidocr(warmup)
            self.rapidocr(warmup)

            t_end = time.perf_counter()
            logger.ui(f"模型[RapidOCR {ENGINE_TYPE}]初始化成功，用时 {(t_end - t_start):.2f} 秒")
            return True

        except Exception as e:
            logger.error(f"模型[RapidOCR {OCR_VERSION} {MODEL_TYPE} / {ENGINE_TYPE}]初始化失败: {e}")
            raise

    def detect(self, image) -> list:
        """执行OCR检测

        Args:
            image: PIL.Image（RGB）或 np.ndarray（BGR，OpenCV 约定）；优先传 ndarray 以省去转换开销

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
            elif isinstance(image, Image):
                # RapidOCR 的 ndarray 入口按 BGR 解释（不转通道），PIL 是 RGB：
                img_np = convert_image_rgb_to_bgr(image)
            else:
                img_np = np.asarray(image)

            result = self.rapidocr(img_np)

            res_data = get_ocrdata_from_result(result)
            t4 = time.perf_counter()

            logger.debug(f"解析结果: {(t4 - t1) * 1000:.2f} ms")
            return res_data
        except Exception as e:
            logger.error(f"OCR检测失败: {e}")
            return []


ocr_manager = OCRManager()
"""全局OCR管理器实例"""


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


class OcrDetector:
    """OCR检测器，负责截图、OCR调用和结果处理"""

    def __init__(self, region: tuple | None = None):
        self.region = region or window_manager.current.client_rect

    def get_raw_result(self) -> list[OcrData]:
        """截图 → OCR → 结构化结果"""
        if not ocr_manager.is_initialized():
            ocr_manager.init()

        start_time = time.time()
        screenshot = ScreenShot(rect=self.region)

        image = screenshot.get_bgr()
        if image is None:
            logger.error(f"OCR 截图失败，region={self.region}")
            return []
        ocr_result = ocr_manager.detect(image)

        data_result: list[OcrData] = []
        for item in ocr_result:
            # 过滤无效数据
            if not isinstance(item, dict):
                logger.warning(f"OCR item is not a dict: {item}")
                continue
            if item.get("Score", 0.0) == 0.0:
                continue
            if item.get("Text", "") == "":
                continue
            ocr_data = OcrData(item)
            ocr_data.to_reference()
            logger.info(f"result: {ocr_data}")
            data_result.append(ocr_data)

        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000
        logger.debug(f"OCR detection took {elapsed_ms:.2f} ms")
        return data_result
