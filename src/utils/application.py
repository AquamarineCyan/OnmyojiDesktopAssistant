from pathlib import Path

from .version import VERSION  # noqa: F401

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


class Connect:
    owner = "AquamarineCyan"
    repo = APP_NAME
    homepage = f"https://github.com/{owner}/{repo}"
    releases_api = f"https://api.github.com/repos/{owner}/{repo}/releases"
    releases_latest_api = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    mirror_station = [
        "https://ghfast.top/",
        "https://gh.nxnow.top/",
        "https://ghproxy.net/",
        "https://gh-proxy.com/",
        "https://free.cn.eu.org/",
    ]


HOME_PAGE_LINK = Connect.homepage
"""主页链接"""
HELP_DOC_LINK = "https://docs.qq.com/doc/DZUxDdm9ya2NpR2FY"
"""帮助文档链接"""
QQ_GROUP_LINK = "https://qm.qq.com/q/T5pnZ5tGAs"
"""QQ群链接"""
