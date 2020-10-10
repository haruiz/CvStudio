import math

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent


class ImagePixmapSignals(QObject):
    hoverMoveEventSgn = pyqtSignal(QGraphicsSceneHoverEvent, int, int)
    hoverLeaveEventSgn = pyqtSignal()
    hoverEnterEventSgn = pyqtSignal()
    mouseClicked = pyqtSignal(QGraphicsSceneMouseEvent)


class ImagePixmap(QGraphicsPixmapItem):

    def __init__(self, parent=None):
        super(ImagePixmap, self).__init__(parent)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setAcceptHoverEvents(True)
        self.signals = ImagePixmapSignals()
        self.setAcceptTouchEvents(True)

    def hoverLeaveEvent(self, event):
        self.signals.hoverLeaveEventSgn.emit()
        super(ImagePixmap, self).hoverLeaveEvent(event)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.signals.hoverEnterEventSgn.emit()
        super(ImagePixmap, self).hoverEnterEvent(event)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        pt = event.pos()
        x = math.floor(pt.x())
        y = math.floor(pt.y())
        self.signals.hoverMoveEventSgn.emit(event, x, y)
        super(ImagePixmap, self).hoverMoveEvent(event)
