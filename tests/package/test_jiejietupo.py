from .utils import Package, check_package


class JieJieTuPo(Package):
    resource_path = "jiejietupo"
    resource_list = [
        "fail",
        "fangshoujilu",
        "geren",
        "jingong",
        "lock",
        "queding",
        "shuaxin",
        "title",
        "tupojilu",
        "unlock",
        "xunzhang_0",
        "xunzhang_1",
        "xunzhang_2",
        "xunzhang_3",
        "xunzhang_4",
        "xunzhang_5",
        "yinyangliao",
    ]


def test_jiejietupo():
    check_package(JieJieTuPo)
