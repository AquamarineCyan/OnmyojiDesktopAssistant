from enum import Enum, StrEnum


class GameFunction(Enum):
    """游戏功能"""

    YUHUN = 1  # 御魂副本
    YONGSHENGZHIHAI = 2  # 永生之海副本
    YEYUANHUO = 3  # 业原火副本
    YULING = 4  # 御灵副本
    GERENTUPO = 5  # 个人突破
    LIAOTUPO = 6  # 寮突破
    DAOGUANTUPO = 7  # 道馆突破
    ZHAOHUAN = 8  # 普通召唤
    BAIGUIYEXING = 9  # 百鬼夜行
    HUODONG = 10  # 限时活动
    RILUN = 11  # 日轮副本
    TANSUO = 12  # 单人探索
    QILING = 13  # 契灵之境
    JUEXING = 14  # 觉醒副本
    LIUDAOZHIMEN = 15  # 六道之门速刷
    DOUJI = 16  # 斗技自动上阵
    YINGJIESHILIAN = 17  # 英杰试炼
    HUIJUAN = 18  # 绘卷刷分
    MIWEN = 19  # 每周秘闻


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

    BAI_ZHAN = "百战"
    JING_SU = "竞速"
