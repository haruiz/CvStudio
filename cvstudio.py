import os
import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication

from dao.models import create_tables
from util import GUIUtilities
from view.windows import MainWindow


def dark_theme(app: QApplication):
    app.setStyle('Fusion')
    style = os.path.abspath("assets/styles/dark/style.css")
    with open(style, "r") as f:
        app.setStyleSheet(f.read())
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QPalette.Base, QColor(15, 15, 15))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QPalette.Text, QtCore.Qt.white)
    palette.setColor(QPalette.Button, QColor(20, 20, 20))
    palette.setColor(QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QPalette.Highlight, QColor(239, 74, 40).lighter())
    palette.setColor(QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)

def cvstudio_theme(app: QApplication):
    app.setStyle('Fusion')
    app.setStyle('Fusion')
    style=os.path.abspath("assets/styles/cvstudio/style.css")
    with open(style,"r") as f:
        app.setStyleSheet(f.read())
    palette=QPalette()
    palette.setColor(QPalette.Window,QColor(0,0,0))
    palette.setColor(QPalette.WindowText,QtCore.Qt.white)
    palette.setColor(QPalette.Base,QColor(15,15,15))
    palette.setColor(QPalette.AlternateBase,QColor(53,53,53))
    palette.setColor(QPalette.ToolTipBase,QtCore.Qt.white)
    palette.setColor(QPalette.ToolTipText,QtCore.Qt.white)
    palette.setColor(QPalette.Text,QtCore.Qt.white)
    palette.setColor(QPalette.Button,QColor(20,20,20))
    palette.setColor(QPalette.ButtonText,QtCore.Qt.white)
    palette.setColor(QPalette.BrightText,QtCore.Qt.red)
    palette.setColor(QPalette.Highlight,QColor(169, 3, 252).lighter())
    palette.setColor(QPalette.HighlightedText,QtCore.Qt.black)
    app.setPalette(palette)

def light_theme(app: QApplication):
    app.setStyle("Fusion")
    style = os.path.abspath("assets/styles/light/style.css")
    with open(style, "r") as f:
        app.setStyleSheet(f.read())

def gray_theme(app: QApplication):
    # **** => copy this code ****
    app.setStyle("Fusion")
    style=os.path.abspath("assets/styles/gray/style.css")
    with open(style,"r") as f:
        app.setStyleSheet(f.read())
    dark_palette=QPalette()
    dark_palette.setColor(QPalette.Window,QColor(46,47,48))
    dark_palette.setColor(QPalette.WindowText,QColor(208,208,208))
    dark_palette.setColor(QPalette.Light,QColor(255,255,255))
    dark_palette.setColor(QPalette.Midlight,QColor(227,227,227))
    dark_palette.setColor(QPalette.Dark,QColor(64,66,68))
    dark_palette.setColor(QPalette.Mid,QColor(160,160,160))
    dark_palette.setColor(QPalette.Text,QColor(208,208,208))
    dark_palette.setColor(QPalette.BrightText,QColor(255,51,51))
    dark_palette.setColor(QPalette.Button,QColor(64,66,68))
    dark_palette.setColor(QPalette.ButtonText,QColor(208,208,208))
    dark_palette.setColor(QPalette.Base,QColor(46,47,48))
    dark_palette.setColor(QPalette.Shadow,QColor(105,105,105))
    dark_palette.setColor(QPalette.Highlight,QColor(0,0,0,102))
    dark_palette.setColor(QPalette.HighlightedText,QColor(255,255,255))
    dark_palette.setColor(QPalette.Link,QColor(0,122,244))
    dark_palette.setColor(QPalette.LinkVisited,QColor(165,122,255))
    dark_palette.setColor(QPalette.AlternateBase,QColor(53,54,55))
    dark_palette.setColor(QPalette.NoRole,QColor(0,0,0))
    dark_palette.setColor(QPalette.ToolTipBase,QColor(0,0,0,102))
    dark_palette.setColor(QPalette.ToolTipText,QColor(208,208,208))
    dark_palette.setColor(QPalette.Disabled,QPalette.Window,QColor(68,68,68,255))
    dark_palette.setColor(QPalette.Disabled,QPalette.WindowText,QColor(164,166,168,96))
    dark_palette.setColor(QPalette.Disabled,QPalette.Text,QColor(164,166,168,96))
    dark_palette.setColor(QPalette.Disabled,QPalette.ButtonText,QColor(164,166,168,96))
    dark_palette.setColor(QPalette.Disabled,QPalette.Base,QColor(68,68,68,255))
    dark_palette.setColor(QPalette.Disabled,QPalette.Shadow,QColor(0,0,0,255))
    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")


if __name__ == "__main__":
    try:
        create_tables()
        app = QApplication(sys.argv)
        app_theme = "cvstudio"
        app.setProperty("theme", app_theme)
        if app_theme == "light":
            light_theme(app)
        elif app_theme == "dark":
            dark_theme(app)
        elif app_theme == "gray":
            gray_theme(app)
        elif app_theme == "cvstudio":
            cvstudio_theme(app)
        mainWindow = MainWindow()
        mainWindow.setWindowIcon(GUIUtilities.get_icon("polygon.png"))
        mainWindow.show()
        sys.exit(app.exec_())
    except Exception as ex:
        print(ex)
