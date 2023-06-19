from .utils import Package, check_package


class QiLing(Package):
    resource_path = "qiling"
    resource_list = [
        "start",
    ]


def test_qiling():
    check_package(QiLing)
