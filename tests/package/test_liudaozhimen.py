from .utils import Package, check_package


class LiuDaoZhiMen(Package):
    resource_path = "liudaozhimen"

    image_keys = {
        "determine": "IMAGE_DETERMINE",
        "fight": "IMAGE_FIGHT",
        "fight_choose_skill_refresh": "IMAGE_FIGHT_CHOOSE_SKILL_REFRESH",
        "quit": "IMAGE_QUIT",
        "imitation": "IMAGE_IMITATION",
        "open": "IMAGE_OPEN",
        "shop_refresh": "IMAGE_SHOP_REFRESH",
        "start": "IMAGE_START",
    }


def test_liudaozhimen():
    check_package(LiuDaoZhiMen)
