from .utils import Package, check_package


class HuiJuan(Package):
    resource_path = "huijuan"


def test_huijuan():
    check_package(HuiJuan)
