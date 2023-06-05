from .utils import Package, check_package


class YuLing(Package):
    resource_path = "yuling"
    resource_list = [
        "title",
        "start",
    ]


def test_yuling():
    check_package(YuLing)
