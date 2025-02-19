from .utils import Package, check_package


class YuLing(Package):
    resource_path = "yuling"

    image_keys = {
        "start": "IMAGE_START",
        "title": "IMAGE_TITLE",
    }


def test_yuling():
    check_package(YuLing)
