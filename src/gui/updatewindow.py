from PyQt5.QtCore import QMetaObject, QSize, Qt, QThread, pyqtSlot
from PyQt5.QtWidgets import QSizePolicy, QGridLayout, QLabel, \
    QDialog, QPushButton, QSpacerItem, QProgressBar, QVBoxLayout
from PyQt5.QtGui import QIcon

import ctypes
import sys
import os
from threading import Timer

from base.https.update import Updater
from base.common import is_admin
from app import path, is_executable

class DialogUI:
    def __init__(self, dialog: QDialog):
        self.dialog = dialog
        
    def setupUi(self):
        self.dialog.setFixedSize(409, 121)
        self.dialog.setWindowIcon(QIcon(path('images', 'logo.png')))

        self.verticalLayout = QVBoxLayout(self.dialog)

        self.gridLayout = QGridLayout()

        self.progress = QProgressBar(self.dialog)
        self.progress.setMaximumSize(QSize(16777215, 21))
        self.progress.setProperty("value", 0)
        self.progress.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.progress, 1, 0, 1, 1)
        self.status = QLabel(self.dialog)
        self.status.setMaximumSize(QSize(16777215, 14))

        self.gridLayout.addWidget(self.status, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.restart_button = QPushButton(self.dialog)
        self.restart_button.setEnabled(False)

        self.verticalLayout.addWidget(self.restart_button)

        self.retranslateUi()
        QMetaObject.connectSlotsByName(self.dialog)

    def retranslateUi(self):
        self.dialog.setWindowTitle("Tassomai Automation Updater")
        self.status.setText("Click BEGIN to start.")
        self.restart_button.setText("BEGIN")
        self.restart_button.setEnabled(True)

class UpdateDialog(QDialog):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.gui = main_window

        if is_executable:
            if not is_admin() and 'C:\\' in os.path.abspath(path("Tassomai Automation.exe")):
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, path(), None, 1)
                self.close()
                self.gui.close()
                return

        self.setModal(True)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.ui = DialogUI(self)
        self.ui.setupUi()

        self.createWorkers()

    def createWorkers(self):
        self.updater = Updater(self)
        self.updater_thread = QThread()
        self.updater.moveToThread(self.updater_thread)
        self.updater_thread.start()

        self.updater.progress.connect(self.setProgress)
        self.updater.status.connect(self.setStatus)
        self.updater.change.connect(self.changeConnect)
        self.ui.restart_button.clicked.connect(self.updater.begin)

    def restart(self):
        thread = Timer(0.5, lambda: os.startfile(path('bin', 'Updater.exe')))
        thread.start()
        self.close()
        self.gui.ui.win.close()

    @pyqtSlot(int)
    def setProgress(self, value):
        self.ui.progress.setValue(value)

    @pyqtSlot(str)
    def setStatus(self, status):
        self.ui.status.setText(status)

    def progressValue(self):
        return self.ui.progress.value()

    @pyqtSlot(object)
    def changeConnect(self, func):
        self.ui.restart_button.clicked.connect(func)