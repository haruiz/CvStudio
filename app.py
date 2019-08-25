import os
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QFile,QTextStream
from PyQt5.QtGui import QFont,QPalette,QColor
from PyQt5.QtWidgets import QApplication
from dao.models import create_tables
from util import GUIUtilities
from view.windows import MainWindow,MainWindowContainer


def fusion_theme(app: QApplication):

    app.setStyle('Fusion')
    style=os.path.abspath("assets/styles/dark/style.css")
    with open(style,"r") as f:
        app.setStyleSheet(f.read())
    # app.setStyleSheet("font: 50pt")  # for mac
    palette=QPalette()
    palette.setColor(QPalette.Window,QColor(43,33,34))
    #palette.setColor(QPalette.Window,QColor(53,53,53))
    palette.setColor(QPalette.WindowText,QtCore.Qt.white)
    palette.setColor(QPalette.Base,QColor(15,15,15))
    palette.setColor(QPalette.AlternateBase,QColor(53,53,53))
    palette.setColor(QPalette.ToolTipBase,QtCore.Qt.white)
    palette.setColor(QPalette.ToolTipText,QtCore.Qt.white)
    palette.setColor(QPalette.Text,QtCore.Qt.white)
    #palette.setColor(QPalette.Button,QColor(0,0,0))
    palette.setColor(QPalette.Button,QColor(53,53,53))
    palette.setColor(QPalette.ButtonText,QtCore.Qt.white)
    palette.setColor(QPalette.BrightText,QtCore.Qt.red)
    palette.setColor(QPalette.Highlight,QColor(239,74,40).lighter())
    palette.setColor(QPalette.HighlightedText,QtCore.Qt.black)
    app.setPalette(palette)


if __name__ == "__main__":
    try:
        create_tables()
        app=QApplication(sys.argv)
        fusion_theme(app)
        mainWindow=MainWindow()
        mainWindow.setWindowIcon(GUIUtilities.get_icon("python.png"))
        #mainWindow.showMaximized()
        #main_container = MainWindowContainer(mainWindow)
        mainWindow.show()
        #mainWindow.showMaximized()
        #mainWindow.setFont(QFont("arial",8,QFont.Light))
        sys.exit(app.exec_())
    except Exception as ex:
        print(ex)


