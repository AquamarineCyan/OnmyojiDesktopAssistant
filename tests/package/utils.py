import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from ..utils import RESOURCE_DIR_PATH

# class AssetImage(BaseModel):
#     name: str = None
#     file: str = None
#     region: tuple[int, int, int, int] = None
#     score: float = 0.7
#     method: Literal["COLOR", "GRAYSCALE"] = "COLOR"


# class AssetOcr(BaseModel):
#     name: str = None
#     keyword: str = None
#     region: tuple[int, int, int, int] = None
#     score: float = 0.7
#     method: Literal["PERFACT", "INCLUDE"] = "PERFACT"


# def open_asset_file(file: Path) -> dict:
#     data = {}
#     try:
#         with open(str(file), encoding="utf-8") as f:
#             data = json.load(f)
#     except FileNotFoundError:
#         if "myresource" not in str(file):
#             print(f"文件未找到:{file}")
#     except json.JSONDecodeError:
#         print(f"{file}解析错误")
#     except (ValueError, TypeError):
#         print(f"{file}值错误或类型错误")
#     except Exception as e:
#         print(f"{file}打开失败: {e}")
#     finally:
#         return data


# def get_asset_data(resource_path) -> tuple[Path | dict]:
#     _full_path = RESOURCE_DIR_PATH / resource_path / "assets.json"
#     data_default = open_asset_file(_full_path)
#     return (_full_path, data_default)


# def load_asset(resource_path, type: str = Literal["image", "ocr"]) -> dict:
#     assets_file, data = get_asset_data(resource_path)
#     if data.get(f"{type}_data") is None:
#         return None

#     try:
#         if type == "image":
#             current_asset = data["current_path"]
#             data = data["image_data"]
#             for item in data:
#                 _item = item["file"]
#                 item["file"] = f"{current_asset}/{_item}"
#             return data
#         elif type == "ocr":
#             data = data["ocr_data"]
#             return data
#     except KeyError:
#         print(f"{assets_file}文件内容格式错误")
#     except Exception as e:
#         print(f"{assets_file}文件内容解析失败: {e}")

#     return {}


# def get_asset(dict_, name):
#     for item in dict_:
#         if item["name"] == name:
#             return item


class Package:
    resource_path: str = None
    image_keys = {}
    ocr_keys = {}

    # def load_asset(self):
    #     self.asset_image_list = load_asset(self.resource_path, "image")
    #     for key, sttr_name in self.image_keys.items():
    #         setattr(self, sttr_name, AssetImage(**get_asset(self.asset_image_list, key)))

    #     self.asset_ocr_list = load_asset(self.resource_path, "ocr")
    #     for key, sttr_name in self.ocr_keys.items():
    #         setattr(self, sttr_name, AssetOcr(**get_asset(self.asset_ocr_list, key)))


# def check_package(P: Package):
#     assert Path(RESOURCE_DIR_PATH / P.resource_path).exists()
#     P().load_asset()


def check_package(P: Package):
    print("")

    resource_path = Path(RESOURCE_DIR_PATH / P.resource_path)
    print(resource_path)
    assert resource_path.exists()

    assets_path = RESOURCE_DIR_PATH / P.resource_path / "assets.json"
    print(f"assets file [{assets_path}]")
    assert assets_path.exists()

    raw_data: dict = {}
    with open(str(assets_path), encoding="utf-8") as f:
        raw_data = json.load(f)

    current_asset = raw_data.get("current_path")
    if current_asset is None:
        return

    image_data = raw_data.get("image_data")
    assert isinstance(image_data, list)

    # image_data 可以不存在
    if isinstance(image_data, list):
        for item in image_data:
            file = Path(RESOURCE_DIR_PATH / current_asset / item["file"])
            print(f"resource file [{file}]")
            assert file.exists()
