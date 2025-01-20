from .utils import Package, check_package


class YongShengZhiHai(Package):
    resource_path = "yongshengzhihai"
    resource_list = [
        "title_team",
        "passenger",
        "start_team",
    ]


def test_yongshengzhihai():
    check_package(YongShengZhiHai)
