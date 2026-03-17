import json
import os
import time
from ctypes import *
from typing import Literal

from .application import APP_PATH, CACHE_DIR_PATH
from .assets import AssetOcr
from .log import logger
from .point import Point, Rectangle
from .screenshot import ScreenShot
from .window import window_manager


class PaddleOCRParameter(Structure):
    _fields_ = [
        ("use_gpu", c_bool),
        ("gpu_id", c_int),
        ("gpu_mem", c_int),
        ("cpu_math_library_num_threads", c_int),
        ("enable_mkldnn", c_bool),
        ("det", c_bool),
        ("rec", c_bool),
        ("cls", c_bool),
        ("max_side_len", c_int),
        ("det_db_thresh", c_float),
        ("det_db_box_thresh", c_float),
        ("det_db_unclip_ratio", c_float),
        ("use_dilation", c_bool),
        ("det_db_score_mode", c_bool),
        ("visualize", c_bool),
        ("use_angle_cls", c_bool),
        ("cls_thresh", c_float),
        ("cls_batch_num", c_int),
        ("rec_batch_num", c_int),
        ("rec_img_h", c_int),
        ("rec_img_w", c_int),
        ("show_img_vis", c_bool),
        ("use_tensorrt", c_bool),
    ]

    def __init__(self):
        self.use_gpu = False
        self.gpu_id = 0
        self.gpu_mem = 4000
        self.cpu_math_library_num_threads = 10
        self.enable_mkldnn = True
        self.det = True
        self.rec = True
        self.cls = False
        self.max_side_len = 960
        self.det_db_thresh = 0.3
        self.det_db_box_thresh = 0.618
        self.det_db_unclip_ratio = 1.6
        self.use_dilation = False
        self.det_db_score_mode = True
        self.visualize = False
        self.use_angle_cls = False
        self.cls_thresh = 0.9
        self.cls_batch_num = 1
        self.rec_batch_num = 6
        self.rec_img_h = 48
        self.rec_img_w = 320
        self.show_img_vis = False
        self.use_tensorrt = False


def PaddleOCRParameter2dict(param):
    return {
        "use_gpu": param.use_gpu,
        "gpu_id": param.gpu_id,
        "gpu_mem": param.gpu_mem,
        "cpu_math_library_num_threads": param.cpu_math_library_num_threads,
        "enable_mkldnn": param.enable_mkldnn,
        "det": param.det,
        "rec": param.rec,
        "cls": param.cls,
        "max_side_len": param.max_side_len,
        "det_db_thresh": param.det_db_thresh,
        "det_db_box_thresh": param.det_db_box_thresh,
        "det_db_unclip_ratio": param.det_db_unclip_ratio,
        "use_dilation": param.use_dilation,
        "det_db_score_mode": param.det_db_score_mode,
        "visualize": param.visualize,
        "use_angle_cls": param.use_angle_cls,
        "cls_thresh": param.cls_thresh,
        "cls_batch_num": param.cls_batch_num,
        "rec_batch_num": param.rec_batch_num,
        "rec_img_h": param.rec_img_h,
        "rec_img_w": param.rec_img_w,
        "show_img_vis": param.show_img_vis,
        "use_tensorrt": param.use_tensorrt,
    }


def check_ocr_folder():
    """检查当前目录下是否存在名为`ocr`的文件夹"""
    current_dir = os.getcwd()
    ocr_folder = os.path.join(current_dir, "ocr")

    if not os.path.exists(ocr_folder):
        return False

    dll_folder = os.path.join(ocr_folder, "dll")
    model_folder = os.path.join(ocr_folder, "model")

    if not (os.path.exists(dll_folder) and os.path.exists(model_folder)):
        return False

    return True


class OCRManager:
    """OCR管理器，负责OCR的初始化、资源管理和清理"""

    def __init__(self):
        self._init: bool = False
        self.paddleocr = None

    def init(self):
        """初始化OCR"""
        if self._init:
            return

        ocr_path = os.path.join(str(APP_PATH), "ocr")
        if os.path.exists(ocr_path):
            logger.info(f"ocr_path:{ocr_path}")
        else:
            raise FileNotFoundError(f"OCR文件夹不存在: {ocr_path}")

        dll_path = os.path.join(ocr_path, "dll")
        model_path = os.path.join(ocr_path, "model")
        # 添加dll至环境变量，方便相对路径读取，2个操作缺一不可
        os.environ["path"] += f";{dll_path}"
        os.add_dll_directory(dll_path)

        # https://gitee.com/raoyutian/PaddleOCRSharp/tree/dev/PaddleOCRDemo/python
        try:
            paddleOCR = cdll.LoadLibrary("PaddleOCR.dll")
            encode = "gbk"
            cls_infer = os.path.join(model_path, "ch_ppocr_mobile_v2.0_cls_infer")
            rec_infer = os.path.join(model_path, "ch_PP-OCRv3_rec_infer")
            det_infer = os.path.join(model_path, "ch_PP-OCRv3_det_infer")
            ocrkeys = os.path.join(model_path, "ppocr_keys.txt")

            parameter = PaddleOCRParameter()
            p_cls_infer = cls_infer.encode(encode)
            p_rec_infer = rec_infer.encode(encode)
            p_det_infer = det_infer.encode(encode)
            p_ocrkeys = ocrkeys.encode(encode)

            parameterjson = json.dumps(parameter, default=PaddleOCRParameter2dict)
            paddleOCR.Initializejson(
                p_det_infer,
                p_cls_infer,
                p_rec_infer,
                p_ocrkeys,
                parameterjson.encode(encode),
            )
            paddleOCR.Detect.restype = c_wchar_p

            self.paddleocr = paddleOCR
            self._init = True
            logger.info("OCR初始化成功")

        except Exception as e:
            logger.error(f"OCR初始化失败: {e}")
            self._init = False
            raise

    def is_initialized(self) -> bool:
        """检查OCR是否已初始化"""
        return self._init

    def detect(self, image_path: str) -> str:
        """执行OCR检测

        Args:
            image_path: 图像路径

        Returns:
            str: OCR检测结果（JSON字符串）
        """
        if not self._init:
            if not self.init():
                return ""

        try:
            image = image_path.encode("gbk")
            return self.paddleocr.Detect(image)
        except Exception as e:
            logger.error(f"OCR检测失败: {e}")
            return ""


# 全局OCR管理器实例
ocr_manager = OCRManager()


class OcrData:
    text: str
    """识别文本"""
    score: float
    """分数阈值"""
    rect: Rectangle
    """识别区域"""
    center: Point
    """识别区域中心坐标"""

    def __init__(self, item) -> None:
        self.score: float = round(item["Score"], 2)
        self.text: str = item["Text"]
        _BoxPoints = item["BoxPoints"]
        for i in range(len(_BoxPoints)):
            match i:
                case 0:
                    self.x1: int = _BoxPoints[i]["X"]
                    self.y1: int = _BoxPoints[i]["Y"]
                case 2:
                    self.x2: int = _BoxPoints[i]["X"]
                    self.y2: int = _BoxPoints[i]["Y"]
        self.rect = Rectangle(self.x1, self.y1, x2=self.x2, y2=self.y2)
        self.center = self.rect.get_center_point()

    def __repr__(self) -> str:
        return f"text: {self.text}, score: {self.score}, rect: {self.rect.get_box()}, center: {self.center}"


class OcrDetector:
    """OCR检测器，负责执行OCR检测和结果处理"""

    def __init__(self, region: tuple | None = None):
        """
        Args:
            region: 检测区域，格式为 (x, y, width, height)
        """
        self.region = region or window_manager.current.client_rect

    def get_raw_result(self) -> list[OcrData]:
        """获取原始OCR检测结果

        Returns:
            list[OcrData]: OCR检测结果列表
        """
        start_time = time.time()
        file = os.path.join(str(CACHE_DIR_PATH), "ocr_screenshot.png")
        ScreenShot(rect=self.region).save(file)

        ocr_result = ocr_manager.detect(file)
        data_result: list[OcrData] = []
        try:
            ocr_result = json.loads(ocr_result)
            if not isinstance(ocr_result, list):
                logger.error(f"OCR result is not a list: {ocr_result}")
                return data_result
        except Exception as e:
            logger.error(f"Failed to parse OCR result: {str(e)}")
            logger.error(f"Raw OCR result: {ocr_result}")
            return data_result

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
            logger.info(f"ocr result: {ocr_data}")
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
    detector = OcrDetector()
    result = detector.get_raw_result()
    for item in result:
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
        # 确保OCR已初始化
        if not ocr_manager.is_initialized():
            ocr_manager.init()

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
    """文字匹配

    参数:
        asset_list (list[AssetOcr]): 关键字列表

    返回:
        AssetOcr | None: 识别结果
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
