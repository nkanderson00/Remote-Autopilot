import sys
from PyQt6 import uic
from PyQt6.QtWidgets import *


class Dialog(QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi('servosettings.ui', self)
        self.setWindowTitle("Servo Settings")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dialog()
    window.show()
    sys.exit(app.exec())
