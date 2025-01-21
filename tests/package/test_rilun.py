from .utils import Package, check_package


class RiLun(Package):
    resource_path = "rilun"
    resource_list = [
    ]


def test_rilun():
    check_package(RiLun)
