from .utils import Package, check_package


class YuHun(Package):
    resource_path = "yuhun"
    resource_list = [
        "title_10",
        "title_11",
        "title_12",
        "finish_2000",
        "finish_damage",
        "finish_damage_2000",
    ]


def test_yuhun():
    check_package(YuHun)
