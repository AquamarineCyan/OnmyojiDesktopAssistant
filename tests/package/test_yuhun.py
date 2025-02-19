from .utils import Package, check_package


class YuHun(Package):
    resource_path = "yuhun"

    image_keys = {
        "finish_2000": "IMAGE_FINISH_2000",
        "finish_damage": "IMAGE_FINISH_DAMAGE",
        "finish_damage_2000": "IMAGE_FINISH_DAMAGE_2000",
        "title_10": "IMAGE_TITLE_10",
        "title_11": "IMAGE_TITLE_11",
        "title_12": "IMAGE_TITLE_12",
    }


def test_yuhun():
    check_package(YuHun)
