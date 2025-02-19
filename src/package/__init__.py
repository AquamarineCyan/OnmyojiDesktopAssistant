from .baiguiyexing import BaiGuiYeXing
from .daoguantupo import DaoGuanTuPo
from .douji import DouJi
from .huodong import HuoDong
from .jiejietupo import JieJieTuPo, JieJieTuPoGeRen, JieJieTuPoYinYangLiao
from .juexing import JueXing
from .liudaozhimen import LiuDaoZhiMen
from .qiling import QiLing
from .rilun import RiLun, RiLunSingle, RiLunTeam
from .tansuo import TanSuo
from .utils import GlobalResource
from .xuanshangfengyin import XuanShangFengYin, task_xuanshangfengyin
from .yeyuanhuo import YeYuanHuo
from .yingjieshilian import BingZangMiJing, GuiBingYanWu
from .yongshengzhihai import YongShengZhiHai, YongShengZhiHaiTeam
from .yuhun import YuHun, YuHunSingle, YuHunTeam
from .yuling import YuLing
from .zhaohuan import ZhaoHuan

__all__ = [
    "GlobalResource",
    "BaiGuiYeXing",
    "DaoGuanTuPo",
    "DouJi",
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
    "task_xuanshangfengyin",
    "YeYuanHuo",
    "BingZangMiJing",
    "GuiBingYanWu",
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
        GlobalResource,
        BaiGuiYeXing,
        DaoGuanTuPo,
        DouJi,
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
        BingZangMiJing,
        GuiBingYanWu,
        YongShengZhiHai,
        YongShengZhiHaiTeam,
        YuHun,
        YuHunSingle,
        YuHunTeam,
        YuLing,
        ZhaoHuan,
    ]
