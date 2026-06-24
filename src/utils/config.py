import yaml
from pydantic import BaseModel

from .application import RESOURCE_DIR_PATH, RESOURCE_JA_DIR_PATH, USER_DATA_DIR_PATH
from .log import logger

_game_language_list = ["国服", "日服"]
"""游戏语言"""
_update_download_list = ["镜像站", "GitHub"]
"""下载线路"""
_xuanshangfengyin_list = ["接受", "拒绝", "忽略", "关闭"]
"""悬赏封印"""
_shortcut_start_stop_list = [
    "无",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "F10",
    "F11",
    "F12",
]
"""快捷键-开始/停止"""
_interaction_mode_list = ["前台", "后台"]
"""交互模式"""
# 前台/后台的子配置
_frontend_sub_config = {
    "force_window": [True, False],
}
_backend_sub_config = {
    "prevent_sleep": [True, False],
    "screenshot_method": ["BitBlt", "PrintWindow"],
}


class FrontendConfig(BaseModel):
    """前台配置"""

    force_window: bool = True


class BackendConfig(BaseModel):
    """后台配置"""

    prevent_sleep: bool = True
    screenshot_method: str = "BitBlt"


class InteractionModeConfig(BaseModel):
    """交互模式配置"""

    mode: str = _interaction_mode_list[0]
    frontend: FrontendConfig = FrontendConfig()
    backend: BackendConfig = BackendConfig()


class DefaultConfig(BaseModel):
    """默认配置，用于UI显示选项"""

    game_language: list = _game_language_list
    """游戏服务器"""
    auto_update: bool = True
    """自动更新"""
    update_download: list = _update_download_list
    """下载线路"""
    xuanshangfengyin: list = _xuanshangfengyin_list
    """悬赏封印"""
    remember_last_choice: bool = False
    """记住上次选择"""
    shortcut_start_stop: list = _shortcut_start_stop_list
    """快捷键-开始/停止"""
    win_toast: bool = True
    """是否启用系统通知"""
    interaction_mode: dict = {
        "mode": _interaction_mode_list,
        "frontend": _frontend_sub_config,
        "backend": _backend_sub_config,
    }
    """交互模式"""
    function_order: list = []
    """功能排序默认值"""


default_config = DefaultConfig()


class UserConfig(BaseModel):
    """用户配置"""

    game_language: str = _game_language_list[0]
    """游戏服务器"""
    auto_update: bool = True
    """自动更新"""
    update_download: str = _update_download_list[0]
    """下载线路"""
    xuanshangfengyin: str = _xuanshangfengyin_list[0]
    """悬赏封印"""
    remember_last_choice: bool = False
    """记忆上次所选功能"""
    last_function: str = ""
    """上次选择的功能名（GameFunction.name），与remember_last_choice配合使用"""
    shortcut_start_stop: str = _shortcut_start_stop_list[0]
    """快捷键-开始/停止"""
    win_toast: bool = True
    """系统通知"""
    interaction_mode: InteractionModeConfig = InteractionModeConfig()
    """交互模式"""
    function_order: list[str] = []
    """功能排序，可通过GameFunctionSelectorWidget修改"""


class Config:
    """配置"""

    config_path = USER_DATA_DIR_PATH / "config.yaml"

    def __init__(self):
        self.user: UserConfig = UserConfig()
        self.data_error: int = 0
        self.resource_dir = RESOURCE_DIR_PATH
        self._init()

    def _init(self) -> None:
        """初始化"""
        if self.config_path.is_file():
            logger.info("Find config file.")
            data = self._check_outdated(self._read())
            # 注意：isinstance(True, int) 为 True，需先排除 bool 类型
            # TODO v2.2：删除兼容代码
            val = data.get("remember_last_choice")
            if isinstance(val, int) and not isinstance(val, bool):
                data["remember_last_choice"] = val == 0
            self.user = UserConfig(**data)
            if self.data_error:
                logger.warning("Data error, reset config.")
                self._save(self.user)
        else:
            logger.ui_warn("Cannot find config file.")
            self._save(self.user)
            logger.ui("create file config.yaml success.")

        if self.user.game_language == "日服":
            self.resource_dir = RESOURCE_JA_DIR_PATH

    def _read(self) -> dict:
        with open(self.config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _save(self, data) -> bool:
        if isinstance(data, UserConfig):
            data = data.model_dump()
        if isinstance(data, dict):
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, indent=4, allow_unicode=True, sort_keys=False)
        else:
            logger.ui_error("file config.yaml save failed.")
            return False
        return True

    def show_log(self):
        logger.info(f"配置更新完成\n{yaml.dump(self.user.model_dump(), allow_unicode=True, sort_keys=False)}")

    def update(self, key: str, value: str) -> None:
        """设置项更新

        参数:
            key (str): 设置项，可以是一级("xuanshangfengyin")或二级("notifications.sound")或三级("interaction_mode.frontend.force_window")
            value (str): 属性

        示例：
        ``` python
            config.update("interaction_mode.mode", "后台")
            config.update("interaction_mode.frontend.force_window", False)
            config.update("interaction_mode.backend.prevent_sleep", False)
        ```
        """
        logger.info(f"配置项 [{key}] 更新为 [{value}]")
        config_dict = self.user.model_dump()

        keys = key.split(".")
        target = config_dict
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value

        self.user = UserConfig.model_validate(config_dict)
        self._save(self.user.model_dump())

    def _check_outdated(self, data: dict) -> dict:
        """仅检查不符合配置项的部分，不存在的设置项可以通过UserConfig的model_dump()方法获取默认值"""

        def validate(value, default_value):
            # 如果 default 是列表，表示候选值
            if isinstance(default_value, list):
                if value not in default_value:
                    return default_value[0], True
                return value, False
            # 如果 default 是字典，递归检查
            elif isinstance(default_value, dict):
                fixed = {}
                changed = False
                for k, v in default_value.items():
                    sub_val, sub_changed = validate(value.get(k), v) if isinstance(value, dict) else (v, True)
                    fixed[k] = sub_val
                    if sub_changed:
                        changed = True
                return fixed, changed
            # 其他类型，直接返回
            return value, False

        for key, default_value in default_config.model_dump().items():
            if key not in data:
                continue
            # function_order 是列表类型，不走候选值校验逻辑
            if key == "function_order":
                continue
            fixed_value, changed = validate(data[key], default_value)
            if changed:
                data[key] = fixed_value
                self.data_error += 1
        return data


config = Config()
