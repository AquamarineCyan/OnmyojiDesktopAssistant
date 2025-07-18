import json
import os
import tempfile
from ctypes import *
from datetime import datetime, timezone
from typing import Literal

import win32api

from .application import APP_NAME, APP_PATH
from .assets import AssetOcr
from .decorator import run_in_thread, time_count
from .event import event_ocr_init
from .log import logger
from .point import Rectangle
from .screenshot import ScreenShot


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


class CharacterRecognition:
    """文字识别"""

    def __init__(self) -> None:
        self.flag_init: bool = False  # 与 event_ocr_init 作用相同
        self.result: list = []

    def init(self):
        ocr_path = os.path.join(str(APP_PATH), "ocr")
        if os.path.exists(ocr_path):
            logger.info(f"ocr_path:{ocr_path}")
        else:
            self.flag_init = False
            event_ocr_init.clear()
            return False

        dll_path = os.path.join(ocr_path, "dll")
        model_path = os.path.join(ocr_path, "model")
        # 添加dll至环境变量，方便相对路径读取，2个操作缺一不可
        os.environ["path"] += f";{dll_path}"
        os.add_dll_directory(dll_path)

        # https://gitee.com/raoyutian/PaddleOCRSharp/tree/dev/PaddleOCRDemo/python
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

        # OCR_DEBUG_FILE = SCREENSHOT_DIR_PATH / "ocr_debug.png"
        # if not SCREENSHOT_DIR_PATH.exists():
        # SCREENSHOT_DIR_PATH.mkdir()

        parameterjson = json.dumps(parameter, default=PaddleOCRParameter2dict)
        paddleOCR.Initializejson(
            p_det_infer,
            p_cls_infer,
            p_rec_infer,
            p_ocrkeys,
            parameterjson.encode(encode),
        )
        paddleOCR.Detect.restype = c_wchar_p

        # self.img_file = OCR_DEBUG_FILE
        self.img_file = os.path.join(tempfile.gettempdir(), f"{APP_NAME}_ocr_debug.png")
        self.paddleocr = paddleOCR
        self.flag_init = True
        event_ocr_init.set()
        return True

    def get_raw_result(self) -> dict | None:
        if not self.flag_init:
            return None

        ScreenShot().save(self.img_file)

        # 下面的方法不能实现，只能保存到本地，然后用gbk编码打开
        # byte_image = io.BytesIO()
        # img.save(byte_image, format="PNG")
        # byte_image = byte_image.getvalue()

        t2 = datetime.now(timezone.utc)
        img = str(self.img_file).encode("gbk")
        result = self.paddleocr.Detect(img)
        t3 = datetime.now(timezone.utc)

        logger.info(f"ocr cost: {t3 - t2}")
        self.result = json.loads(result)
        for item in self.result:
            logger.info(f"ocr result: {item}")
        # TODO 优化返回值，去除多余项
        return self.result

    def free_dll(self):
        if not self.flag_init:
            return
        try:
            win32api.FreeLibrary(self.paddleocr._handle)
        except Exception:
            logger.error("free dll failed")


ocr = CharacterRecognition()


class OcrData:
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
        self.center = self.rect.get_rela_center()

    def __str__(self) -> str:
        return f"text: {self.text}, score: {self.score}, rect: {self.rect.get_box()}, center: {self.center}"


def check_raw_result_once(text: str = None, score: float = 0.8) -> OcrData | None:
    result = ocr.get_raw_result()
    for item in result:
        ocr_data = OcrData(item)
        if ocr_data.score >= score and ocr_data.text == text:
            return ocr_data
    return None


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

        self.match_result: OcrData = None

    def get_raw_result(self, file: str = None) -> list[OcrData]:
        if file is None:
            file = os.path.join(tempfile.gettempdir(), f"{APP_NAME}_ocr_debug.png")
            ScreenShot().save(file)
        image = file.encode("gbk")
        result = ocr.paddleocr.Detect(image)
        result = json.loads(result)
        list_ = []
        for item in result:
            # 过滤无效数据
            if item["Score"] == 0.0:
                continue
            if item["Text"] == "":
                continue
            ocr_data = OcrData(item)
            logger.info(f"ocr result: {ocr_data}")
            list_.append(ocr_data)
        return list_

    def match(
        self,
        ocr_result: str | list[OcrData] = None,
        keyword: str = None,
        score: float = None,
        debug: bool = False,
    ) -> OcrData | None:
        if not bool(event_ocr_init):
            ocr.init()

        if not isinstance(ocr_result, list):
            ocr_result = self.get_raw_result(ocr_result)

        if keyword is None:
            keyword = self.keyword
        if score is None:
            score = self.score
        for item in ocr_result:
            # TODO match region first
            if item.score < score:
                continue
            if self.method == "PERFACT":
                if item.text == self.keyword:
                    logger.info(f"{self.name} ocr match successfully.")
                    self.match_result = item
                    return item
            elif self.method == "INCLUDE":
                if self.keyword in item.text:
                    logger.info(f"{self.name} ocr match successfully.")
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
    ocr_result = RuleOcr().get_raw_result()
    for item in asset_list:
        rule = RuleOcr(item)
        result = rule.match(ocr_result)
        if result:
            return rule
    return None
