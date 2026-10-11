from . import base
from .base import ENGINE_TYPE, ONNXRUNTIME_ENGINE

if ENGINE_TYPE == ONNXRUNTIME_ENGINE:
    from . import rapidocr as _engine
else:
    from . import paddleocr as _engine

base.bind_engine(_engine.OcrDetector, _engine.ocr_manager)

OcrData = base.OcrData
RuleOcr = base.RuleOcr
ocr_match_once = base.ocr_match_once

OcrDetector = _engine.OcrDetector
check_ocr_folder = _engine.check_ocr_folder
ocr_manager = _engine.ocr_manager

__all__ = [
    "ENGINE_TYPE",
    "OcrData",
    "OcrDetector",
    "RuleOcr",
    "check_ocr_folder",
    "ocr_match_once",
    "ocr_manager",
]
