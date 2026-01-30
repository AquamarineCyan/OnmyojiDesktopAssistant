import json
from pathlib import Path
from typing import Literal

from ..utils.assets import AssetOcr
from ..utils.config import config
from ..utils.function import get_asset_data
from ..utils.image import AssetImage
from ..utils.log import logger


def load_asset(resource_path, type: str = Literal["image", "ocr"]) -> dict:
    assets_file, data = get_asset_data(resource_path)
    if data.get(f"{type}_data") is None:
        return None

    try:
        if type == "image":
            current_asset = data["current_path"]
            data = data["image_data"]
            for item in data:
                _item = item["file"]
                item["file"] = f"{current_asset}/{_item}"
            return data
        elif type == "ocr":
            data = data["ocr_data"]
            return data
    except KeyError:
        logger.ui_error(f"{assets_file}文件内容格式错误")
    except Exception as e:
        logger.ui_error(f"{assets_file}文件内容解析失败: {e}")

    return {}


def get_asset(dict_, name):
    for item in dict_:
        if item["name"] == name:
            return item


def get_image_asset(asset_image_list, name) -> AssetImage:
    return AssetImage(**get_asset(asset_image_list, name))


def get_ocr_asset(asset_ocr_list, name) -> AssetOcr:
    return AssetOcr(**get_asset(asset_ocr_list, name))


def check_assets(resource_path: str) -> bool:
    try:
        assets_path = config.resource_dir / resource_path / "assets.json"
        raw_data: dict = {}
        with open(str(assets_path), encoding="utf-8") as f:
            raw_data = json.load(f)

        current_asset = raw_data.get("current_path")
        if current_asset is None:
            return False

        image_data = raw_data.get("image_data")
        # image_data 可以不存在
        if isinstance(image_data, list):
            for item in image_data:
                file = Path(config.resource_dir / current_asset / item["file"])
                if file.exists():
                    logger.info(f"resource file [{file}] exists.")
                else:
                    logger.ui_error(f"资源文件[{file}]丢失")
                    raise FileNotFoundError

    except Exception as e:
        logger.ui_error(f"资源文件夹{resource_path}加载失败: {str(e)}")
        return False

    return True
