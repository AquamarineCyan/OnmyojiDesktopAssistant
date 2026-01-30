from .utils import Package, check_package


class YeYuanHuo(Package):
    resource_path = "yeyuanhuo"


def test_yeyuanhuo():
    check_package(YeYuanHuo)
