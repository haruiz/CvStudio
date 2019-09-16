from PyQt5 import QtGui,QtWidgets,QtCore
from PyQt5.QtCore import QObject,pyqtSignal
from PyQt5.QtWidgets import QGraphicsRectItem,QMenu,QGraphicsSceneContextMenuEvent,QAction,QGraphicsItem


class EditableBoxSignals(QObject):
    deleted = pyqtSignal(QGraphicsItem)

class EditableBox(QGraphicsRectItem):
    def __init__(self,*args, **kwargs):
        super(EditableBox,self).__init__(*args,*kwargs)
        self.setZValue(10)
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable,True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setOpacity(0.5)
        self.signals = EditableBoxSignals()
        self._pen_color = QtGui.QColor(235,72,40)
        self._brush_color = QtGui.QColor(255, 0, 0, 100)
        self.setPen(QtGui.QPen(self._pen_color,2))

    @property
    def pen_color(self):
        return self._pen_color

    @pen_color.setter
    def pen_color(self, value):
        self._pen_color = value
        self.setPen(QtGui.QPen(self._pen_color,2))


    @property
    def brush_color(self):
        return self._brush_color

    @brush_color.setter
    def brush_color(self, value):
        self._brush_color = value

    def contextMenuEvent(self,evt: QGraphicsSceneContextMenuEvent) -> None:
        menu=QMenu()
        action: QAction=menu.addAction("Delete")
        delete_point=menu.exec_(evt.screenPos())
        if action == delete_point:
            self.scene().removeItem(self)
            self.signals.deleted.emit(self)
            
    def hoverEnterEvent(self, event):
        self.setBrush(self._brush_color)
        super(EditableBox,self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        super(EditableBox,self).hoverLeaveEvent(event)


