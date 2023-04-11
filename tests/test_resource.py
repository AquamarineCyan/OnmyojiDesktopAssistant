from pathlib import Path

resource_path = Path(__file__).parent.parent/"resource"
assert resource_path.exists()
assert resource_path.is_dir()

log_path = Path(__file__).parent / "log"
log_path.mkdir(parents=True, exist_ok=True)


class Package:
    def __init__(self, n: int = 0) -> None:
        self.scene_name = "tests"
        self.n: int = 0
        self.max: int = n
        self.resource_path = "tests"
        self.resource_list: list = []


def test_resource():
    from package import (
        baiguiyexing,
        daoguantupo,
        huodong,
        jiejietupo,
        rilun,
        xuanshangfengyin,
        yeyuanhuo,
        yongshengzhihai,
        yuhun,
        yuling,
        zhaohuan
    )

    T: Package
    for T in [
        baiguiyexing.BaiGuiYeXing(),
        daoguantupo.DaoGuanTuPo(),
        huodong.HuoDong(),
        jiejietupo.JieJieTuPo(),
        rilun.RiLun(),
        xuanshangfengyin.XuanShangFengYin(),
        yeyuanhuo.YeYuanHuo(),
        yongshengzhihai.YongShengZhiHai(),
        yuhun.YuHun(),
        yuling.YuLing(),
        zhaohuan.ZhaoHuan()
    ]:
        assert Path(resource_path / T.resource_path).exists()
        assert isinstance(T.resource_list, list)
        for i in range(len(T.resource_list)):
            resource: Path = resource_path / T.resource_path / f"{T.resource_list[i]}.png"
            print(resource)
            assert resource.exists()
            assert resource.is_file()
