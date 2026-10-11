import ctypes
import sys
from ctypes import windll

from PySide6.QtWidgets import QApplication

from src.utils.application import APP_NAME
from src.utils.config import config  # noqa: F401
from src.utils.gui import MainWindow
from src.utils.log import redirect_third_party_output

# 重定向到日志并记录第三方输出
redirect_third_party_output()

if __name__ == "__main__":
    # 检查管理员权限
    if windll.shell32.IsUserAnAdmin():
        app = QApplication(sys.argv)
        main_win_widget = MainWindow()
        main_win_widget.show()
        app.exec()
    else:
        # 打包产物在 main.spec 中已声明 uac_admin=True，正常不会走到这里；
        # 这条分支服务的是「源码直接运行」场景（IDE 里双击 main.py）。
        # ShellExecuteW 返回值 > 32 才算拉起成功：用户点 UAC 的「否」时返回
        # SE_ERR_ACCESSDENIED(5)，原先无条件 exit(0) 会让程序凭空消失。
        # 打包产物 console=False，print 用户看不到，必须用 MessageBox。
        print("请以管理员身份运行程序")  # IDE模式下才会触发
        ret = windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 1)
        if ret <= 32:
            ctypes.windll.user32.MessageBoxW(
                None,
                "程序需要管理员权限才能运行。\n请右键选择「以管理员身份运行」。",
                APP_NAME,
                0x10,  # MB_ICONERROR
            )
        sys.exit(0)
