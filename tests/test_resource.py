from pathlib import Path

resource_path = Path(__file__).parent.parent/"resource"
assert resource_path.exists()
assert resource_path.is_dir()


def test_func():
    from package import huodong
    t = huodong.HuoDong()
    assert Path(resource_path / t.resource_path).exists()
    assert isinstance(t.scene_list, list)
    for i in range(len(t.scene_list)):
        assert Path(resource_path / t.resource_path / f"{t.scene_list[i]}.png").exists()
        assert Path(resource_path / t.resource_path / f"{t.scene_list[i]}.png").is_file()
