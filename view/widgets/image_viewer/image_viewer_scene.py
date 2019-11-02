from PyQt5.QtCore import QObject,pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene,QGraphicsItem

from view.widgets.image_viewer.box_item import EditableBox
from view.widgets.image_viewer.polygon_item import EditablePolygon


class ImageViewerScene(QGraphicsScene, QObject):
    itemAdded = pyqtSignal(QGraphicsItem)
    itemDeleted=pyqtSignal(QGraphicsItem)

    def __init__(self, parent=None):
        super(ImageViewerScene, self).__init__(parent)

    def addItem(self, item: QGraphicsItem) -> None:
        super(ImageViewerScene, self).addItem(item)
        if isinstance(item, EditableBox) or isinstance(item, EditablePolygon):
            self.itemAdded.emit(item)

    def removeItem(self, item: QGraphicsItem) -> None:
        super(ImageViewerScene, self).removeItem(item)
        if isinstance(item,EditableBox) or isinstance(item,EditablePolygon):
            self.itemDeleted.emit(item)