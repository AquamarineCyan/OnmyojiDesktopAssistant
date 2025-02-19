from .utils import Package, check_package


class YeYuanHuo(Package):
    resource_path = "yeyuanhuo"

    image_keys = {
        "title": "IMAGE_TITLE",
        "start": "IMAGE_START",
    }


def test_yeyuanhuo():
    check_package(YeYuanHuo)
