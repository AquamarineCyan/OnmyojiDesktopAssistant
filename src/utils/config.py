import yaml
from pydantic import BaseModel

from .application import APP_PATH, USER_DATA_DIR_PATH
from .log import logger

_update_list = ["自动更新", "关闭"]
"""更新模式"""
_update_download_list = ["ghproxy", "GitHub", "gitee"]
"""下载线路"""
_xuanshangfengyin_list = ["接受", "拒绝", "忽略", "关闭"]
"""悬赏封印"""
_fight_theme_list = ["自动", "怀旧", "简约"]
"""战斗主题"""
_window_style_list = ["Windows", "Fusion"]
"""界面风格"""
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


class DefaultConfig(BaseModel):
    """默认配置"""

    update: list = _update_list
    update_download: list = _update_download_list
    xuanshangfengyin: list = _xuanshangfengyin_list
    fight_theme: list = _fight_theme_list
    window_style: list = _window_style_list
    remember_last_choice: int = -1
    shortcut_start_stop: list = _shortcut_start_stop_list


class UserConfig(BaseModel):
    """用户配置"""

    update: str = _update_list[0]
    """更新模式"""
    update_download: str = _update_download_list[0]
    """下载线路"""
    xuanshangfengyin: str = _xuanshangfengyin_list[0]
    """悬赏封印"""
    fight_theme: str = _fight_theme_list[0]
    """战斗主题"""
    window_style: str = _window_style_list[0]
    """界面风格"""
    remember_last_choice: int = -1
    """记忆上次所选功能 -1:关闭 0:开启 1-12:各项功能"""
    shortcut_start_stop: str = _shortcut_start_stop_list[0]
    """快捷键-开始/停止"""


class Config:
    """配置"""

    config_path = USER_DATA_DIR_PATH / "config.yaml"

    def __init__(self):
        self.config_user: UserConfig = UserConfig()
        self.config_default: DefaultConfig = DefaultConfig()

    def config_yaml_init(self) -> None:
        """初始化"""
        # 移动旧版文件
        if (APP_PATH / "config.yaml").is_file():
            logger.info("Find old config file. Move it.")
            (APP_PATH / "config.yaml").rename(self.config_path)

        if self.config_path.is_file():
            logger.info("Find config file.")
            data = self._read_config_yaml()
            self.config_user = UserConfig(**data)
            self._check_outdated_config_data(data)
        else:
            logger.ui_warn("Cannot find config file.")
            self._save_config_yaml(self.config_user)

    def _read_config_yaml(self) -> dict:
        """读取配置文件"""
        with open(self.config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _save_config_yaml(self, data) -> bool:
        """保存配置文件"""
        if isinstance(data, UserConfig):
            data = data.model_dump()
        if isinstance(data, dict):
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        else:
            logger.ui_error("file config.yaml save failed.")
            return False
        return True

    def config_user_changed(self, key: str, value: str) -> None:
        """设置项更改

        参数:
            key (str): 设置项
            value (str): 属性
        """
        logger.info(f"Config setting [{key}] change to [{value}].")
        config_dict = self.config_user.model_dump()
        config_dict[key] = value
        logger.info(config_dict)
        self.config_user = UserConfig.model_validate(config_dict)
        self._save_config_yaml(self.config_user.model_dump())

    def _check_outdated_config_data(self, data: dict) -> None:
        # data = self.config_user.model_dump()
        _flag = False
        key = "更新模式"
        if key in data:
            value = data.get(key)
            data.pop(key)
            data.setdefault("update", value)
            _flag = True
        key = "下载线路"
        if key in data:
            value = data.get(key)
            data.pop(key)
            data.setdefault("update_download", value)
            _flag = True
        key = "悬赏封印"
        if key in data:
            value = data.get(key)
            data.pop(key)
            data.setdefault("xuanshangfengyin", value)
            _flag = True
        if _flag:
            self.config_user = UserConfig.model_validate(data)
            self._save_config_yaml(self.config_user)


config = Config()


def is_Chinese_Path() -> bool:
    """是否中文路径

    `opencv` 需要英文路径
    """
    from re import compile

    zhPattern = compile("[\u4e00-\u9fa5]+")
    match = zhPattern.search(str(APP_PATH))
    if not match:
        logger.info("English Path")
        return False
    logger.ui_error("Chinese Path")
    return True
