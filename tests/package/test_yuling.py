from .utils import Package, check_package


class YuLing(Package):
    resource_path = "yuling"


def test_yuling():
    check_package(YuLing)
