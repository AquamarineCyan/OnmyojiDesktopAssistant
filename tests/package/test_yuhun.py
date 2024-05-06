from .utils import Package, check_package


class YuHun(Package):
    resource_path = "yuhun"
    resource_list = [
        "title_10",
        "title_11",
        "title_12",
        "xiezhanduiwu",
        "passenger_2",
        "passenger_3",
        "start_team",
        "start_single",
        "fighting",
        "fighting_linshuanghanxue",
        "fighting_shenfa",
        "finish_damage",
        "finish_damage_2000",
        "finish_damage_shenfa",
    ]


def test_yuhun():
    check_package(YuHun)
