from cvstudio.pyqt import (
    QtCore,
    QtGui,
    QSize,
    QObject,
    Signal,
    QIcon,
    QPushButton,
    QGraphicsDropShadowEffect,
)


class ImageButton(QPushButton, QObject):
    doubleClicked = Signal(QtGui.QMouseEvent)

    def __init__(
        self,
        icon: QIcon = QIcon(),
        size: QSize = QSize(64, 64),
        tag=None,
        tooltip=None,
        parent=None,
    ):
        super(ImageButton, self).__init__(parent)
        self.setIcon(icon)
        self.setContentsMargins(10, 10, 10, 20)
        #self.setCursor(QtCore.Qt.PointingHandCursor)
        self._size = size
        self._effect = self.graphicsEffect()
        self.setIconSize(self._size)
        self.setObjectName("image_button")
        self._tag = tag
        self.setStyleSheet("QPushButton{border: 0px solid;}")
        self.setToolTip(tooltip)

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    def enterEvent(self, evt: QtCore.QEvent) -> None:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setColor(QtGui.QColor(76, 35, 45).lighter())
        shadow.setOffset(4)
        self.setGraphicsEffect(shadow)
        super(ImageButton, self).enterEvent(evt)

    def leaveEvent(self, evt: QtCore.QEvent) -> None:
        self.setGraphicsEffect(self._effect)
        self.setIconSize(self._size)
        super(ImageButton, self).leaveEvent(evt)

    def mouseDoubleClickEvent(self, evt: QtGui.QMouseEvent) -> None:
        self.doubleClicked.emit(evt)
