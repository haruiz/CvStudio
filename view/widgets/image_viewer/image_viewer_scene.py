from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem

from view.widgets.image_viewer.items import EditableItem


class ImageViewerScene(QGraphicsScene, QObject):
    itemAdded = pyqtSignal(QGraphicsItem)
    itemDeleted = pyqtSignal(QGraphicsItem)

    def __init__(self, parent=None):
        super(ImageViewerScene, self).__init__(parent)

    def addItem(self, item: QGraphicsItem) -> None:
        super(ImageViewerScene, self).addItem(item)
        if isinstance(item, EditableItem):
            self.itemAdded.emit(item)

    def removeItem(self, item: QGraphicsItem) -> None:
        super(ImageViewerScene, self).removeItem(item)
        if isinstance(item, EditableItem):
            self.itemDeleted.emit(item)
