from .utils import Package, check_package


class DaoGuanTuPo(Package):
    resource_path = "daoguantupo"

    image_keys = {
        "chuzhan": "IMAGE_CHUZHAN",
        "guanzhan": "IMAGE_GUANZHAN",
        "qianwang": "IMAGE_QIANWANG",
        "tiaozhan": "IMAGE_TIAOZHAN",
        "title": "IMAGE_TITLE",
        "zhanbao": "IMAGE_ZHANBAO",
        "zhuwei": "IMAGE_ZHUWEI",
        "zhuwei_gray": "IMAGE_ZHUWEI_GRAY",
    }

    ocr_keys = {
        "title": "OCR_TITLE",
        "daojishi": "OCR_DAOJISHI",
        "shengyutuposhijian": "OCR_SHENGYUTUPOSHIJIAN",
    }


def test_daoguantupo():
    check_package(DaoGuanTuPo)
