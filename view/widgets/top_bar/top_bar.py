from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QFrame,QVBoxLayout,QHBoxLayout,QPushButton
from pyface.qt import QtGui

from util import GUIUtilities


class TopBar(QFrame):
    def __init__(self, parent=None):
        super(TopBar, self).__init__(parent)
        self.setLayout(QHBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignRight)
        self.layout().setContentsMargins(0,0,0,0)
        self.setFrameStyle(QFrame.Box)
        self.setObjectName("top_bar")
        self.setFixedHeight(40)
        #self.setCursor(QtCore.Qt.SizeAllCursor)
        preferred_size=QSize(30,30)
        self.btn_minimize = QPushButton(icon=GUIUtilities.get_icon("minimize.png"))
        self.btn_maximize=QPushButton(icon=GUIUtilities.get_icon("maximize.png"))
        self.btn_close=QPushButton(icon=GUIUtilities.get_icon("close.png"))
        self.btn_minimize.clicked.connect(lambda evt: self.window().showMinimized())
        self.btn_maximize.clicked.connect(self.btn_maximize_click)
        self.btn_close.clicked.connect(lambda evt: self.window().close())
        self.layout().addWidget(self.btn_minimize)
        self.layout().addWidget(self.btn_maximize)
        self.layout().addWidget(self.btn_close)
        self.dragPos = None
        for i in reversed(range(self.layout().count())):
            widget=self.layout().itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setFixedSize(preferred_size)
                widget.setCursor(QtCore.Qt.PointingHandCursor)

    def mousePressEvent(self, evt: QtGui.QMouseEvent) -> None:
        if evt.buttons() == QtCore.Qt.LeftButton:
            self.dragPos=evt.globalPos()
            evt.accept()

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.window().windowState() == QtCore.Qt.WindowMaximized:
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def btn_maximize_click(self):
        if self.window().windowState() == QtCore.Qt.WindowMaximized:
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def mouseMoveEvent(self, evt: QtGui.QMouseEvent) -> None:
        if evt.buttons() == QtCore.Qt.LeftButton:
            self.window().move(self.window().pos() + evt.globalPos()-self.dragPos)
            self.dragPos=evt.globalPos()


