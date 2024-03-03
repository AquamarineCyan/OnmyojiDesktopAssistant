import json
import tempfile
import os
from ctypes import *
from datetime import datetime, timezone

import pyautogui
import win32api

from .application import APP_NAME, APP_PATH, SCREENSHOT_DIR_PATH
from .coordinate import RectangleCoor
from .decorator import run_in_thread, time_count
from .event import event_ocr_init
from .log import logger
from .window import window


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

        # https://gitee.com/raoyutian/paddle-ocrsharp/tree/dev/PaddleOCRDemo/python
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
        paddleOCR.Initializejson(p_det_infer, p_cls_infer, p_rec_infer, p_ocrkeys, parameterjson.encode(encode))
        paddleOCR.Detect.restype = c_wchar_p

        # self.img_file = OCR_DEBUG_FILE
        self.img_file = os.path.join(tempfile.gettempdir(), f"{APP_NAME}_ocr_debug.png")
        self.paddleocr = paddleOCR
        self.flag_init = True
        event_ocr_init.set()
        return True

    def get_raw_result(self) -> dict | None:
        window_width_screenshot = 1138  # 截图宽度
        window_height_screenshot = 679  # 截图高度

        if not self.flag_init:
            return None

        try:
            t1 = datetime.now(timezone.utc)
            pyautogui.screenshot(
                imageFilename=self.img_file,
                region=(
                    window.window_left - 1,
                    window.window_top,
                    window_width_screenshot,
                    window_height_screenshot
                )
            )
            t2 = datetime.now(timezone.utc)
            logger.info(f"ocr screenshot cost {t2-t1} at {self.img_file}")
        except Exception:
            logger.error("screenshot failed.")
            return None

        # 下面的方法不能实现，只能保存到本地，然后用gbk编码打开
        # byte_image = io.BytesIO()
        # img.save(byte_image, format="PNG")
        # byte_image = byte_image.getvalue()

        img = str(self.img_file).encode("gbk")
        result = self.paddleocr.Detect(img)
        t3 = datetime.now(timezone.utc)

        logger.info(f"ocr cost: {t3-t2}")
        self.result = json.loads(result)
        for item in self.result:
            logger.info(f"ocr result: {item}")
        # TODO 优化返回值，去除多余项
        return self.result

    @run_in_thread
    @time_count
    def self_check(self):
        self.get_raw_result()
        for item in self.result:
            logger.debug(item)
            BoxPoints = item["BoxPoints"]
            for _ in BoxPoints:
                logger.debug(_)
            logger.debug(BoxPoints)
            logger.debug(item["Score"])
            logger.debug(item["Text"])
            if (item["Score"] > 0.9) and (item["Text"] == "阴阳师-网易游戏"):
                logger.ui("ocr self check successfully.")
                return
        logger.warn("ocr self check failed.")

    def free_dll(self):
        if not self.flag_init:
            return
        try:
            win32api.FreeLibrary(self.paddleocr._handle)
        except Exception:
            logger.error("free dll failed")


ocr = CharacterRecognition()
"""文字识别
    
    用法：
    ```python
    ocr.get_raw_result()
"""


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
        self.rect = RectangleCoor(self.x1, self.x2, self.y1, self.y2)


def check_raw_result_once(text: str = None, score: float = 0.8) -> (OcrData | None):
    result = ocr.get_raw_result()
    for item in result:
        ocr_data = OcrData(item)
        if ocr_data.score >= score and ocr_data.text == text:
            return ocr_data
    return None
