from .utils import Package, check_package


class GlobalResource(Package):
    resource_path = "global"
    resource_list = [
        "accept_invitation",
        "fail",
        "finish",
        "passenger_2",
        "passenger_3",
        "ready_new",
        "ready_old",
        "tanchigui",
        "victory",
    ]


def test_globalresource():
    check_package(GlobalResource)
