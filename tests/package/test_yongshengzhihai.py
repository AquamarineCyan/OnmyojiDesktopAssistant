from .utils import Package, check_package


class YongShengZhiHai(Package):
    resource_path = "yongshengzhihai"


def test_yongshengzhihai():
    check_package(YongShengZhiHai)
