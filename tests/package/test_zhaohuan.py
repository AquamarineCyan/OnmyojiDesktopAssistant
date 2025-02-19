from .utils import Package, check_package


class ZhaoHuan(Package):
    resource_path = "zhaohuan"

    image_keys = {
        "title": "IMAGE_TITLE",
    }

    ocr_keys = {
        "title": "OCR_TITLE",
        "zhaohuan": "OCR_ZHAOHUAN",
        "queding": "OCR_QUEDING",
        "again": "OCR_AGAIN",
    }


def test_zhaohuan():
    check_package(ZhaoHuan)
