import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget


class TitleTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("陰陽師Onmyoji")
        self.setGeometry(300, 300, 400, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TitleTestWindow()
    window.show()
    sys.exit(app.exec())
