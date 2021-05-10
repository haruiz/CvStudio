from cvstudio.pyqt import (
    QAbstractGraphicsShapeItem,
    QtWidgets,
    QtCore,
    QtGui,
    QObject,
    Signal,
    QGraphicsItem,
    QPointF,
    QPalette,
    QApplication,
    QColor,
    QPen,
    QMenu,
    QAction,
    QGraphicsSceneContextMenuEvent,
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QRectF,
    QGraphicsSceneMouseEvent,
)
import math
import abc
from cvstudio.dao import LabelDao
from cvstudio.vo import LabelVO


class EditableItemSignals(QObject):
    deleted = Signal(QGraphicsItem)
    moved = Signal(QGraphicsItem, QPointF)
    doubleClicked = Signal(QGraphicsItem)
    clicked = Signal(QGraphicsItem)


class EditableItem(QAbstractGraphicsShapeItem):
    def __init__(self, *args, **kwargs):
        super(EditableItem, self).__init__(*args, **kwargs)
        self.setZValue(10)
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setOpacity(0.5)
        self.signals = EditableItemSignals()
        self._labels_dao = LabelDao()
        self._label = LabelVO()
        self._data_item = None
        self._shape_type = None

        app = QApplication.instance()
        color = app.palette().color(QPalette.Highlight)
        self._pen_color = color
        self._pen_width = 2
        self._brush_color = color
        self.setPen(QtGui.QPen(self._pen_color, self._pen_width))

    @property
    def pen_color(self):
        return self._pen_color

    @pen_color.setter
    def pen_color(self, value):
        self._pen_color = value
        self.setPen(QtGui.QPen(self._pen_color, self._pen_width))

    @property
    def brush_color(self):
        return self._brush_color

    @brush_color.setter
    def brush_color(self, value):
        self._brush_color = value
        self.setBrush(self._brush_color)

    @property
    def pen_width(self):
        return self._pen_width

    @pen_width.setter
    def pen_width(self, value):
        self._pen_width = value
        self.pen().setWidth(self._pen_width)

    @property
    def shape_type(self):
        return self._shape_type

    @shape_type.setter
    def shape_type(self, value):
        self._shape_type = value

    @property
    def data_item(self):
        return self._data_item

    @data_item.setter
    def data_item(self, value):
        self._data_item = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value: LabelVO):
        self._label = value
        if self._label:
            self.pen_color = QColor(self._label.color)
            self.brush_color = QColor(self._label.color)

    def hoverEnterEvent(self, event):
        self.setBrush(self._brush_color)
        self.setPen(QtGui.QPen(self._pen_color, self._pen_width))
        super(EditableItem, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        self.setPen(QtGui.QPen(self._pen_color, self._pen_width))
        super(EditableItem, self).hoverLeaveEvent(event)

    def delete_item(self):
        self.scene().removeItem(self)

    @abc.abstractmethod
    def coordinates(self, offset=QPointF(0, 0)):
        raise NotImplementedError

    def contextMenuEvent(self, evt: QGraphicsSceneContextMenuEvent) -> None:
        pass


class EditableBox(QGraphicsRectItem, EditableItem):
    def __init__(self, *args, **kwargs):
        super(EditableBox, self).__init__(*args, **kwargs)
        self.shape_type = "box"

    def coordinates(self, offset=QPointF(0, 0)):
        item_box: QRectF = self.sceneBoundingRect()
        x1 = math.floor(item_box.topLeft().x() + offset.x())
        y1 = math.floor(item_box.topRight().y() + offset.y())
        x2 = math.floor(item_box.bottomRight().x() + offset.x())
        y2 = math.floor(item_box.bottomRight().y() + offset.y())
        return ",".join(map(str, [x1, y1, x2, y2]))


class EditableEllipse(QGraphicsEllipseItem, EditableItem):
    def __init__(self, *args, **kwargs):
        super(EditableEllipse, self).__init__(*args, **kwargs)
        self.shape_type = "ellipse"

    def coordinates(self, offset=QPointF(0, 0)):
        item_box: QRectF = self.sceneBoundingRect()
        x1 = math.floor(item_box.topLeft().x() + offset.x())
        y1 = math.floor(item_box.topRight().y() + offset.y())
        x2 = math.floor(item_box.bottomRight().x() + offset.x())
        y2 = math.floor(item_box.bottomRight().y() + offset.y())
        return ",".join(map(str, [x1, y1, x2, y2]))
