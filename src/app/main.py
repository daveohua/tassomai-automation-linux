import sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    from gui import Window

    app = QApplication(sys.argv)

    win = Window()
    win.show()

    sys.exit(app.exec())