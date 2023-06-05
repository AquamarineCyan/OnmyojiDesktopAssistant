from .utils import RESOURCE_DIR_PATH


def test_resource_dir():
    assert RESOURCE_DIR_PATH.exists()
    assert RESOURCE_DIR_PATH.is_dir()
