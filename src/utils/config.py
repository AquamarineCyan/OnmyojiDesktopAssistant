import yaml
from pydantic import BaseModel

from .application import USER_DATA_DIR_PATH
from .log import logger

_update_list = ["自动更新", "关闭"]
"""更新模式"""
_update_download_list = ["mirror", "GitHub"]
"""下载线路"""
_xuanshangfengyin_list = ["接受", "拒绝", "忽略", "关闭"]
"""悬赏封印"""
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
    window_style: list = _window_style_list
    remember_last_choice: int = -1
    shortcut_start_stop: list = _shortcut_start_stop_list
    win_toast: bool = True


class UserConfig(BaseModel):
    """用户配置"""

    update: str = _update_list[0]
    """更新模式"""
    update_download: str = _update_download_list[0]
    """下载线路"""
    xuanshangfengyin: str = _xuanshangfengyin_list[0]
    """悬赏封印"""
    window_style: str = _window_style_list[0]
    """界面风格"""
    remember_last_choice: int = -1
    """记忆上次所选功能 -1:关闭 0:开启 其他:各项功能"""
    shortcut_start_stop: str = _shortcut_start_stop_list[0]
    """快捷键-开始/停止"""
    win_toast: bool = True
    """系统通知"""


class Config:
    """配置"""

    config_path = USER_DATA_DIR_PATH / "config.yaml"

    def __init__(self):
        self.user: UserConfig = UserConfig()
        self.default: DefaultConfig = DefaultConfig()
        self.backend: bool = False  # 后台交互
        self.data_error: int = 0

    def config_yaml_init(self) -> None:
        """初始化"""
        if self.config_path.is_file():
            logger.info("Find config file.")
            data = self._check_outdated(self._read())
            self.user = UserConfig(**data)
            if self.data_error:
                logger.warning("Data error, reset config.")
                self._save(self.user)
        else:
            logger.ui_warn("Cannot find config file.")
            self._save(self.user)
            logger.ui("create file config.yaml success.")

    def _read(self) -> dict:
        with open(self.config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _save(self, data) -> bool:
        if isinstance(data, UserConfig):
            data = data.model_dump()
        if isinstance(data, dict):
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        else:
            logger.ui_error("file config.yaml save failed.")
            return False
        return True

    def update(self, key: str, value: str) -> None:
        """设置项更新

        参数:
            key (str): 设置项
            value (str): 属性
        """
        logger.info(f"Config setting [{key}] change to [{value}].")
        config_dict = self.user.model_dump()
        config_dict[key] = value
        logger.info(config_dict)
        self.user = UserConfig.model_validate(config_dict)
        self._save(self.user.model_dump())

    def _check_outdated(self, data: dict) -> dict:
        """仅检查不符合配置项的部分，不存在的设置项可以通过UserConfig的model_dump()方法获取默认值"""
        for key, value in self.default.model_dump().items():
            if not isinstance(value, list):
                continue
            if key in data.keys():
                if data.get(key) not in value:
                    data[key] = value[0]
                    self.data_error += 1
        return data


config = Config()
