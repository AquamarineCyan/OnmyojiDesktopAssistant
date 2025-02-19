from .utils import Package, check_package


class QiLing(Package):
    resource_path = "qiling"

    image_keys = {
        "mingqizhaohuan": "IMAGE_MINGQIZHAOHUAN",
        "queding": "IMAGE_QUEDING",
        "start_jieqi": "IMAGE_START_JIEQI",
        "start_tancha": "IMAGE_START_TANCHA",
        "title": "IMAGE_TITLE",
        "zhenmushou": "IMAGE_ZHENMUSHOU",
        "zhenmushou_mingqishi": "IMAGE_ZHENMUSHOU_MINGQISHI",
    }


def test_qiling():
    check_package(QiLing)
