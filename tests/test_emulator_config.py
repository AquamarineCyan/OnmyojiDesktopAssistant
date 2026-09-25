"""Task 6b: 模拟器配置字段与截图方法枚举（T7/T8/T9 的前置依赖）。"""
from src.utils.config import BackendConfig, ScreenshotMethod, config


def test_screenshot_method_has_nemu_ipc():
    assert ScreenshotMethod.NEMU_IPC == "NemuIPC"


def test_backend_config_defaults():
    b = BackendConfig()
    assert b.emulator_type == "" and b.mumu_folder == "" and b.ipc_dll_override == ""


def test_config_update_roundtrip():
    before = config.user.interaction_mode.backend.mumu_folder
    config.update("interaction_mode.backend.mumu_folder", "E:\\MuMuPlayer")
    assert config.user.interaction_mode.backend.mumu_folder == "E:\\MuMuPlayer"
    config.update("interaction_mode.backend.mumu_folder", before)


def test_check_outdated_preserves_free_text_paths():
    """自由文本路径（安装目录/IPC DLL）不得被候选值校验清空。"""
    data = config.user.model_dump(mode="json")
    data["interaction_mode"]["backend"]["mumu_folder"] = "E:\\MuMuPlayer"
    data["interaction_mode"]["backend"]["ipc_dll_override"] = "E:\\MuMuPlayer\\ipc.dll"
    fixed = config._check_outdated(data)
    assert fixed["interaction_mode"]["backend"]["mumu_folder"] == "E:\\MuMuPlayer"
    assert fixed["interaction_mode"]["backend"]["ipc_dll_override"] == "E:\\MuMuPlayer\\ipc.dll"