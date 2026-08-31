import json

import httpx

from .application import ANNOUNCEMENT_CACHE_FILE, ANNOUNCEMENT_URL, Connect
from .config import config
from .decorator import run_in_thread
from .log import logger
from .mysignal import global_ms as ms


def _fetch_remote() -> list[dict] | None:
    """从远端获取公告列表（依次尝试直连与镜像站），全部失败返回 None"""
    url_list = [ANNOUNCEMENT_URL]
    url_list.extend(f"{mirror}{ANNOUNCEMENT_URL}" for mirror in Connect.mirror_station)

    for i, url in enumerate(url_list):
        try:
            # 主站超时 3 秒，镜像站 2 秒
            timeout = 3 if i == 0 else 2
            logger.info(f"正在尝试获取公告: {url} (超时 {timeout}s)")
            response = httpx.get(url, headers=Connect.headers, timeout=timeout)
            if response.status_code != 200:
                logger.warning(f"获取公告失败 [{url}]: HTTP {response.status_code}")
                continue
            data = json.loads(response.text)
            announcements = data.get("announcements", [])
            logger.info(f"获取公告成功 [{url}]: 共 {len(announcements)} 条")
            return sorted(announcements, key=lambda x: x["id"])
        except Exception as e:
            logger.warning(f"获取公告异常 [{url}]: {e}")
            continue
    logger.warning("所有公告地址均获取失败")
    return None


def _read_cache() -> list[dict]:
    """读取本地缓存公告"""
    try:
        if ANNOUNCEMENT_CACHE_FILE.is_file():
            with open(ANNOUNCEMENT_CACHE_FILE, encoding="utf-8") as f:
                data = json.load(f)
                return sorted(data.get("announcements", []), key=lambda x: x["id"])
    except Exception as e:
        logger.warning(f"读取公告缓存失败: {e}")
    return []


def _write_cache(announcements: list[dict]):
    """写入本地缓存公告"""
    try:
        if not ANNOUNCEMENT_CACHE_FILE.parent.exists():
            ANNOUNCEMENT_CACHE_FILE.parent.mkdir(parents=True)
        with open(ANNOUNCEMENT_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"announcements": announcements}, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.warning(f"写入公告缓存失败: {e}")


def fetch_announcements() -> list[dict]:
    """获取公告列表：优先远端，失败时回退到本地缓存"""
    announcements = _fetch_remote()
    if announcements is not None:
        _write_cache(announcements)
        return announcements
    logger.warning("获取公告失败，使用本地缓存")
    return _read_cache()


def get_new_announcements() -> list[dict]:
    """获取比本地已读 id 更新的公告列表"""
    announcements = fetch_announcements()
    if not announcements:
        return []
    local_id = config.user.announcement_id
    return [a for a in announcements if a["id"] > local_id]


@run_in_thread
def check_announcements():
    """检查新公告，有新公告时通过信号展示"""
    new_list = get_new_announcements()
    if not new_list:
        return
    logger.ui(f"发现 {len(new_list)} 条新公告")
    ms.announcement.show_ui.emit(new_list)


def show_all_announcements():
    """手动查看全部公告（仅显示本地缓存）"""
    announcements = _read_cache()
    if not announcements:
        logger.ui_warn("暂无公告")
        return
    ms.announcement.show_ui.emit(announcements)


def mark_as_read(latest_id: int):
    """阅读完毕后更新本地已读 id"""
    if latest_id > config.user.announcement_id:
        config.update("announcement_id", latest_id)
