from pathlib import Path

from ..utils import RESOURCE_DIR_PATH


class Package:
    resource_path: str = None
    resource_list: list = []


def check_package(P: Package):
    assert Path(RESOURCE_DIR_PATH / P.resource_path).exists()
    assert isinstance(P.resource_list, list)
    for i in range(len(P.resource_list)):
        resource: Path = RESOURCE_DIR_PATH / P.resource_path / f"{P.resource_list[i]}.png"
        print(resource)
        assert resource.exists()
        assert resource.is_file()
