from .utils import Package, check_package


class LiuDaoZhiMen(Package):
    resource_path = "liudaozhimen"

    image_keys = {
        "determine": "IMAGE_DETERMINE",
        "fight_ready_quit": "IMAGE_FIGHT_READY_QUIT",
        "fight_ready_refresh": "IMAGE_FIGHT_READY_REFRESH",
        "fight_ready_reset": "IMAGE_FIGHT_READY_RESET",
        "fight": "IMAGE_FIGHT",
        "imitation": "IMAGE_IMITATION",
        "open": "IMAGE_OPEN",
        "shop_refresh": "IMAGE_SHOP_REFRESH",
        "start": "IMAGE_START",
    }


def test_liudaozhimen():
    check_package(LiuDaoZhiMen)
