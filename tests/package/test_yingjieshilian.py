from .utils import Package, check_package


class YingJieShiLian(Package):
    resource_path = "yingjieshilian"

    image_keys = {
        "exp_start": "exp_IMAGE_START",
        "exp_title": "exp_IMAGE_TITLE",
        "main_title":"main_IMAGE_TITLE",
        "main_goto_exp": "main_IMAGE_GOTO_EXP",
        "main_goto_skill":"main_IMAGE_GOTO_SKILL",
        "skill_choose_attribute":"IMAGE_CHOOSE_ATTR",
        "skill_choose_buff":"IMAGE_CHOOSE_BUFF",
        "skill_choose_buff_ensure":"IMAGE_CHOOSE_BUFF_ENSURE",
        "skill_first_remain":"IMAGE_FIRST_REMAIN",
        "skill_start":"skill_IMAGE_START",
        "skill_title":"skill_IMAGE_TITLE",
    }

    ocr_keys = {
        "main_title": "OCR_MAIN_TITLE"
    }


def test_yingjieshilian():
    check_package(YingJieShiLian)
