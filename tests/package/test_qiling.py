from .utils import Package, check_package


class QiLing(Package):
    resource_path = "qiling"

    image_keys = {
        "stone_add": "IMAGE_STONE_ADD",
        "stone_max": "IMAGE_STONE_MAX",
        "zhaohuan": "IMAGE_ZHAOHUAN",
    }

    ocr_keys = {
        "tancha_start": "OCR_TANCHA_START",
        "title": "OCR_TITLE",
        "jieqi_give_up": "OCR_JIEQI_GIVE_UP",
    }


def test_qiling():
    check_package(QiLing)
