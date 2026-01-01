from typing import Literal

from ..utils.assets import AssetOcr
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
