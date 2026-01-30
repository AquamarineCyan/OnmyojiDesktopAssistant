from .utils import Package, check_package


class JieJieTuPo(Package):
    resource_path = "jiejietupo"


def test_jiejietupo():
    check_package(JieJieTuPo)
