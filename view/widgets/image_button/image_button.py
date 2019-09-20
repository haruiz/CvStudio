import math

from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import QSize,QObject,pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton,QGraphicsDropShadowEffect


class ImageButton(QPushButton, QObject):
    doubleClicked = pyqtSignal(QtGui.QMouseEvent)
    def __init__(self,icon: QIcon = QIcon(), size: QSize=QSize(64,64),  parent=None):
        super(ImageButton, self).__init__(parent=parent, icon=icon)
        self.setContentsMargins(10,10,10,20)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._size = size
        self._effect = self.graphicsEffect()
        self.setIconSize(self._size)
        self.setObjectName("image_button")
        self._tag = None
        self.setStyleSheet('QPushButton{border: 0px solid;}')
        # shadow.setColor(QtGui.QColor(99, 255, 255))

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    def enterEvent(self, evt: QtCore.QEvent) -> None:
        #self.setIconSize(QSize(math.floor(self._size.width() * 1.2),math.floor(self._size.height() * 1.2)))
        shadow=QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        #shadow.setColor(QtGui.QColor(76,35,45).lighter())
        shadow.setColor(QtGui.QColor(76,35,45).lighter())
        shadow.setOffset(4)
        self.setGraphicsEffect(shadow)
        super(ImageButton, self).enterEvent(evt)

    def leaveEvent(self, evt: QtCore.QEvent) -> None:
        self.setGraphicsEffect(self._effect)
        self.setIconSize(self._size)
        super(ImageButton, self).leaveEvent(evt)

    def mouseDoubleClickEvent(self, evt: QtGui.QMouseEvent) -> None:
        self.doubleClicked.emit(evt)





