import math

from cvstudio.pyqt import (
    QtCore,
    Signal,
    QObject,
    QGraphicsPixmapItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
)


class ImagePixmapSignals(QObject):
    hoverMoveEventSgn = Signal(QGraphicsSceneHoverEvent, int, int)
    hoverLeaveEventSgn = Signal()
    hoverEnterEventSgn = Signal()
    mouseClicked = Signal(QGraphicsSceneMouseEvent)


class ImagePixmap(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super(ImagePixmap, self).__init__(parent)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setAcceptHoverEvents(True)
        self.signals = ImagePixmapSignals()
        self.setAcceptTouchEvents(True)

    def hoverLeaveEvent(self, event):
        super(ImagePixmap, self).hoverLeaveEvent(event)
        self.signals.hoverLeaveEventSgn.emit()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        super(ImagePixmap, self).hoverEnterEvent(event)
        self.signals.hoverEnterEventSgn.emit()

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        super(ImagePixmap, self).hoverMoveEvent(event)
        pt = event.pos()
        x = math.floor(pt.x())
        y = math.floor(pt.y())
        self.signals.hoverMoveEventSgn.emit(event, x, y)
