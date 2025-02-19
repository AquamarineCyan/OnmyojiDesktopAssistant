from .utils import Package, check_package


class JieJieTuPo(Package):
    resource_path = "jiejietupo"

    image_keys = {
        "title": "IMAGE_TITLE",
    }


def test_jiejietupo():
    check_package(JieJieTuPo)
