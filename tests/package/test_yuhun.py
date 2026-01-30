from .utils import Package, check_package


class YuHun(Package):
    resource_path = "yuhun"


def test_yuhun():
    check_package(YuHun)
