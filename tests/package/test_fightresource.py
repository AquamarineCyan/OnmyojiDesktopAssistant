from .utils import Package, check_package


class FightResource(Package):
    resource_path = "fight"
    resource_list = [
        "passenger_2",
        "passenger_3",
        "victory",
        "fail",
        "finish",
        "tanchigui",
        "accept_invitation",
        "ready_old",
        "ready_new",
    ]


def test_fightresource():
    check_package(FightResource)
