from .utils import Package, check_package


class RiLun(Package):
    resource_path = "rilun"

    image_keys = {
        "title_3": "IMAGE_TITLE_3",
        "title_4": "IMAGE_TITLE_4",
    }


def test_rilun():
    check_package(RiLun)
