from cvstudio.pyqt import (
    QGraphicsScene,
    QApplication,
    QColor,
    QPixmap,
    QPainter,
    QBrush,
    Signal,
    QGraphicsItem,
    QObject,
)
from .image_graphicsview_items import EditableItem


class ImageViewerScene(QGraphicsScene, QObject):
    itemAdded = Signal(QGraphicsItem)
    itemDeleted = Signal(QGraphicsItem)

    def __init__(self, *args, **kwargs):
        super(ImageViewerScene, self).__init__(*args, **kwargs)

    def addItem(self, item: QGraphicsItem) -> None:
        super(ImageViewerScene, self).addItem(item)
        if isinstance(item, EditableItem):
            self.itemAdded.emit(item)

    def removeItem(self, item: QGraphicsItem) -> None:
        super(ImageViewerScene, self).removeItem(item)
        if isinstance(item, EditableItem):
            self.itemDeleted.emit(item)
