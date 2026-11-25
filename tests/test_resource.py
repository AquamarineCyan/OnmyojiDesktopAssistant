import pytest

from .package.test_package import RESOURCE_DIR_PATH, RESOURCE_JA_DIR_PATH


@pytest.mark.parametrize(
    "resource_dir",
    (RESOURCE_DIR_PATH, RESOURCE_JA_DIR_PATH),
    ids=("resource", "resource_ja"),
)
def test_resource_dir(resource_dir):
    assert resource_dir.exists()
    assert resource_dir.is_dir()
