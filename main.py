import sys
from ctypes import windll

from PySide6.QtWidgets import QApplication

from src.utils.config import config
from src.utils.gui import MainWindow

if __name__ == "__main__":
    # Is Admin
    if windll.shell32.IsUserAnAdmin():
        app = QApplication([])
        if config.user.window_style == "Fusion":
            app.setStyle("Fusion")
        main_win_ui = MainWindow()
        main_win_ui.show()
        app.exec()
    else:
        # Run Admin by UAC
        windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(0)
