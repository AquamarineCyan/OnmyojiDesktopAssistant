from .baiguiyexing import BaiGuiYeXing
from .daoguantupo import DaoGuanTuPo
from .douji import DouJi
from .global_resource import GlobalResource
from .huijuan import HuiJuan
from .huodong import HuoDong
from .jiejietupo import JieJieTuPo, JieJieTuPoGeRen, JieJieTuPoYinYangLiao
from .juexing import JueXing
from .liudaozhimen import LiuDaoZhiMen
from .qiling import QiLing
from .rilun import RiLun, RiLunSingle, RiLunTeam
from .tansuo import TanSuo
from .xuanshangfengyin import XuanShangFengYin
from .yeyuanhuo import YeYuanHuo
from .yingjieshilian import YingJieShiLianExp, YingJieShiLianSkill
from .yongshengzhihai import YongShengZhiHai, YongShengZhiHaiTeam
from .yuhun import YuHun, YuHunSingle, YuHunTeam
from .yuling import YuLing
from .zhaohuan import ZhaoHuan

__all__ = [
    "BaiGuiYeXing",
    "DaoGuanTuPo",
    "DouJi",
    "HuiJuan",
    "HuoDong",
    "JieJieTuPoGeRen",
    "JieJieTuPoYinYangLiao",
    "JueXing",
    "LiuDaoZhiMen",
    "QiLing",
    "RiLun",
    "RiLunSingle",
    "RiLunTeam",
    "TanSuo",
    "XuanShangFengYin",
    "YeYuanHuo",
    "YingJieShiLianExp",
    "YingJieShiLianSkill",
    "YongShengZhiHai",
    "YongShengZhiHaiTeam",
    "YuHun",
    "YuHunSingle",
    "YuHunTeam",
    "YuLing",
    "ZhaoHuan",
    "get_package_resource_list",
]


def get_package_resource_list():
    return [
        BaiGuiYeXing,
        DaoGuanTuPo,
        DouJi,
        GlobalResource,
        HuoDong,
        JieJieTuPo,
        JieJieTuPoGeRen,
        JieJieTuPoYinYangLiao,
        JueXing,
        LiuDaoZhiMen,
        QiLing,
        RiLun,
        RiLunSingle,
        RiLunTeam,
        TanSuo,
        XuanShangFengYin,
        YeYuanHuo,
        YingJieShiLianExp,
        YingJieShiLianSkill,
        YongShengZhiHai,
        YongShengZhiHaiTeam,
        YuHun,
        YuHunSingle,
        YuHunTeam,
        YuLing,
        ZhaoHuan,
    ]
