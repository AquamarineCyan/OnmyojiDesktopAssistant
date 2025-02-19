from .utils import Package, check_package


class TanSuo(Package):
    resource_path = "tansuo"

    image_keys = {
        "tansuo": "IMAGE_START",
        "chuzhanxiaohao": "IMAGE_CHUZHANXIAOHAO",
        "fight_boss": "IMAGE_FIGHT_BOSS",
        "fight_little_monster": "IMAGE_FIGHT_LITTLE_MONSTER",
        "kunnan_big": "IMAGE_KUNNAN_BIG",
        "quit_true": "IMAGE_QUIT_TRUE",
        "treasure_box": "IMAGE_TREASURE_BOX",
        "quit": "IMAGE_QUIT",
        "tansuo_28_0": "IMAGE_TANSUO_28_0",
        "tansuo_28": "IMAGE_TANSUO_28",
        "tansuo_28_title": "IMAGE_TANSUO_28_TITLE",
    }


def test_tansuo():
    check_package(TanSuo)
