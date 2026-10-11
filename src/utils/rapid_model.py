import hashlib
import importlib.metadata
import os
import shutil
from pathlib import Path

import httpx

from .application import APP_PATH, MODEL_DIR_PATH, Connect
from .log import logger

OCR_VERSION: str = "PP-OCRv6"
"""OCR 模型版本"""

MODEL_TYPE: str = "tiny"
"""模型规格。

注意：可用取值随 `OCR_VERSION` 变化，v4/v5 为 `mobile`/`server`，v6 为 `tiny`/`small`/`medium`。
"""

LANG_TYPE: str = "ch"
"""识别语言，中英文"""

PADDLE_ENGINE: str = "paddle"
"""PaddlePaddle 引擎标识"""

ONNXRUNTIME_ENGINE: str = "onnxruntime"
"""ONNX Runtime 引擎标识"""

PADDLE_GPU_DIST: str = "paddlepaddle-gpu"
"""GPU 版 PaddlePaddle 的发行包名

CPU 版包名为 `paddlepaddle`，两者都提供 `paddle` 模块，故只能按包名区分。
仅在从源码直接运行（没有 `lib/nvidia` 目录）时作为 GPU 判据的补充。
"""

ONNX_MODEL_FILES: tuple = ("SHA256",)
"""ONNX Runtime 引擎：单个 `.onnx` 文件，校验和键为 `SHA256`"""

PADDLE_MODEL_FILES: tuple = ("inference.json", "inference.pdiparams")
"""PaddlePaddle 引擎：模型目录下的文件，校验和键与文件名同名"""


def is_gpu_build() -> bool:
    """是否为 GPU 版

    判据与 `Config._detect_gpu_mode()` 一致：GPU 版打包后会包含 `lib/nvidia`
    目录，检查该目录是否存在即可。这样打包后无需依赖包元数据即可判定版本类型。

    Returns:
        bool: 是否为 GPU 版
    """
    return (APP_PATH / "lib" / "nvidia").is_dir()


def detect_engine() -> str:
    """探测当前环境可用的推理引擎

    GPU 版走 PaddlePaddle + CUDA，CPU 版走 ONNX Runtime + CPU，判定顺序：

    1. **`lib/nvidia` 目录存在** —— 打包后的 GPU 版。与 `Config._detect_gpu_mode()`
       用同一个判据，打包后不依赖包元数据即可判定。
    2. **回退检查发行包名 `paddlepaddle-gpu`** —— 从源码直接运行时（未打包，
       没有 `lib/nvidia` 目录）靠它识别出 GPU 环境。

    注意不能用 `import paddle` 判断：CPU 版 `paddlepaddle` 同样提供 `paddle`
    模块，用它判断会把纯 CPU 的 PaddlePaddle 误判为 GPU 版，导致
    `EngineConfig.paddle.use_cuda=True` 下初始化失败。

    Returns:
        str: `paddle` 或 `onnxruntime`
    """
    if is_gpu_build():
        return PADDLE_ENGINE

    try:
        importlib.metadata.version(PADDLE_GPU_DIST)
    except importlib.metadata.PackageNotFoundError:
        return ONNXRUNTIME_ENGINE
    return PADDLE_ENGINE


ENGINE_TYPE: str = detect_engine()
"""实际使用的推理引擎，启动时根据环境自动判定"""


class RapidModel:
    """RapidOCR 模型

    - ONNX Runtime 引擎：单个 `.onnx` 文件，如 `models/PP-OCRv6_det_small.onnx`
    - PaddlePaddle 引擎：模型目录，如 `models/PP-OCRv6_det_small/inference.json`

    下载地址与校验和从 RapidOCR 自带的 `default_models.yaml` 中解析，
    避免与库版本脱节。
    """

    task_type: str = ""
    """模型任务类型，det 检测 / rec 识别"""

    HTTP_TIMEOUT: int = 60
    """HTTP 请求超时时间（秒）"""

    CHUNK_SIZE: int = 8192
    """下载文件时的块大小（字节）"""

    PROGRESS_STEP: int = 10
    """进度日志输出间隔（百分比）"""

    @classmethod
    def get_model_info(cls) -> dict:
        """从 RapidOCR 获取该模型的下载信息

        Returns:
            dict: 含 `model_dir`(下载地址) 与各文件的校验和
        """
        from rapidocr.inference_engine.base import FileInfo, InferSession
        from rapidocr.utils.typings import EngineType, ModelType, OCRVersion, TaskType

        return InferSession.get_model_url(
            FileInfo(
                engine_type=EngineType(ENGINE_TYPE),
                ocr_version=OCRVersion(OCR_VERSION),
                task_type=TaskType(cls.task_type),
                lang_type=LANG_TYPE,
                model_type=ModelType(MODEL_TYPE),
            )
        )

    @classmethod
    def get_model_dir(cls) -> Path:
        """模型在 `models` 目录下的存放目录

        Returns:
            Path: 模型目录（ONNX 引擎下即模型文件所在目录）
        """
        info = cls.get_model_info()
        return MODEL_DIR_PATH / Path(info["model_dir"]).name

    @classmethod
    def get_required_files(cls) -> tuple:
        """当前引擎下需要哪些文件，以及各自的校验和键"""
        if ENGINE_TYPE == PADDLE_ENGINE:
            return PADDLE_MODEL_FILES
        return ONNX_MODEL_FILES

    @classmethod
    def get_file_paths(cls) -> list:
        """当前引擎下所有需要校验的文件路径"""
        model_dir = cls.get_model_dir()
        if ENGINE_TYPE == PADDLE_ENGINE:
            return [model_dir / name for name in PADDLE_MODEL_FILES]
        return [model_dir]

    @classmethod
    def get_dict_path(cls) -> Path | None:
        """识别字典文件路径

        ONNX 模型内嵌了字符表，无需字典；Paddle 模型不内嵌，
        需从 `dict_url` 下载。

        存放位置与 RapidOCR 自身保持一致：平铺在 `model_root_dir` 下
        （见 rapidocr/ch_ppocr_rec/main.py 的 `dict_dir`），
        而不是在模型子目录里，否则预下载的文件 RapidOCR 不会读到。

        Returns:
            Path | None: 字典文件路径，无需字典时为 None
        """
        info = cls.get_model_info()
        dict_url = info.get("dict_url")
        if not dict_url:
            return None
        return MODEL_DIR_PATH / Path(dict_url).name

    @classmethod
    def is_valid(cls) -> bool:
        """校验模型文件是否存在且完整"""
        model_name = cls.get_model_dir().name
        info = cls.get_model_info()

        for path in cls.get_file_paths():
            if not path.is_file():
                logger.ui_error(f"{model_name} 缺少文件: {path.name}")
                return False
            # ONNX 的校验和键是 SHA256，Paddle 的键与文件名同名
            expect = info.get("SHA256") if path.name.endswith(".onnx") else info.get(path.name)
            if expect is None:
                continue
            if cls.get_file_sha256(path) != expect:
                logger.ui_error(f"{path.name} 校验失败，文件可能已损坏")
                return False

        dict_path = cls.get_dict_path()
        if dict_path is not None and not dict_path.is_file():
            logger.ui_error(f"{model_name} 缺少字典文件: {dict_path.name}")
            return False

        return True

    @classmethod
    def download(cls) -> bool:
        """下载模型到 `models` 目录

        每个文件先落到 `.part` 临时文件，校验通过后再原子替换到最终路径：
        直接写最终路径时，中途中断会留下半截模型，is_valid() 判定失败后
        又会把它删掉——原本完好的模型因此被误删，下次启动还要重下。

        Returns:
            bool: 是否下载成功
        """
        info = cls.get_model_info()
        model_dir = cls.get_model_dir()

        logger.ui(f"下载 {model_dir.name} 模型...")
        if ENGINE_TYPE == PADDLE_ENGINE:
            ok = cls._download_paddle_model(info, model_dir)
        else:
            ok = cls._download_onnx_model(info, model_dir)

        if not ok:
            return False

        if not cls.is_valid():
            # 校验没过：清理本次下载产物（仅 .part 与新下载的完整文件）
            if model_dir.is_dir():
                shutil.rmtree(model_dir, ignore_errors=True)
            else:
                model_dir.unlink(missing_ok=True)
            dict_path = cls.get_dict_path()
            if dict_path is not None:
                dict_path.unlink(missing_ok=True)
            return False

        return True

    @classmethod
    def _download_onnx_model(cls, info: dict, model_dir: Path) -> bool:
        """下载 ONNX 模型（单个文件）"""
        url = info["model_dir"]
        return cls._download_file(url, model_dir, model_dir.name)

    @classmethod
    def _download_paddle_model(cls, info: dict, model_dir: Path) -> bool:
        """下载 PaddlePaddle 模型（目录 + 多个文件 + 识别字典）"""
        base_url = info["model_dir"].rstrip("/")
        model_dir.mkdir(parents=True, exist_ok=True)

        for name in PADDLE_MODEL_FILES:
            url = f"{base_url}/{name}"
            if not cls._download_file(url, model_dir / name, name):
                return False

        dict_url = info.get("dict_url")
        if dict_url:
            # 字典平铺存放，与 RapidOCR 的 dict_dir 保持一致
            dict_name = Path(dict_url).name
            if not cls._download_file(dict_url, MODEL_DIR_PATH / dict_name, dict_name):
                return False

        return True

    @classmethod
    def _download_file(cls, url: str, save_path: Path, name: str) -> bool:
        """下载单个文件到 `save_path`

        先写 `save_path.part`，下载完整后 `os.replace` 原子替换：
        中断/失败只影响临时文件，已有的可用模型保持完好。
        """
        tmp_path = save_path.with_name(save_path.name + ".part")
        try:
            with httpx.stream(
                "GET", url, headers=Connect.headers, timeout=cls.HTTP_TIMEOUT, follow_redirects=True
            ) as resp:
                resp.raise_for_status()

                total_size = int(resp.headers.get("content-length", 0))
                downloaded_size = 0
                last_logged_percent = 0

                with open(tmp_path, "wb") as f:
                    for chunk in resp.iter_bytes(chunk_size=cls.CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            # 每 PROGRESS_STEP% 输出一次进度
                            if total_size > 0:
                                progress = downloaded_size / total_size * 100
                                current_percent = int(progress // cls.PROGRESS_STEP * cls.PROGRESS_STEP)
                                if current_percent != last_logged_percent and current_percent % cls.PROGRESS_STEP == 0:
                                    last_logged_percent = current_percent
                                    logger.ui(
                                        f"下载进度: {progress:.1f}% ({downloaded_size / 1024 / 1024:.2f}MB/{total_size / 1024 / 1024:.2f}MB)"
                                    )
            os.replace(tmp_path, save_path)
            return True
        except httpx.HTTPError as e:
            logger.ui_error(f"下载失败: {e}")
            tmp_path.unlink(missing_ok=True)
            return False
        except OSError as e:
            logger.ui_error(f"文件操作失败: {e}")
            tmp_path.unlink(missing_ok=True)
            return False
        except Exception as e:
            logger.ui_error(f"下载过程中发生未知错误: {e}")
            tmp_path.unlink(missing_ok=True)
            return False

    @classmethod
    def get_file_sha256(cls, file_path: Path) -> str:
        """计算文件的 sha256"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(cls.CHUNK_SIZE), b""):
                sha256.update(block)
        return sha256.hexdigest()


class DetModel(RapidModel):
    """文本检测模型"""

    task_type: str = "det"


class RecModel(RapidModel):
    """文本识别模型"""

    task_type: str = "rec"


ALL_MODELS: tuple = (DetModel, RecModel)
"""程序运行所需的全部模型"""


def check_models() -> bool:
    """检查模型文件是否完整

    Returns:
        bool: 是否完整
    """
    if not MODEL_DIR_PATH.exists():
        logger.error("models文件夹不存在")
        return False

    for model in ALL_MODELS:
        if not model.is_valid():
            return False

    logger.info(f"{OCR_VERSION} ({ENGINE_TYPE}) 的模型文件完整")
    return True


def download_models() -> bool:
    """下载全部模型

    Returns:
        bool: 是否全部下载成功
    """
    for model in ALL_MODELS:
        if not model.download():
            return False

    logger.ui("模型下载完成")
    return True


def auto_download() -> bool:
    """检查并按需下载模型

    Returns:
        bool: 模型是否可用
    """
    logger.info(f"检查 {OCR_VERSION} ({ENGINE_TYPE}) 的模型文件...")

    if check_models():
        logger.info("模型已存在且完整，无需下载")
        return True

    logger.ui(f"模型不完整或不存在，开始下载 {OCR_VERSION} ({ENGINE_TYPE}) 的模型...")
    if not download_models():
        logger.ui_error(f"下载 {OCR_VERSION} 模型失败")
        return False

    return check_models()
