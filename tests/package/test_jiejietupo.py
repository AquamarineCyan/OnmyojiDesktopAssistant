from .utils import Package, check_package


class JieJieTuPo(Package):
    resource_path = "jiejietupo"
    resource_list = [
        "fail",
        "fangshoujilu",
        "fighting_fail",
        "geren",
        "jingong",
        "queding",
        "shuaxin",
        "title",
        "tupojilu",
        "victory",
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
