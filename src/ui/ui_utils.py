import subprocess

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from ..utils.application import LOG_DIR_PATH
from ..utils.log import today_log_file


def open_log_folder():
    """打开日志文件夹并选中当前日志文件（Windows 资源管理器）"""
    log_file = today_log_file()
    if log_file.is_file():
        # 打开文件夹并高亮选中当前使用的日志文件
        subprocess.Popen(f'explorer.exe /select,"{log_file}"')
    else:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(LOG_DIR_PATH)))
