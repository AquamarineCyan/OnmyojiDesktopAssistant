from .utils import Package, check_package


class GlobalResource(Package):
    resource_path = "global"
    
    image_keys = {
        "accept_invitation": "IMAGE_ACCEPT_INVITATION",
        "fail": "IMAGE_FAIL",
        "finish": "IMAGE_FINISH",
        "passenger_2": "IMAGE_PASSENGER_2",
        "passenger_3": "IMAGE_PASSENGER_3",
        "ready_new": "IMAGE_READY_NEW",
        "ready_old": "IMAGE_READY_OLD",
        "soul_overflow": "IMAGE_SOUL_OVERFLOW",
        "start_single": "IMAGE_START_SINGLE",
        "start_team": "IMAGE_START_TEAM",
        "tanchigui": "IMAGE_TANCHIGUI",
        "victory": "IMAGE_VICTORY",
        "xiezhanduiwu": "IMAGE_XIEZHAN_DUIWU",
    }

    ocr_keys = {
        "auto_fight": "OCR_AUTO_FIGHT",
        "cancel": "OCR_CANCEL",
        "confirm": "OCR_CONFIRM",
        "click_and_continue": "OCR_CLICK_AND_CONTINUE",
        "start": "OCR_START",
    }


def test_globalresource():
    check_package(GlobalResource)
