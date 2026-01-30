from .utils import Package, check_package


class BaiGuiYeXing(Package):
    resource_path = "baiguiyexing"


def test_baiguiyexing():
    check_package(BaiGuiYeXing)
