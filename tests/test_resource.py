from pathlib import Path

resource_path = Path(__file__).parent.parent/"resource"
assert resource_path.exists()
assert resource_path.is_dir()


class Package:
    def __init__(self, n: int = 0) -> None:
        self.scene_name = "tests"
        self.resource_path = "tests"
        self.n = 0
        self.max = n
        self.scene_list: list = []


def test_func():
    from package import huodong
    from package import yuhun

    T: Package
    for T in [huodong.HuoDong(), yuhun.YuHun()]:
        assert Path(resource_path / T.resource_path).exists()
        assert isinstance(T.scene_list, list)
        for i in range(len(T.scene_list)):
            assert Path(resource_path / T.resource_path / f"{T.scene_list[i]}.png").exists()
            assert Path(resource_path / T.resource_path / f"{T.scene_list[i]}.png").is_file()
