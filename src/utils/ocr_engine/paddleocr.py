import os
import subprocess
import time
from contextlib import contextmanager

import numpy as np
from PIL import Image

from ..application import MODEL_DIR_PATH
from ..gpu_info import get_cuda_device_list, get_gpu_list, resolve_device
from ..log import logger
from ..screenshot import ScreenShot
from ..window import window_manager
from .base import OcrData
from .paddle_model import PaddleModel

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"  # 禁用 Paddle 模型源校验，避免不必要的网络请求


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
        logger.info("正在拦截控制台黑框")
        yield
    finally:
        # 恢复
        subprocess.Popen = orig_popen
        logger.info("控制台黑框拦截已恢复")


def check_ocr_folder():
    """检查OCR资源是否存在，不存在则自动下载"""
    return PaddleModel.auto_download(3)


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

    def init(self, version: int = 3, gpu_id: int | None = None) -> bool:
        """初始化OCR

        Args:
            version: OCR模型版本号，默认 3
            gpu_id: GPU编号，>=0 时通过 device=gpu:{gpu_id} 手动指定，None/-1 自动选择

        Returns:
            bool: 初始化成功/已初始化返回 True
        """
        if self.is_initialized():
            return True

        try:
            logger.ui(f"开始初始化文字识别模型[PaddleOCR v{version}]")
            t_start = time.perf_counter()
            from paddleocr import PaddleOCR

            det_class, rec_class = PaddleModel._get_model_classes(version)
            if not det_class or not rec_class:
                logger.ui_error(f"未找到版本[PaddleOCR v{version}]的模型定义")
                return False

            kwargs = {
                "text_detection_model_name": det_class.name,
                "text_detection_model_dir": str(MODEL_DIR_PATH / det_class.model_dir_name),
                "text_recognition_model_name": rec_class.name,
                "text_recognition_model_dir": str(MODEL_DIR_PATH / rec_class.model_dir_name),
                "use_doc_orientation_classify": False,
                "use_doc_unwarping": False,
                "use_textline_orientation": False,
                "det_db_thresh": 0.3,
                "det_db_box_thresh": 0.5,
                "det_db_unclip_ratio": 1.5,
            }
            device = resolve_device(gpu_id)
            cuda_devices = get_cuda_device_list()
            # 仅当 CUDA 设备存在时指定 device；无 N 卡时回退 CPU，避免 device=gpu:N 报错
            if device and cuda_devices:
                kwargs["device"] = device
            elif device:
                # CUDA 设备不可用时从 nvidia-smi 获取显卡名称，取不到则用泛称
                unavailable_gpu = next((g["name"] for g in get_gpu_list() if g["index"] == gpu_id), "所选GPU")
                logger.ui_warn(f"{unavailable_gpu} 不可用，切换到CPU模式")
            with paddle_hide_window_context():
                self.paddleocr = PaddleOCR(**kwargs)

            t_end = time.perf_counter()
            gpu_name = None
            if cuda_devices:
                gpu_name = cuda_devices[gpu_id if device and 0 <= gpu_id < len(cuda_devices) else 0]
            logger.ui(
                f"模型[PaddleOCR v{version}]初始化成功，用时 {(t_end - t_start):.2f} 秒（设备: {gpu_name or 'CPU'}）"
            )
            return True

        except Exception as e:
            logger.error(f"模型[PaddleOCR v{version}]初始化失败: {e}")
            raise

    def detect(self, image: Image.Image | np.ndarray) -> list:
        """执行OCR检测

        Args:
            image: PIL Image（RGB）或 np.ndarray（BGR，OpenCV 约定）

        Returns:
            list[dict]: 已格式化的识别结果，每项含 Text / Score / BoxPoints

        Example:
            [
                {
                    "Text": "XXXX",
                    "Score": 0.99,
                    "BoxPoints": [
                        {"X": 100, "Y": 10},
                        {"X": 200, "Y": 20},
                        {"X": 300, "Y": 30},
                        {"X": 400, "Y": 40},
                    ],
                }
            ]
        """
        if not self.is_initialized():
            logger.ui_error("模型未初始化成功，请重启后再试")
            return []

        try:
            t1 = time.perf_counter()
            img_np = np.array(image)
            result = self.paddleocr.predict(input=img_np)
            # 统一格式
            formatted_result = []
            for res in result:
                formatted_result.extend(get_ocrdata_from_result(res))
            t2 = time.perf_counter()
            logger.debug(f"OCR总耗时: {(t2 - t1) * 1000:.2f} ms")
            return formatted_result
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
        if not ocr_manager.is_initialized():
            ocr_manager.init()

        start_time = time.time()
        screenshot = ScreenShot(rect=self.region)
        image = screenshot.get_image()

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
            ocr_data.to_reference()  # 截图坐标 → 基准空间坐标
            logger.info(f"result: {ocr_data}")
            data_result.append(ocr_data)

        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000
        logger.debug(f"OCR detection took {elapsed_ms:.2f} ms")
        return data_result
