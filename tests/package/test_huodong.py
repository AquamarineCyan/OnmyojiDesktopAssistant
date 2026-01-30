from .utils import Package, check_package


class HuoDong(Package):
    resource_path = "huodong"


def test_huodong():
    check_package(HuoDong)
