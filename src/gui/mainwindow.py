from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QFrame, QFormLayout, QWidget, QGridLayout, QCheckBox, QLabel, \
            QSpinBox, QHBoxLayout, QLineEdit, QMenuBar, QGroupBox, QTextEdit, QPushButton
from PyQt5.QtCore import QMetaObject, QRect, QThread, pyqtSlot
from PyQt5.QtGui import QPixmap, QFont, QIcon

import os, sys

from base.https.session import Session
from base.output import OutputSender
from app.cache import Database

class TassomaiUI(object):
    def __init__(self, main_window: QMainWindow):
        self.win = main_window
        self.path = __file__
        if not self.path.endswith(("gui\\mainwindow.py", "gui/mainwindow.py")): # this is when we're using the .exe version
            self.path = ""
        else:
            self.path = self.path.replace("gui\\mainwindow.py", "").replace("\\", "/")

    def setupUi(self):
        self.win.setWindowTitle("Tassomai Automation")
        self.win.setWindowIcon(QIcon(self.path + 'images/logo.png'))
        self.win.resize(665, 510)

        self.centralwidget = QWidget(self.win)

        self.formLayout = QFormLayout(self.centralwidget)
        self.formLayout.setContentsMargins(5, 0, 5, -1)

        self.topFrame = QFrame(self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.topFrame.sizePolicy().hasHeightForWidth())
        self.topFrame.setSizePolicy(sizePolicy)
        self.topFrame.setAutoFillBackground(True)
        self.topFrame.setFrameShape(QFrame.StyledPanel)
        self.topFrame.setFrameShadow(QFrame.Raised)

        self.gridLayout = QGridLayout(self.topFrame)

        self.tassomaiImage = QLabel(self.topFrame)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tassomaiImage.sizePolicy().hasHeightForWidth())
        self.tassomaiImage.setSizePolicy(sizePolicy)
        self.tassomaiImage.setPixmap(QPixmap(self.path + "images/banner.png"))
        self.gridLayout.addWidget(self.tassomaiImage, 0, 0, 1, 1)

        self.formLayout.setWidget(0, QFormLayout.SpanningRole, self.topFrame)

        self.frame = QFrame(self.centralwidget)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame)
        self.gridLayout_2.setContentsMargins(5, 2, 2, -1)
        self.gridLayout_2.setVerticalSpacing(10)

        self.dailyGoal = QCheckBox(self.frame)
        font = QFont()
        font.setPointSize(10)
        self.dailyGoal.setFont(font)
        self.dailyGoal.setChecked(True)
        self.gridLayout_2.addWidget(self.dailyGoal, 2, 0, 1, 1)

        self.bonusGoal = QCheckBox(self.frame)
        self.bonusGoal.setFont(font)
        self.gridLayout_2.addWidget(self.bonusGoal, 3, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()

        self.label1 = QLabel(self.frame)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label1.sizePolicy().hasHeightForWidth())
        self.label1.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(10)
        self.label1.setFont(font)
        self.horizontalLayout.addWidget(self.label1)

        self.maxQuizes = QSpinBox(self.frame)
        self.maxQuizes.setMinimum(1)
        self.maxQuizes.setMaximum(1000)
        self.maxQuizes.setProperty("value", 1000)
        self.horizontalLayout.addWidget(self.maxQuizes)

        self.label2 = QLabel(self.frame)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label2.sizePolicy().hasHeightForWidth())
        self.label2.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(10)
        self.label2.setFont(font)
        self.horizontalLayout.addWidget(self.label2)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.seleniumBox = QGroupBox(self.frame)
        font = QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.seleniumBox.setFont(font)
        self.gridLayout_3 = QGridLayout(self.seleniumBox)

        self.passwordTassomaiLabel = QLabel(self.seleniumBox)
        self.gridLayout_3.addWidget(self.passwordTassomaiLabel, 2, 0, 1, 1)

        self.emailTassomaiLabel = QLabel(self.seleniumBox)
        self.gridLayout_3.addWidget(self.emailTassomaiLabel, 1, 0, 1, 1)

        self.pathToGeckoLabel = QLabel(self.seleniumBox)
        self.gridLayout_3.addWidget(self.pathToGeckoLabel, 0, 0, 1, 1)

        self.emailTassomai = QLineEdit(self.seleniumBox)
        self.gridLayout_3.addWidget(self.emailTassomai, 1, 1, 1, 1)

        self.pathToGecko = QLineEdit(self.seleniumBox)
        self.gridLayout_3.addWidget(self.pathToGecko, 0, 1, 1, 1)

        self.passwordTassomai = QLineEdit(self.seleniumBox)
        self.passwordTassomai.setEchoMode(QLineEdit.Password)
        self.gridLayout_3.addWidget(self.passwordTassomai, 2, 1, 1, 1)

        self.framelessFirefox = QCheckBox(self.seleniumBox)
        font = QFont()
        font.setPointSize(9)
        self.framelessFirefox.setFont(font)
        self.framelessFirefox.setChecked(False)
        self.gridLayout_3.addWidget(self.framelessFirefox, 3, 0, 1, 1)

        self.gridLayout_2.addWidget(self.seleniumBox, 0, 0, 1, 1)

        self.formLayout.setWidget(3, QFormLayout.SpanningRole, self.frame)

        self.buttonsLayout = QHBoxLayout()

        self.startButton = QPushButton(self.centralwidget)
        self.startButton.setDefault(True)
        self.buttonsLayout.addWidget(self.startButton)

        self.stopButton = QPushButton(self.centralwidget)
        self.stopButton.setDefault(True)
        self.buttonsLayout.addWidget(self.stopButton)

        self.formLayout.setLayout(4, QFormLayout.SpanningRole, self.buttonsLayout)

        self.output = QTextEdit(self.centralwidget)
        self.output.setReadOnly(True)
        self.formLayout.setWidget(5, QFormLayout.SpanningRole, self.output)

        self.win.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(self.win)
        self.menubar.setGeometry(QRect(0, 0, 665, 21))
        self.win.setMenuBar(self.menubar)

        self.retranslateUi()
        QMetaObject.connectSlotsByName(self.win)

    def retranslateUi(self):
        self.dailyGoal.setText("Finish when daily goal complete")
        self.bonusGoal.setText("Finish when bonus goal complete")
        self.framelessFirefox.setText("Enable Frameless Window (runs in background)")
        self.label1.setText("Only do a maximum of ")
        self.label2.setText(" quiz(s)")
        self.seleniumBox.setTitle("Selenium Settings")
        self.passwordTassomaiLabel.setText("Password for Tassomai login")
        self.emailTassomaiLabel.setText("Email for Tassomai login")
        self.pathToGeckoLabel.setText("PATH to geckodriver.exe (Firefox WebDriver)")
        self.startButton.setText("Start Automation")
        self.stopButton.setText("Stop Automation")
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.output.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
        "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">-------------------------------------------</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600; text-decoration: underline; color:#14860a;\">All output will go here<br /></span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">-------------------------------------------</p>\n"
)

class Window(QMainWindow):
    def __init__(self, show_stats=True, close=False, parent=None):
        super().__init__(parent)
        self.showStats = show_stats
        self.shouldClose = close

        self.ui = TassomaiUI(self)
        self.ui.setupUi()

        self.outputSender = OutputSender(self.ui.output)

        self.database = Database(f'{os.environ["USERPROFILE"]}/AppData/Local/tassomai-automation/', 'answers.json')
        self.cache = Database(f'{os.environ["USERPROFILE"]}/AppData/Local/tassomai-automation/', 'info.json')

        self.ui.pathToGecko.setText(self.cache.get('path'))
        self.ui.emailTassomai.setText(self.cache.get('email'))
        self.ui.passwordTassomai.setText(self.cache.get('password'))

        self.createWorkers()

    def closeEvent(self, event):
        if self.session_thread.isRunning():
            self.session.running = False
            try:
                self.session_thread.terminate()
                self.session_thread.wait()
            except:
                pass

    def createWorkers(self):
        # Session
        self.session = Session(self)
        self.session_thread = QThread()
        self.session.moveToThread(self.session_thread)
        self.session_thread.start()

        self.session.logger.connect(self.updateLog)
        self.session.show.connect(self.show)
        self.session.close.connect(sys.exit)
        self.ui.startButton.clicked.connect(self.session.start)
        self.ui.stopButton.clicked.connect(self.terminate_session)

    @pyqtSlot(str, dict)
    def updateLog(self, text, kwargs):
        return self.outputSender.send_html(text, **kwargs)

    def terminate_session(self):
        self.session.logger.emit('TYPES=[(#c8001a, BOLD), Successfully terminated script.]', {'newlinesafter': 2})
        self.ui.startButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.session.running = False

        if not self.session.shownStats:
            if hasattr(self.session, 'tassomai'):
                self.session.show_stats()