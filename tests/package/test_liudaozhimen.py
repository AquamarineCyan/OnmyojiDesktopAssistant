from .utils import Package, check_package


class LiuDaoZhiMen(Package):
    resource_path = "liudaozhimen"
    resource_list = [
        "determine",
        "fight",
        "fight_ready_quit",
        "fight_ready_refresh",
        "imitation",
        "open",
        "shop_refresh",
        "start",
    ]


def test_liudaozhimen():
    check_package(LiuDaoZhiMen)
