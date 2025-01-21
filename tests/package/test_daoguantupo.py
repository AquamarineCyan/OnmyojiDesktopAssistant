from .utils import Package, check_package


class DaoGuanTuPo(Package):
    resource_path = "daoguantupo"
    resource_list = [
        "chuzhan",
        "daojishi",
        "guanzhan",
        "guanzhuzhan",
        "jijie",
        "qianwang",
        "shengyutuposhijian",
        "tiaozhan",
        "title",
        "zhanbao",
    ]


def test_daoguantupo():
    check_package(DaoGuanTuPo)
