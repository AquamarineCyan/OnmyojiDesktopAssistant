from .utils import Package, check_package


class JieJieTuPo(Package):
    resource_path = "jiejietupo"

    image_keys = {
        "fail": "IMAGE_FAIL",
        "fangshoujilu": "IMAGE_FANGSHOUJILU",
        "geren": "IMAGE_GEREN",
        "jingong": "IMAGE_JINGONG",
        "lock": "IMAGE_LOCK",
        "queding": "IMAGE_QUEDING",
        "shuaxin": "IMAGE_SHUAXIN",
        "title": "IMAGE_TITLE",
        "tupojilu": "IMAGE_TUPOJILU",
        "unlock": "IMAGE_UNLOCK",
        "xunzhang_0": "IMAGE_XUNZHANG_0",
        "xunzhang_1": "IMAGE_XUNZHANG_1",
        "xunzhang_2": "IMAGE_XUNZHANG_2",
        "xunzhang_3": "IMAGE_XUNZHANG_3",
        "xunzhang_4": "IMAGE_XUNZHANG_4",
        "xunzhang_5": "IMAGE_XUNZHANG_5",
        "yinyangliao": "IMAGE_YINYANGLIAO",
        "zaicitiaozhan": "IMAGE_ZAICITIAOZHAN",
    }


def test_jiejietupo():
    check_package(JieJieTuPo)
