from .utils import Package, check_package


class HuoDong(Package):
    resource_path = "huodong"
    resource_list = [
        "title",
        "start",
    ]


def test_huodong():
    check_package(HuoDong)
