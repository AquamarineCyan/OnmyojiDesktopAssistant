from subprocess import Popen

from .application import APP_EXE_NAME, APP_PATH
from .log import logger
from .signals import signal_manager

_WAIT_MAX_TRIES = 60
"""等待旧进程退出的最大轮数（每轮约 1 秒），避免脚本无限自旋"""

_WAIT_PING_TARGET = "127.0.0.1"
"""等待用的 ping 目标。

原先写的是公网 IP `123.45.67.89`：出网受限的环境下 ping 不通，
等待轮次会被拉长；而本机回环地址在任何环境下都立即应答，
「靠 ping 产生 1 秒延时」的目的照样达成，还不会向外发包。
"""


class Restart:
    """重启"""

    def __init__(self) -> None:
        self.app_exe_name = APP_EXE_NAME
        # 必须用绝对路径：`restart.bat` 若按 CWD 解析，从不同目录启动时
        # 会命中同名的其它文件（.bat 劫持），而它是在提权进程中执行的
        self.bat_path: str = str(APP_PATH / "restart.bat")

    def save(self, bat_text) -> None:
        # 脚本模板只含 ASCII，改用固定编码而不是 ANSI(系统 locale)，
        # 否则西文 Windows 上写这个文件会直接 UnicodeEncodeError
        with open(self.bat_path, "w", encoding="ascii", errors="replace") as f:
            f.write(bat_text)

    def app_restart(self, is_update: bool = False) -> None:
        """程序重启

        参数:
            is_update (bool): 是否更新重启，默认否
        """
        logger.info("restarting...")
        # 更新重启有独立的脚本
        if not is_update:
            self.write_restart_bat()
        # 启动.bat文件
        Popen([self.bat_path])
        # 关闭当前exe程序
        logger.info("App Exiting...")
        signal_manager.main.sys_exit.emit()

    def write_restart_bat(self) -> None:
        """编写通用重启脚本"""
        # 注意 start 的语法：第一个带引号的参数会被 cmd 当成窗口标题，
        # 所以标题要显式给空串，路径本身也必须加引号，否则含空格时行为未定义
        bat_text = f"""@echo off
@echo Waiting for the app to exit, this window will close automatically
setlocal EnableDelayedExpansion
set "program_name={self.app_exe_name}"
set /a _tries=0

:a
tasklist /FI "IMAGENAME eq %program_name%" | findstr /I /C:"%program_name%" > nul
if not errorlevel 1 (
    set /a _tries+=1
    if !_tries! gtr {_WAIT_MAX_TRIES} (
        echo Giving up waiting after {_WAIT_MAX_TRIES} seconds, starting anyway
        goto :b
    )
    echo %program_name% is still running, waiting...
    ping -n 2 {_WAIT_PING_TARGET} > nul
    goto :a
)

:b
echo Continue restart...
timeout /T 3 /NOBREAK > nul
start "" "%program_name%"
del "%~f0"
"""
        self.save(bat_text)

    def write_update_restart_bat(self, unzip_path: str = "zip_files") -> None:
        """编写更新重启脚本

        参数:
            unzip_path (str): 解压文件路径
        """
        # xcopy 的 errorlevel 必须检查：原脚本无条件 rd 删除解压产物、
        # 无条件 start，导致「覆盖失败却报重启成功」，更新被永久丢失
        bat_text = f"""@echo off
@echo Waiting for the app to exit, this window will close automatically
setlocal EnableDelayedExpansion
set "program_name={self.app_exe_name}"
set "unzip_path={unzip_path}"
set /a _tries=0

:a
tasklist /FI "IMAGENAME eq %program_name%" | findstr /I /C:"%program_name%" > nul
if not errorlevel 1 (
    set /a _tries+=1
    if !_tries! gtr {_WAIT_MAX_TRIES} (
        echo Giving up waiting after {_WAIT_MAX_TRIES} seconds
        goto :fail
    )
    echo %program_name% is still running, waiting...
    ping -n 2 {_WAIT_PING_TARGET} > nul
    goto :a
)

:b
if not exist "%unzip_path%\\%program_name%" goto :fail
timeout /T 3 /NOBREAK > nul

echo Copy new version...
xcopy ".\\%unzip_path%\\*" . /s /e /y /v > nul
if errorlevel 1 goto :fail

rd /s /q "%unzip_path%"

echo Start exe...
timeout /T 3 /NOBREAK > nul
start "" "%program_name%"
del "%~f0"
exit /b 0

:fail
echo Update failed, please update manually.
pause
exit /b 1
"""
        self.save(bat_text)
