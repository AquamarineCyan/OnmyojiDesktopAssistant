from .utils import Package, check_package


class XuanShangFengYin(Package):
    resource_path = "xuanshangfengyin"
    resource_list = [
        "title",
        "xuanshang_accept",
        "xuanshang_refuse",
        "xuanshang_ignore",
    ]


def test_xuanshangfengyin():
    check_package(XuanShangFengYin)
