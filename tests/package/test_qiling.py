from .utils import Package, check_package


class QiLing(Package):
    resource_path = "qiling"

    image_keys = {
        "mingqizhaohuan": "IMAGE_MINGQIZHAOHUAN",
        "stone_add": "IMAGE_STONE_ADD",
        "stone_max": "IMAGE_STONE_MAX",
        "zhenmushou": "IMAGE_ZHENMUSHOU",
    }

    ocr_keys = {
        "tancha_start": "OCR_TANCHA_START",
        "title": "OCR_TITLE",
        "zhenmushou": "OCR_ZHENMUSHOU",
    }


def test_qiling():
    check_package(QiLing)
