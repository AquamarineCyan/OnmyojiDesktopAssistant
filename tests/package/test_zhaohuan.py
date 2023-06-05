from .utils import Package, check_package


class ZhaoHuan(Package):
    resource_path = "zhaohuan"
    resource_list = [
        "putongzhaohuan",
        "queding",
        "title",
        "zaicizhaohuan",
    ]


def test_zhaohuan():
    check_package(ZhaoHuan)
