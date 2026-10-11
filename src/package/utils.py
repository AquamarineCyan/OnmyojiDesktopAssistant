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

        # ocr_data 同样要校验：它不校验的话，name 写错会一路静默，
        # 直到 BasePackage 取属性时才 AttributeError，而 init 标志没人检查，
        # 表现为任务跑到一半才崩
        ocr_data = raw_data.get("ocr_data")
        if isinstance(ocr_data, list):
            _check_ocr_data(ocr_data, resource_path)

    except Exception as e:
        logger.ui_error(f"资源文件夹{resource_path}加载失败: {str(e)}")
        return False

    return True


def _check_ocr_data(ocr_data: list, resource_path: str) -> None:
    """校验 ocr_data 条目；发现问题抛 ValueError，由 check_assets 统一转成提示"""
    seen: set = set()
    for index, item in enumerate(ocr_data):
        if not isinstance(item, dict):
            raise ValueError(f"{resource_path} ocr_data[{index}] 不是对象")

        name = item.get("name")
        if not name:
            raise ValueError(f"{resource_path} ocr_data[{index}] 缺少 name")
        if name in seen:
            raise ValueError(f"{resource_path} ocr_data name 重复: {name}")
        seen.add(name)

        # keyword 可以是字符串或字符串列表（列表表示任一命中即可），
        # 但不能为空：空 keyword 会让 match 恒不命中，且没有任何提示
        keyword = item.get("keyword")
        if isinstance(keyword, str):
            if not keyword.strip():
                raise ValueError(f"{resource_path} ocr_data[{name}] 的 keyword 为空")
        elif isinstance(keyword, list):
            if not keyword or not all(isinstance(k, str) and k.strip() for k in keyword):
                raise ValueError(f"{resource_path} ocr_data[{name}] 的 keyword 列表非法: {keyword!r}")
        else:
            raise ValueError(f"{resource_path} ocr_data[{name}] 的 keyword 类型非法: {type(keyword).__name__}")

        region = item.get("region")
        if region is not None:
            if not isinstance(region, list) or len(region) != 4 or not all(isinstance(v, int) for v in region):
                raise ValueError(f"{resource_path} ocr_data[{name}] 的 region 非法: {region!r}")

    logger.info(f"{resource_path} ocr_data 校验通过（{len(ocr_data)} 条）")
