import tarfile
from enum import Enum
from pathlib import Path
from typing import Tuple, Type

import httpx

from .application import MODEL_DIR_PATH, Connect
from .log import logger


class ModelType(Enum):
    DET = "det"
    REC = "rec"


class PaddleModel:
    name: str = ""
    """模型名称"""
    version: int = 0
    """模型版本号"""
    model_type: ModelType = None
    """模型类型（DET 检测 / REC 识别）"""
    model_dir_name: str = ""
    """模型解压后的目录名（由 __init_subclass__ 自动计算）"""
    model_tar_name: str = ""
    """模型压缩包文件名（由 __init_subclass__ 自动计算）"""
    base_url: str = "https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/"
    """模型下载基础 URL"""

    REQUIRED_FILES: Tuple[str, ...] = ("inference.json", "inference.pdiparams", "inference.yml")
    """模型必需的文件列表"""

    HTTP_TIMEOUT: int = 30
    """HTTP 请求超时时间（秒）"""

    CHUNK_SIZE: int = 8192
    """下载文件时的块大小（字节）"""

    PROGRESS_STEP: int = 10
    """进度日志输出间隔（百分比）"""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name:
            cls.model_dir_name = f"{cls.name}_infer"
            cls.model_tar_name = f"{cls.name}_infer.tar"

    @property
    def url(self) -> str:
        """构建模型文件的下载 URL"""
        return f"{self.base_url}{self.model_tar_name}"

    @classmethod
    def get_models_dir(cls) -> Path:
        """获取模型存储目录"""
        return MODEL_DIR_PATH

    @classmethod
    def _get_model_classes(cls, version: int) -> Tuple[Type["PaddleModel"] | None, Type["PaddleModel"] | None]:
        """获取指定版本的 DET 和 REC 模型类"""
        det_class: Type["PaddleModel"] | None = None
        rec_class: Type["PaddleModel"] | None = None

        for subclass in cls.__subclasses__():
            if subclass.version == version:
                if subclass.model_type == ModelType.DET:
                    det_class = subclass
                elif subclass.model_type == ModelType.REC:
                    rec_class = subclass

        return det_class, rec_class

    @classmethod
    def download_version(cls, version: int) -> bool:
        """下载指定版本的det和rec模型"""
        model_dir = cls.get_models_dir()

        det_class, rec_class = cls._get_model_classes(version)
        if not det_class or not rec_class:
            logger.ui_warn(f"未找到版本 {version} 的模型")
            return False

        # 下载det模型
        if not cls._download_and_extract_model(det_class(), model_dir):
            return False

        # 下载rec模型
        if not cls._download_and_extract_model(rec_class(), model_dir):
            return False

        logger.ui(f"版本 {version} 的模型下载完成")
        return True

    @classmethod
    def _download_and_extract_model(cls, model: "PaddleModel", model_dir: Path) -> bool:
        """下载并解压单个模型"""
        tar_file = model_dir / model.model_tar_name

        logger.ui(f"下载 {model.name} 模型...")
        if not cls._download_file(model.url, str(tar_file)):
            return False

        if not cls._extract_tar(str(tar_file), str(model_dir)):
            return False

        return True

    @classmethod
    def _download_file(cls, url: str, save_path: str) -> bool:
        """下载文件（带进度条）"""
        try:
            with httpx.stream("GET", url, headers=Connect.headers, timeout=cls.HTTP_TIMEOUT) as response:
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))
                downloaded_size = 0
                last_logged_percent = 0

                with open(save_path, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=cls.CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            # 计算并显示进度（每 PROGRESS_STEP% 输出一次）
                            if total_size > 0:
                                progress = downloaded_size / total_size * 100
                                current_percent = int(progress // cls.PROGRESS_STEP * cls.PROGRESS_STEP)
                                if current_percent != last_logged_percent and current_percent % cls.PROGRESS_STEP == 0:
                                    last_logged_percent = current_percent
                                    logger.ui(
                                        f"下载进度: {progress:.1f}% ({downloaded_size / 1024 / 1024:.2f}MB/{total_size / 1024 / 1024:.2f}MB)"
                                    )
            return True
        except httpx.HTTPError as e:
            logger.ui_error(f"下载失败: {e}")
            # 清理不完整的文件
            save_path_obj = Path(save_path)
            if save_path_obj.exists():
                save_path_obj.unlink()
            return False
        except OSError as e:
            logger.ui_error(f"文件操作失败: {e}")
            return False
        except Exception as e:
            logger.ui_error(f"下载过程中发生未知错误: {e}")
            save_path_obj = Path(save_path)
            if save_path_obj.exists():
                save_path_obj.unlink()
            return False

    @classmethod
    def _extract_tar(cls, tar_path: str, extract_dir: str) -> bool:
        """解压tar文件"""
        tar_path_obj = Path(tar_path)
        logger.info(f"开始解压文件: {tar_path_obj.name}")
        try:
            with tarfile.open(tar_path, "r") as tar:
                tar.extractall(extract_dir)
            # 删除模型压缩包
            tar_path_obj.unlink()
            logger.info(f"解压完成: {tar_path_obj.name}")
            return True
        except tarfile.TarError as e:
            logger.ui_error(f"解压失败: {e}")
            return False
        except OSError as e:
            logger.ui_error(f"文件操作失败: {e}")
            return False

    @classmethod
    def check_model_files(cls, version: int) -> bool:
        """检测指定版本的模型文件是否完整"""
        model_dir = cls.get_models_dir()

        if not model_dir.exists():
            logger.error("models文件夹不存在")
            return False

        det_class, rec_class = cls._get_model_classes(version)
        if not det_class or not rec_class:
            logger.ui_warn(f"未找到版本 {version} 的模型")
            return False

        # 检查det模型文件
        det_model = det_class()
        if not cls._check_single_model_files(det_model, model_dir):
            return False

        # 检查rec模型文件
        rec_model = rec_class()
        if not cls._check_single_model_files(rec_model, model_dir):
            return False

        logger.ui(f"PP-OCRv{version} 的模型文件完整")
        return True

    @classmethod
    def _check_single_model_files(cls, model: "PaddleModel", model_dir: Path) -> bool:
        """检查单个模型的文件是否完整"""
        model_dir_path = model_dir / model.model_dir_name

        if not model_dir_path.exists():
            logger.ui_error(f"{model.model_dir_name} 目录不存在")
            return False

        for file_name in cls.REQUIRED_FILES:
            file_path = model_dir_path / file_name
            if not file_path.exists():
                logger.ui_error(f"{model.model_dir_name} 缺少文件: {file_name}")
                return False

        return True

    @classmethod
    def auto_download(cls, version: int) -> bool:
        """自动检查并下载指定版本的模型"""
        logger.info(f"检查 PP-OCRv{version} 的模型文件...")

        # 检查模型是否完整
        if cls.check_model_files(version):
            logger.info("模型已存在且完整，无需下载")
            return True

        # 模型不完整或不存在，开始下载
        logger.ui(f"模型不完整或不存在，开始下载 PP-OCRv{version} 的模型...")
        if not cls.download_version(version):
            logger.ui_error(f"下载 PP-OCRv{version} 模型失败")
            return False

        # 再次检查模型是否完整
        logger.info(f"下载完成，检查 PP-OCRv{version} 的模型文件...")
        return cls.check_model_files(version)


class OCRv5MobileDet(PaddleModel):
    name: str = "PP-OCRv5_mobile_det"
    version: int = 5
    model_type: ModelType = ModelType.DET


class OCRv5MobileRec(PaddleModel):
    name: str = "PP-OCRv5_mobile_rec"
    version: int = 5
    model_type: ModelType = ModelType.REC


class OCRv4MobileDet(PaddleModel):
    name: str = "PP-OCRv4_mobile_det"
    version: int = 4
    model_type: ModelType = ModelType.DET


class OCRv4MobileRec(PaddleModel):
    name: str = "PP-OCRv4_mobile_rec"
    version: int = 4
    model_type: ModelType = ModelType.REC


class OCRv3MobileDet(PaddleModel):
    name: str = "PP-OCRv3_mobile_det"
    version: int = 3
    model_type: ModelType = ModelType.DET


class OCRv3MobileRec(PaddleModel):
    name: str = "PP-OCRv3_mobile_rec"
    version: int = 3
    model_type: ModelType = ModelType.REC
