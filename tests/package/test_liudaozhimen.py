from .utils import Package, check_package


class LiuDaoZhiMen(Package):
    resource_path = "liudaozhimen"


def test_liudaozhimen():
    check_package(LiuDaoZhiMen)
