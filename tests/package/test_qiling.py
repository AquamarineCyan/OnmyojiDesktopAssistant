from .utils import Package, check_package


class QiLing(Package):
    resource_path = "qiling"


def test_qiling():
    check_package(QiLing)
