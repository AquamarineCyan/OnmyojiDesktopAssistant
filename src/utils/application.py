from pathlib import Path

from .version import DEBUG_VERSION, VERSION  # noqa: F401

APP_NAME: str = "OnmyojiDesktopAssistant"
"""程序名称"""

APP_EXE_NAME: str = f"{APP_NAME}.exe"
"""程序本体文件名称"""

APP_PATH: Path = Path().cwd()
"""程序本体路径"""

USER_DATA_DIR_PATH: Path = APP_PATH / "data"
"""用户数据文件夹路径"""
if not USER_DATA_DIR_PATH.exists():
    USER_DATA_DIR_PATH.mkdir(parents=True)

LOG_DIR_PATH: Path = APP_PATH / "log"
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

MODEL_DIR_PATH: Path = APP_PATH / "models"
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
