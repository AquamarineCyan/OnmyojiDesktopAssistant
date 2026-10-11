import os
import sys
from pathlib import Path

import httpx

from .version import DEBUG_VERSION, VERSION  # noqa: F401

APP_NAME: str = "OnmyojiDesktopAssistant"
"""程序名称"""

APP_EXE_NAME: str = f"{APP_NAME}.exe"
"""程序本体文件名称"""


def _resolve_app_path() -> Path:
    """程序本体路径

    打包运行时必须用 exe 所在目录：`Path.cwd()` 取决于启动方式
    （快捷方式的「起始位置」、计划任务、资源管理器），从别处启动时
    `data/`、`log/`、`models/` 会散落到无关目录，且快捷方式目标、
    更新包落盘位置、restart.bat 解析路径全部跟着跑偏。
    """
    if getattr(sys, "frozen", False):  # PyInstaller
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


APP_PATH: Path = _resolve_app_path()
"""程序本体路径"""

# 可写目录的根，可由环境变量覆盖。
# 测试跑 pytest 时用它把 data/ log/ models/ 重定向到临时目录，
# 避免读写开发者（以及 CI 工作区）的真实用户数据；资源目录仍从
# APP_PATH 解析，测试才能读到 src/resource。
DATA_ROOT: Path = Path(os.environ.get("ODAGUI_DATA_ROOT") or APP_PATH)
"""用户数据/日志/模型的根目录"""

USER_DATA_DIR_PATH: Path = DATA_ROOT / "data"
"""用户数据文件夹路径"""
if not USER_DATA_DIR_PATH.exists():
    USER_DATA_DIR_PATH.mkdir(parents=True)

LOG_DIR_PATH: Path = DATA_ROOT / "log"
"""日志文件夹路径"""
if not LOG_DIR_PATH.exists():
    LOG_DIR_PATH.mkdir(parents=True)

RESOURCE_DIR_PATH: Path = APP_PATH / "resource"
"""资源/素材文件夹路径"""
RESOURCE_JA_DIR_PATH: Path = APP_PATH / "resource_ja"
# 开发路径
if Path(APP_PATH / "src/resource").exists():
    RESOURCE_DIR_PATH = Path(APP_PATH / "src/resource")
if Path(APP_PATH / "src/resource_ja").exists():
    RESOURCE_JA_DIR_PATH = Path(APP_PATH / "src/resource_ja")

SCREENSHOT_DIR_PATH: Path = USER_DATA_DIR_PATH / "screenshot"
"""截图文件夹路径"""
if not SCREENSHOT_DIR_PATH.exists():
    SCREENSHOT_DIR_PATH.mkdir(parents=True)

MODEL_DIR_PATH: Path = DATA_ROOT / "models"
"""模型文件夹路径"""
if not MODEL_DIR_PATH.exists():
    MODEL_DIR_PATH.mkdir(parents=True)


class Connect:
    owner = "AquamarineCyan"
    repo = APP_NAME
    homepage = f"https://github.com/{owner}/{repo}"
    releases_api = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    API_TIMEOUT: float = 15.0
    """接口请求超时（秒）

    httpx 的缺省 timeout 是 5s，对走第三方镜像站的更新检查偏紧；
    但更关键的是不能不给——不给就是无限等待，守护线程会被永久挂住。
    """

    DOWNLOAD_TIMEOUT: "httpx.Timeout" = httpx.Timeout(connect=10.0, read=60.0, write=30.0, pool=10.0)
    """下载超时：连接可以等，读要留够缓冲时间

    这里直接构造 `httpx.Timeout`（而不是一个数字），好让 update.py 能复用它，
    避免各处各写一套不一致的超时。
    """

    mirror_station = [
        "https://ghfast.top/",
        "https://gh.nxnow.top/",
        "https://gh-proxy.com/",
        "https://free.cn.eu.org/",
        "https://gh.slw.im/",
    ]

    class MirrorChyan:
        """Mirror酱（MirrorChyan）镜像分发站配置

        官方文档: https://github.com/MirrorChyan/docs
        """

        resource = APP_NAME
        """资源ID"""
        home = "https://mirrorchyan.com/zh/get-start"
        """主页链接"""
        api = "https://mirrorchyan.com/api/resources"
        """接口基础地址"""
        user_agent = "ODAGUI"
        """客户端标识"""


HOME_PAGE_LINK = Connect.homepage
"""主页链接"""
HELP_DOC_LINK = "https://docs.qq.com/doc/DZUxDdm9ya2NpR2FY"
"""帮助文档链接"""
QQ_GROUP_LINK = "https://qm.qq.com/q/T5pnZ5tGAs"
"""QQ群链接"""

ICO_RESOURCE_PATH: str = ":/icon/buzhihuo.jpg"
"""图标路径（Qt资源）"""

UPDATE_INFO_FILE: Path = USER_DATA_DIR_PATH / "update_info.json"
"""更新记录文件"""
ANNOUNCEMENT_URL: str = f"https://raw.githubusercontent.com/{Connect.owner}/{Connect.repo}/main/announcements.json"
"""公告文件地址"""
ANNOUNCEMENT_CACHE_FILE: Path = USER_DATA_DIR_PATH / "announcements.json"
"""公告本地缓存文件"""
