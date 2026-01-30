from .utils import Package, check_package


class ZhaoHuan(Package):
    resource_path = "zhaohuan"


def test_zhaohuan():
    check_package(ZhaoHuan)
