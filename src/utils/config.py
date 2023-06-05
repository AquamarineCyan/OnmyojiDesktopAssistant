#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# config.py
"""配置"""

from copy import deepcopy
from re import compile

import yaml

from .application import APP_PATH, CONFIG_PATH
from .log import log
from .mysignal import global_ms as ms


class Config():
    """配置"""

    config_default: dict = {
        "更新模式": ["ghproxy", "GitHub"],
        "悬赏封印": ["接受", "拒绝", "忽略", "关闭"],
    }

    def __init__(self):
        self.config_user: dict = None
        self.data_error: bool = False

    def config_yaml_init(self) -> None:
        if CONFIG_PATH.is_file():
            log.info("Find config file.")
            data = self._read_config_yaml()
            data = self._check_config_data(data)
            if self.data_error:
                self._save_config_yaml(data)
        else:
            log.error("Cannot find config file.")
            data = deepcopy(self.config_default)
            for key, value in data.items():
                data[key] = value[0] if isinstance(value, list) else value
            self._save_config_yaml(data)
        self.config_user = data
        self.setting_to_ui_qcombobox_update_func()

    def _read_config_yaml(self) -> dict:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def _save_config_yaml(self, data) -> bool:
        if isinstance(data, dict):
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        else:
            log.error("file config.yaml save failed.")
            return False
        return True

    def _check_config_data(self, data: dict) -> dict:
        """检查配置字典的键值，返回符合配置要求的字典

        Args:
            data (dict): 待检查的字典

        Returns:
            dict: 符合配置要求的字典
        """
        data, self.update_mode = self.dict_set_default(data, "更新模式")
        data, self.xuanshangfengyin_mode = self.dict_set_default(data, "悬赏封印")
        # TODO config.mode() for more config setting
        print("self.update_mode", self.update_mode)
        print("self.xuanshangfengyin_mode", self.xuanshangfengyin_mode)
        return data

    def dict_set_default(self, data: dict, key: str) -> tuple[dict, str]:
        """检查字典的键值是否存在，并设置默认值

        Args:
            data (dict): 待检查的字典
            key (str): 待匹配的键值

        Returns:
            dict: 新字典
        """
        value = self.config_default.get(key)
        if isinstance(value, list):
            if data.setdefault(key) not in value:
                data.pop(key)
                data.setdefault(key, value[0])
                self.data_error = True
        elif data.setdefault(key) != value:
            data.pop(key)
            data.setdefault(key, value)
            self.data_error = True
        return data, data.get(key)

    def config_user_changed(self, key: str, value: str) -> None:
        """设置项更改

        Args:
            key (str): 设置项
            value (str): 属性
        """
        self.config_user[key] = value
        log.info(self.config_user)
        self._save_config_yaml(self.config_user)

    def setting_to_ui_qcombobox_update_func(self) -> None:
        """配置项同步gui"""
        for item in self.config_default.keys():
            # log.info(f"{item} : {self.config_user[item]}")
            ms.setting_to_ui_update.emit(item, self.config_user[item])


config = Config()


def is_Chinese_Path() -> bool:
    """是否中文路径

    `opencv` 需要英文路径
    """
    zhPattern = compile(u'[\u4e00-\u9fa5]+')
    match = zhPattern.search(str(APP_PATH))
    if not match:
        log.info("English Path")
        return False
    log.error("Chinese Path")
    return True
