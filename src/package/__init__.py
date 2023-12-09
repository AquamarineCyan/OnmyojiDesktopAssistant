from .baiguiyexing import BaiGuiYeXing
from .daoguantupo import DaoGuanTuPo
from .huodong import HuoDong
from .jiejietupo import JieJieTuPo, JieJieTuPoGeRen, JieJieTuPoYinYangLiao
from .juexing import JueXing
from .qiling import QiLing
from .rilun import RiLun
from .tansuo import TanSuo
from .xuanshangfengyin import XuanShangFengYin, task_xuanshangfengyin
from .yeyuanhuo import YeYuanHuo
from .yongshengzhihai import YongShengZhiHai, YongShengZhiHaiTeam
from .yuhun import YuHun, YuHunSingle, YuHunTeam
from .yuling import YuLing
from .zhaohuan import ZhaoHuan
from .utils import FightResource

__all__ = [
    "FightResource",
    "BaiGuiYeXing",
    "DaoGuanTuPo",
    "HuoDong",
    # "JieJieTuPo",
    "JieJieTuPoGeRen",
    "JieJieTuPoYinYangLiao",
    "JueXing",
    "QiLing",
    "RiLun",
    "TanSuo",
    # "XuanShangFengYin",
    "task_xuanshangfengyin",
    "YeYuanHuo",
    "YuLing",
    "YongShengZhiHai",
    "YongShengZhiHaiTeam",
    "YuHun",
    "YuHunSingle",
    "YuHunTeam",
    "ZhaoHuan",
    "get_package_resource_list",
]


def get_package_resource_list():
    print("get_package_resource_list")
    return [
        FightResource,
        BaiGuiYeXing,
        DaoGuanTuPo,
        HuoDong,
        JieJieTuPo,
        JueXing,
        QiLing,
        RiLun,
        TanSuo,
        XuanShangFengYin,
        YeYuanHuo,
        YongShengZhiHai,
        YuHun,
        YuLing,
        ZhaoHuan
    ]
