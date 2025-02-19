from .utils import Package, check_package


class YongShengZhiHai(Package):
    resource_path = "yongshengzhihai"

    image_keys = {
        "passenger": "IMAGE_PASSENGER",
        "title": "IMAGE_TITLE",
        "start_team": "IMAGE_START_TEAM",
    }


def test_yongshengzhihai():
    check_package(YongShengZhiHai)
