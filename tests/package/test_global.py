from .utils import Package, check_package


class GlobalResource(Package):
    resource_path = "global"


def test_globalresource():
    check_package(GlobalResource)
