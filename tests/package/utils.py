import json
from pathlib import Path

from ..utils import RESOURCE_DIR_PATH


class Package:
    resource_path: str


def check_package(P: Package):
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

    # image_data 可以不存在
    if isinstance(image_data, list):
        for item in image_data:
            file = Path(RESOURCE_DIR_PATH / current_asset / item["file"])
            print(f"resource file [{file}]")
            assert file.exists()
