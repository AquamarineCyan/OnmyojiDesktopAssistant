import subprocess

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from ..utils.application import APP_NAME, LOG_DIR_PATH

# 允许由公告正文打开的外链协议。
# 公告来自与更新包同一批第三方镜像站，内容不应被当作可信输入：
# 只放行 http/https，可以挡掉 file://、UNC(\\host\share)、
# 以及 explorer.exe / calc.exe 之类的本地可执行协议。
ALLOWED_LINK_SCHEMES: tuple = ("http", "https")


def is_safe_link(url: QUrl) -> bool:
    """判断链接是否可以交给系统打开"""
    if not url.isValid():
        return False
    return url.scheme().lower() in ALLOWED_LINK_SCHEMES


def open_safe_link(url: QUrl) -> None:
    """安全地打开外部链接：非 http/https 一律拒绝"""
    if not is_safe_link(url):
        from ..utils.log import logger

        logger.warning(f"已阻止非 http/https 链接: {url.toString()[:120]}")
        return
    QDesktopServices.openUrl(url)


def open_log_folder():
    """打开日志文件所在文件夹并选中当前日志文件（Windows 资源管理器）"""
    log_file = LOG_DIR_PATH / f"{APP_NAME}.log"
    if log_file.is_file():
        # 必须用列表形式：字符串形式会经过 cmd.exe 解析，
        # 路径里出现 " & ^ % 等字符时引号配对会被破坏。
        # APP_PATH 来自 Path().cwd()，路径内容不由程序固定。
        subprocess.Popen(["explorer.exe", f"/select,{log_file}"])
    else:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(LOG_DIR_PATH)))
