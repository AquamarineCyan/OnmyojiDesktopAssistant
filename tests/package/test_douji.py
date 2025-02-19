from .utils import Package, check_package


class DouJi(Package):
    resource_path = "douji"

    OCR_keys = {
        "title": "OCR_TITLE",
        "fight": "OCR_FIGHT",
        "update_team": "OCR_UPDATE_TEAM",
        "intentional": "OCR_INTENTIONAL",
        "victory": "OCR_VICTORY",
        "fail": "OCR_FAIL",
        "level_up": "OCR_LEVEL_UP",
    }


def test_douji():
    check_package(DouJi)
