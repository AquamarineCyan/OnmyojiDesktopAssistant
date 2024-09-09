from .baiguiyexing import BaiGuiYeXing
from .daoguantupo import DaoGuanTuPo
from .douji import DouJi
from .guibingyanwu import GuiBingYanWu
from .huodong import HuoDong
from .jiejietupo import JieJieTuPo, JieJieTuPoGeRen, JieJieTuPoYinYangLiao
from .juexing import JueXing
from .liudaozhimen import LiuDaoZhiMen
from .qiling import QiLing
from .rilun import RiLun
from .tansuo import TanSuo
from .xuanshangfengyin import XuanShangFengYin, task_xuanshangfengyin
from .yeyuanhuo import YeYuanHuo
from .yongshengzhihai import YongShengZhiHai, YongShengZhiHaiTeam
from .yuhun import YuHun, YuHunSingle, YuHunTeam
from .yuling import YuLing
from .zhaohuan import ZhaoHuan
from .utils import GlobalResource

__all__ = [
    "GlobalResource",
    "BaiGuiYeXing",
    "DaoGuanTuPo",
    "DouJi",
    "GuiBingYanWu",
    "HuoDong",
    # "JieJieTuPo",
    "JieJieTuPoGeRen",
    "JieJieTuPoYinYangLiao",
    "JueXing",
    "LiuDaoZhiMen",
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
        GlobalResource,
        BaiGuiYeXing,
        DaoGuanTuPo,
        HuoDong,
        GuiBingYanWu,
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
