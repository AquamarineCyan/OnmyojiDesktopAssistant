from .utils import Package, check_package


class MiWen(Package):
    resource_path = "miwen"


def test_miwen():
    check_package(MiWen)
