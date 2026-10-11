import json
from typing import Any

import httpx

from .application import ANNOUNCEMENT_CACHE_FILE, ANNOUNCEMENT_URL, Connect
from .config import config
from .decorator import run_in_thread
from .log import logger
from .signals import signal_manager

MAX_ANNOUNCEMENT_ID: int = 2_000_000_000
"""公告 id 上限

`mark_as_read` 会把 id 写进用户配置。若完全信任远端 id，一个极大值就能
让「比本地 id 更新」的判断永远为假，之后所有公告都被永久压制。
"""

MAX_CONTENT_LENGTH: int = 20_000
"""单条公告正文的字符上限（防远端灌入超长文本撑爆 GUI）"""


def _validate(raw: Any) -> list[dict] | None:
    """校验并规整远端/缓存里的公告结构

    公告与二进制更新包走同一批第三方镜像站，因此不能把它当作可信输入：
    缺 `id` 会在排序时抛 KeyError，`id` 为字符串会在比较时抛 TypeError，
    而这条链路跑在守护线程里，异常此前是完全静默的。
    """
    if not isinstance(raw, list):
        logger.warning("公告结构非法：announcements 不是列表")
        return None

    valid: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            logger.warning("公告结构非法：条目不是对象")
            continue
        item_id = item.get("id")
        if isinstance(item_id, bool) or not isinstance(item_id, int):
            logger.warning(f"公告结构非法：id 不是整数 ({item_id!r})")
            continue
        if not 0 < item_id <= MAX_ANNOUNCEMENT_ID:
            logger.warning(f"公告结构非法：id 超出允许范围 ({item_id})")
            continue
        content = item.get("content")
        if not isinstance(content, str) or not content:
            logger.warning(f"公告 {item_id} 结构非法：content 为空或非字符串")
            continue
        title = item.get("title")
        entry = {
            "id": item_id,
            "content": content[:MAX_CONTENT_LENGTH],
            "title": title if isinstance(title, str) else "",
        }
        if isinstance(item.get("time"), str):
            entry["time"] = item["time"]
        valid.append(entry)

    return sorted(valid, key=lambda x: x["id"])


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
            if not isinstance(data, dict):
                logger.warning(f"公告结构非法 [{url}]: 顶层不是对象")
                continue
            announcements = _validate(data.get("announcements", []))
            if announcements is None:
                continue
            logger.info(f"获取公告成功 [{url}]: 共 {len(announcements)} 条")
            return announcements
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
            if not isinstance(data, dict):
                logger.warning("公告缓存结构非法：顶层不是对象")
                return []
            validated = _validate(data.get("announcements", []))
            return validated or []
    except Exception as e:
        logger.warning(f"读取公告缓存失败: {e}")
    return []


def _write_cache(announcements: list[dict]):
    """写入本地缓存公告"""
    try:
        if not ANNOUNCEMENT_CACHE_FILE.parent.exists():
            ANNOUNCEMENT_CACHE_FILE.parent.mkdir(parents=True)
        # 先写临时文件再替换：进程被杀时不会留下半截 JSON
        tmp = ANNOUNCEMENT_CACHE_FILE.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"announcements": announcements}, f, ensure_ascii=False, indent=4)
        tmp.replace(ANNOUNCEMENT_CACHE_FILE)
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
    try:
        announcements = fetch_announcements()
    except Exception as e:
        # 这条链路跑在守护线程里，任何未捕获异常都不会有人看到
        logger.error(f"获取公告失败: {e}", exc_info=True)
        return []
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
    signal_manager.announcement.show_ui.emit(new_list)


def show_all_announcements():
    """手动查看全部公告（仅显示本地缓存）"""
    announcements = _read_cache()
    if not announcements:
        logger.ui_warn("暂无公告")
        return
    signal_manager.announcement.show_ui.emit(announcements)


def mark_as_read(latest_id: int):
    """阅读完毕后更新本地已读 id"""
    if isinstance(latest_id, bool) or not isinstance(latest_id, int):
        logger.warning(f"忽略非法的已读公告 id: {latest_id!r}")
        return
    if not 0 < latest_id <= MAX_ANNOUNCEMENT_ID:
        logger.warning(f"忽略超出范围的已读公告 id: {latest_id}")
        return
    if latest_id > config.user.announcement_id:
        config.update("announcement_id", latest_id)
