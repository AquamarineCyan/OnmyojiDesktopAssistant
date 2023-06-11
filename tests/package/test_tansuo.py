from .utils import Package, check_package


class TanSuo(Package):
    resource_path = "tansuo"
    resource_list = [
        "chuzhanxiaohao",
        "fighting",
        "fighting_boss",
        "kunnan_big",
        "quit",
        "quit_true",
        "tansuo",
        "tansuo_28",
        "tansuo_28_0",
        "tansuo_28_title",
        "treasure_box",
    ]


def test_tansuo():
    check_package(TanSuo)
