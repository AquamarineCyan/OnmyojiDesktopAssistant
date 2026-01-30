from .utils import Package, check_package


class DaoGuanTuPo(Package):
    resource_path = "daoguantupo"


def test_daoguantupo():
    check_package(DaoGuanTuPo)
