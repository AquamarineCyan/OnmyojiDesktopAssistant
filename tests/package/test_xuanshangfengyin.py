from .utils import Package, check_package


class XuanShangFengYin(Package):
    resource_path = "xuanshangfengyin"

    image_keys = {
        "title": "IMAGE_TITLE",
        "accept": "IMAGE_ACCEPT",
        "ignore": "IMAGE_IGNORE",
        "refuse": "IMAGE_REFUSE",
    }


def test_xuanshangfengyin():
    check_package(XuanShangFengYin)
