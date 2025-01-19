from .utils import Package, check_package


class BaiGuiYeXing(Package):
    resource_path = "baiguiyexing"
    resource_list = [
        "title",
        "jinru",
        "choose",
        "kaishi",
        "baiguiqiyueshu",
    ]


def test_baiguiyexing():
    check_package(BaiGuiYeXing)
