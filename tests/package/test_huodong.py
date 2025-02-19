from .utils import Package, check_package


class HuoDong(Package):
    resource_path = "huodong"

    image_keys = {
        "start": "IMAGE_START",
        "title": "IMAGE_TITLE",
        "result": "IMAGE_RESULT",
    }


def test_huodong():
    check_package(HuoDong)
