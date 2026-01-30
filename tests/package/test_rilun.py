from .utils import Package, check_package


class RiLun(Package):
    resource_path = "rilun"


def test_rilun():
    check_package(RiLun)
