from pathlib import Path

VERSION: str = "2.0.1"
"""版本号"""

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
# 开发路径
if Path(APP_PATH / "src/resource").exists():
    RESOURCE_DIR_PATH = Path(APP_PATH / "src/resource")
if not RESOURCE_DIR_PATH.exists():
    RESOURCE_DIR_PATH.mkdir(parents=True)

RESOURCE_GLOBAL_PATH = RESOURCE_DIR_PATH / "global"
"""通用资源路径"""

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
        "https://github.moeyy.xyz/",
        "https://ghproxy.net/",
        "https://gh-proxy.com/",
        "https://gh.pylas.xyz/",
    ]
    helpdoc = "https://docs.qq.com/doc/DZUxDdm9ya2NpR2FY"
