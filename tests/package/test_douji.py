from .utils import Package, check_package


class DouJi(Package):
    resource_path = "douji"


def test_douji():
    check_package(DouJi)
