#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# config.py
"""配置"""

from re import compile

import yaml
from pydantic import BaseModel

from .application import APP_PATH, CONFIG_PATH
from .log import logger

_update_list = ["自动更新", "关闭"]
"""更新模式"""
_update_download_list = ["gitee", "ghproxy", "GitHub"]
"""下载线路"""
_xuanshangfengyin_list = ["接受", "拒绝", "忽略", "关闭"]
"""悬赏封印"""
_fight_theme_list = ["自动", "怀旧", "简约"]
"""战斗主题"""


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
    remember_last_choice: int = -1
    """记忆上次所选功能 -1:关闭 0:开启 1-12:各项功能"""


class DefaultConfig(BaseModel):
    """默认配置"""
    update: list = _update_list
    update_download: list = _update_download_list
    xuanshangfengyin: list = _xuanshangfengyin_list
    fight_theme: list = _fight_theme_list
    remember_last_choice: int = -1


class Config():
    """配置"""

    def __init__(self):
        self.config_user: UserConfig = UserConfig()
        self.config_default: DefaultConfig = DefaultConfig()

    def config_yaml_init(self) -> None:
        """初始化"""
        if CONFIG_PATH.is_file():
            logger.info("Find config file.")
            data = self._read_config_yaml()
            self.config_user = UserConfig(**data)
            self._check_outdated_config_data(data)
        else:
            logger.ui("Cannot find config file.", "warn")
            self._save_config_yaml(self.config_user)

    def _read_config_yaml(self) -> dict:
        """读取配置文件"""
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _save_config_yaml(self, data) -> bool:
        """保存配置文件"""
        if isinstance(data, UserConfig):
            data = data.model_dump()
        if isinstance(data, dict):
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        else:
            logger.ui("file config.yaml save failed.", "error")
            return False
        return True

    def check_config_data(self, data: dict) -> None:  # TODO Unused
        """检查配置字典的键值

        参数:
            data (dict): 待检查的字典
        """
        value = data["更新模式"]
        if value in _update_list:
            self.config_user.update = value

        value = data["下载线路"]
        if value in _update_download_list:
            self.config_user.update_download = value

        value = data["悬赏封印"]
        if value in _xuanshangfengyin_list:
            self.config_user.xuanshangfengyin = value

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
    zhPattern = compile(u'[\u4e00-\u9fa5]+')
    match = zhPattern.search(str(APP_PATH))
    if not match:
        logger.info("English Path")
        return False
    logger.ui("Chinese Path", "error")
    return True
