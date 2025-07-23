import json

import httpx

from .application import USER_DATA_DIR_PATH, VERSION, Connect
from .log import logger
from .mysignal import global_ms as ms

__all__ = ["get_local_update_record", "get_update_info"]

UPDATE_INFO_FILE = USER_DATA_DIR_PATH / "update_info.json"


def json_read(file_path: str):
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def json_write(file_path: str, data: dict):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_latest_update_info(_file):
    """获取最新更新信息"""
    try:
        response = httpx.get(Connect.releases_api, headers=Connect.headers)
        if response.status_code != 200:
            return
        _api_data = json.loads(response.text)

        _list = []
        for i in range(5):
            _version = _api_data[i]["tag_name"][1:]
            _body = _api_data[i]["body"]
            _dict = {}
            _dict.setdefault("version", _version)
            _dict.setdefault("body", _body)
            _list.append(_dict)

        json_write(_file, _list)
    except Exception as e:
        logger.ui_error(f"获取更新信息失败: {str(e)}")


def get_update_info():
    """获取更新记录"""
    if not USER_DATA_DIR_PATH.exists():
        USER_DATA_DIR_PATH.mkdir(parents=True)

    file = UPDATE_INFO_FILE
    if file.exists():
        _update_info = json_read(file)
        _version = ".".join(VERSION.split(".")[:3])  # 基础版本号
        if _update_info[0]["version"] == _version:
            return

    get_latest_update_info(file)


def get_local_update_record():
    """获取本地更新记录"""
    return json_read(UPDATE_INFO_FILE)
