from .utils import Package, check_package


class QiLing(Package):
    resource_path = "qiling"
    resource_list = [
        "start_tancha",
        "start_jieqi",
        "zhenmushou",
        "xiaohei",
        "huoling",
        "ciqiu",
    ]


def test_qiling():
    check_package(QiLing)
