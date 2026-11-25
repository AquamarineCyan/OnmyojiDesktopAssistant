import json
from pathlib import Path

import pytest

RESOURCE_DIR_PATH = Path(__file__).resolve().parents[2] / "src/resource"
RESOURCE_JA_DIR_PATH = Path(__file__).resolve().parents[2] / "src/resource_ja"


class Package:
    resource_path: str


def check_package(P: Package, resource_dir: Path = RESOURCE_DIR_PATH):
    resource_path = Path(resource_dir / P.resource_path)
    print(resource_path)
    assert resource_path.exists()

    assets_path = resource_dir / P.resource_path / "assets.json"
    print(f"assets file [{assets_path}]")
    assert assets_path.exists()

    raw_data: dict = {}
    with open(str(assets_path), encoding="utf-8") as f:
        raw_data = json.load(f)

    current_asset = raw_data.get("current_path")
    if current_asset is None:
        return

    image_data = raw_data.get("image_data")

    # image_data 可以不存在
    if isinstance(image_data, list):
        for item in image_data:
            file = Path(resource_dir / current_asset / item["file"])
            print(f"resource file [{file}]")
            assert file.exists()


class BaiGuiYeXing(Package):
    resource_path = "baiguiyexing"


class DaoGuanTuPo(Package):
    resource_path = "daoguantupo"


class DouJi(Package):
    resource_path = "douji"


class GlobalResource(Package):
    resource_path = "global"


class HuiJuan(Package):
    resource_path = "huijuan"


class HuoDong(Package):
    resource_path = "huodong"


class JieJieTuPo(Package):
    resource_path = "jiejietupo"


class JueXing(Package):
    resource_path = "juexing"


class LiuDaoZhiMen(Package):
    resource_path = "liudaozhimen"


class MiWen(Package):
    resource_path = "miwen"


class QiLing(Package):
    resource_path = "qiling"


class RiLun(Package):
    resource_path = "rilun"


class TanSuo(Package):
    resource_path = "tansuo"


class XiaJianAnYu(Package):
    resource_path = "xiajiananyu"


class XuanShangFengYin(Package):
    resource_path = "xuanshangfengyin"


class YeYuanHuo(Package):
    resource_path = "yeyuanhuo"


class YingJieShiLian(Package):
    resource_path = "yingjieshilian"


class YongShengZhiHai(Package):
    resource_path = "yongshengzhihai"


class YuHun(Package):
    resource_path = "yuhun"


class YuLing(Package):
    resource_path = "yuling"


class ZhaoHuan(Package):
    resource_path = "zhaohuan"


PACKAGES = [
    BaiGuiYeXing,
    DaoGuanTuPo,
    DouJi,
    GlobalResource,
    HuiJuan,
    HuoDong,
    JieJieTuPo,
    JueXing,
    LiuDaoZhiMen,
    MiWen,
    QiLing,
    RiLun,
    TanSuo,
    XiaJianAnYu,
    XuanShangFengYin,
    YeYuanHuo,
    YingJieShiLian,
    YongShengZhiHai,
    YuHun,
    YuLing,
    ZhaoHuan,
]


@pytest.mark.parametrize("package", PACKAGES, ids=lambda package: package.resource_path)
@pytest.mark.parametrize(
    "resource_dir",
    (RESOURCE_DIR_PATH, RESOURCE_JA_DIR_PATH),
    ids=("resource", "resource_ja"),
)
def test_package(package, resource_dir):
    check_package(package, resource_dir)
