from subprocess import Popen

from .application import APP_EXE_NAME
from .log import logger
from .mysignal import global_ms as ms


class Restart:
    """重启"""

    def __init__(self) -> None:
        self.app_exe_name = APP_EXE_NAME
        self.bat_path: str = "restart.bat"

    def save(self, bat_text) -> None:
        with open(self.bat_path, "w", encoding="ANSI") as f:
            f.write(bat_text)

    def app_restart(self, is_upgrade: bool = False) -> None:
        """程序重启

        参数:
            is_upgrade (bool): 是否更新重启，默认否
        """
        logger.info("restarting...")
        # 更新重启有独立的脚本
        if not is_upgrade:
            self.write_restart_bat()
        # 启动.bat文件
        Popen([self.bat_path])
        # 关闭当前exe程序
        logger.info("App Exiting...")
        ms.main.sys_exit.emit()

    def write_restart_bat(self) -> None:
        """编写通用重启脚本"""
        bat_text = f"""@echo off
@echo 当前为重启程序，等待自动完成
set "program_name={self.app_exe_name}"

:a
tasklist | findstr /I /C:"%program_name%" > nul
if errorlevel 1 (
    echo %program_name% is closed.
    goto :b
) else (
    echo %program_name% is still running, waiting...
    ping 123.45.67.89 -n 1 -w 1000 > nul
    goto :a
)

:b
echo Continue restart...
timeout /T 3 /NOBREAK
start {self.app_exe_name}
del %0
"""
        self.save(bat_text)

    def write_upgrage_restart_bat(self, unzip_path: str = "zip_files") -> None:
        """编写更新重启脚本

        参数:
            unzip_path (str): 解压文件路径
        """

        bat_text = f"""@echo off
@echo 当前为更新程序，等待自动完成
set program_name={self.app_exe_name}

:a
tasklist | findstr /I /C:"%program_name%" > nul
if errorlevel 1 (
    echo %program_name% is closed.
    goto :b
) else (
    echo %program_name% is still running, waiting...
    ping 123.45.67.89 -n 1 -w 1000 > nul
    goto :a
)

:b
echo Continue upgrading...

if not exist {unzip_path}\\{self.app_exe_name} exit
timeout /T 3 /NOBREAK

echo copy new version...
xcopy .\\{unzip_path} . /s /e /y /v
rd /s /q {unzip_path}

echo start exe...
timeout /T 3 /NOBREAK
start {self.app_exe_name}
del %0
"""
        self.save(bat_text)
