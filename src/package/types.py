from enum import Enum, StrEnum


class GameFunction(Enum):
    """游戏功能"""

    YUHUN = "御魂副本"
    YONGSHENGZHIHAI = "永生之海副本"
    YEYUANHUO = "业原火副本"
    YULING = "御灵副本"
    GERENTUPO = "个人突破"
    LIAOTUPO = "寮突破"
    DAOGUANTUPO = "道馆突破"
    ZHAOHUAN = "普通召唤"
    BAIGUIYEXING = "百鬼夜行"
    HUODONG = "限时活动"
    RILUN = "日轮副本"
    TANSUO = "单人探索"
    QILING = "契灵之境"
    JUEXING = "觉醒副本"
    LIUDAOZHIMEN = "六道之门速刷"
    DOUJI = "斗技自动上阵"
    YINGJIESHILIAN = "英杰试炼"
    HUIJUAN = "绘卷刷分"
    MIWEN = "每周秘闻"


class QiLing(StrEnum):
    """契灵"""

    ZHEN_MU_SHOU = "镇墓兽"
    HUO_LING = "火灵"
    CI_QIU = "茨球"
    XIAO_HEI = "小黑"
    ZHEN_NV = "针女"
    TI_HUN = "薙魂"
    YUE_MO_TU = "月魔兔"
    HU_HUO = "狐火"


class Yingjie(StrEnum):
    """英杰"""

    YUAN_LAI_GUANG = "源赖光"
    TENG_YUAN_DAO_CHANG = "藤原道长"


class MiWenMode(StrEnum):
    """秘闻模式"""

    JING_SU = "竞速"
    BAI_ZHAN = "百战"
