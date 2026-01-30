from .utils import Package, check_package


class TanSuo(Package):
    resource_path = "tansuo"


def test_tansuo():
    check_package(TanSuo)
