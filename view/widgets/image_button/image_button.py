from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import QSize,QObject,pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton,QGraphicsDropShadowEffect


class ImageButton(QPushButton, QObject):
    doubleClicked = pyqtSignal(QtGui.QMouseEvent)
    def __init__(self,icon: QIcon = QIcon(), size: QSize=QSize(64,64),  parent=None, with_shadow= False):
        super(ImageButton, self).__init__(parent=parent, icon=icon)
        self.setContentsMargins(10,10,10,20)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setIconSize(size)
        self.setObjectName("image_button")
        shadow=QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QtGui.QColor(76,35,45).lighter())
        self.setStyleSheet('QPushButton{border: 0px solid;}')
        # shadow.setColor(QtGui.QColor(99, 255, 255))
        shadow.setOffset(2)
        if with_shadow:
            self.setGraphicsEffect(shadow)

    def mouseDoubleClickEvent(self, evt: QtGui.QMouseEvent) -> None:
        self.doubleClicked.emit(evt)





