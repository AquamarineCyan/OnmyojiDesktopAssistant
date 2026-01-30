from .utils import Package, check_package


class XuanShangFengYin(Package):
    resource_path = "xuanshangfengyin"


def test_xuanshangfengyin():
    check_package(XuanShangFengYin)
