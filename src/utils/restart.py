from .application import APP_EXE_NAME, APP_PATH
from .log import logger
from .mysignal import global_ms as ms


class Restart:
    """重启"""

    def __init__(self) -> None:
        self.app_exe_name = APP_EXE_NAME
        self.bat_path: str = "restart.bat"  # 重启脚本路径

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
        from subprocess import Popen
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

    def write_upgrage_restart_bat(self, zip_path: str = None, reserve_resource: bool = False) -> None:
        """编写更新重启脚本

        参数:
            zip_path (str): 更新包路径
            reserve_resource (bool): 是否保留个人资源，默认否
        """
        if reserve_resource:
            need_backup = 1
        else:
            need_backup = 0

        bat_text = f"""@echo off
@echo 当前为更新程序，等待自动完成
set program_name={self.app_exe_name}
set need_backup={need_backup}

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

if not exist zip_files\\{self.app_exe_name} exit
timeout /T 3 /NOBREAK

if %need_backup%==1 (
echo backup resource...
md backup\\resource
xcopy .\\resource .\\backup\\resource /s /e /y
)

echo copy new version...
xcopy .\\zip_files . /d /s /e /y
rd /s /q zip_files
del {zip_path}

if %need_backup%==1 (
echo recover resource...
xcopy .\\backup\\resource .\\resource /s /e /y
if exist backup (
rd /s /q backup
)
)

echo start exe...
start {self.app_exe_name}
del %0
"""
        self.save(bat_text)

    def move_screenshot(self):
        bat_text = f"""@echo off
@echo 当前为迁移脚本，等待自动完成
xcopy /e /y /i "screenshot" "data\\screenshot"
rmdir /s /q "screenshot"
@echo 用户数据迁移完成
pause
del %0
"""
        if not (APP_PATH / "screenshot").exists():
            return
        _remove_bat_path = "remove.bat"
        with open(_remove_bat_path, "w", encoding="ANSI") as f:
            f.write(bat_text)
        from subprocess import Popen
        Popen([_remove_bat_path])
        logger.info("迁移截图文件夹完成")
