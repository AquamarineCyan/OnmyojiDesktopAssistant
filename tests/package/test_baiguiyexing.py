from .utils import Package, check_package


class BaiGuiYeXing(Package):
    resource_path = "baiguiyexing"

    image_keys = {
        "baiguiqiyueshu": "IMAGE_BAIGUIQIYUESHU",
        "jinru": "IMAGE_JINRU",
        "kaishi": "IMAGE_KAISHI",
        "title": "IMAGE_TITLE",
        "choose": "IMAGE_CHOOSE",
    }


def test_baiguiyexing():
    check_package(BaiGuiYeXing)
