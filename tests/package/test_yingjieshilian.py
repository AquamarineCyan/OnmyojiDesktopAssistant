from .utils import Package, check_package


class YingJieShiLian(Package):
    resource_path = "yingjieshilian"


def test_yingjieshilian():
    check_package(YingJieShiLian)
