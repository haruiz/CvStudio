from PyQt5 import QtGui,QtCore,QtWidgets
from PyQt5.QtCore import QObject,pyqtSignal,QPointF,QThreadPool
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsSceneContextMenuEvent,QMenu,QAction,QGraphicsItem,QGraphicsSceneMouseEvent

from dao import LabelDao
from decor import gui_exception,work_exception
from util import Worker
from vo import LabelVO,DatasetEntryVO


class EditablePolygonPointSignals(QObject):
    deleted=pyqtSignal(int)
    moved=pyqtSignal(QGraphicsItem,QPointF)
    doubleClicked=pyqtSignal(QGraphicsItem)


class EditablePolygonPoint(QtWidgets.QGraphicsPathItem):
    circle=QtGui.QPainterPath()
    circle.addEllipse(QtCore.QRectF(-3,-3,5,5))
    square=QtGui.QPainterPath()
    square.addRect(QtCore.QRectF(-5,-5,10,10))

    def __init__(self,index):
        super(EditablePolygonPoint,self).__init__()
        self.setPath(EditablePolygonPoint.circle)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable,True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setAcceptHoverEvents(True)
        self.index=index
        self.setZValue(11)
        self.signals=EditablePolygonPointSignals()
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self._pen_color = QtGui.QColor(235,72,40)
        self._brush_color = QtGui.QColor(235,72,40)
        self.setPen(QtGui.QPen(self._pen_color,2))
        self.setBrush(self._brush_color)


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
        self.setBrush(self._brush_color)


    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.signals.doubleClicked.emit(self)

    def contextMenuEvent(self,evt: QGraphicsSceneContextMenuEvent) -> None:
        menu=QMenu()
        action: QAction=menu.addAction("Delete point")
        delete_point=menu.exec_(evt.screenPos())
        if action == delete_point:
            self.scene().removeItem(self)
            self.signals.deleted.emit(self.index)

    def hoverEnterEvent(self,event):
        self.setPath(EditablePolygonPoint.square)
        self.setBrush(QtGui.QColor("white"))
        #self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        super(EditablePolygonPoint,self).hoverEnterEvent(event)

    def hoverLeaveEvent(self,event):
        self.setPath(EditablePolygonPoint.circle)
        self.setBrush(self._brush_color)
        super(EditablePolygonPoint,self).hoverLeaveEvent(event)

    def mouseReleaseEvent(self,event):
        self.setSelected(False)
        super(EditablePolygonPoint,self).mouseReleaseEvent(event)

    def itemChange(self,change,value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange and self.isEnabled():
            self.signals.moved.emit(self,value)
        return super(EditablePolygonPoint,self).itemChange(change,value)

class EditablePolygonSignals(QObject):
    deleted=pyqtSignal(QGraphicsItem)

class EditablePolygon(QtWidgets.QGraphicsPolygonItem):
    def __init__(self,parent=None):
        super(EditablePolygon,self).__init__(parent)
        self.setZValue(10)
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.points=[]
        self.controls=[]
        self.setOpacity(0.5)
        self._labels_dao = LabelDao()
        self.signals = EditablePolygonSignals()
        self._pen_color=QtGui.QColor(235,72,40)
        self._brush_color=QtGui.QColor(255, 0, 0, 100)
        self.setPen(QtGui.QPen(self._pen_color,1))
        self._label = LabelVO()
        self._tag = None

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value
        if self._label:
            self._pen_color = QColor(self._label.color)
            self.setPen(QtGui.QPen(self._pen_color,1))
            self._brush_color = QColor(self._label.color)
            self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
            if len(self.controls) > 0:
                for point_control in self.controls:
                    point_control.brush_color=self._brush_color
                    point_control.pen_color=self._pen_color


    @property
    def tag(self)-> DatasetEntryVO:
        return self._tag

    @tag.setter
    def tag(self,value):
        self._tag = value

    @property
    def last_point(self):
        return self.points[-1]

    @property
    def count(self):
        return len(self.points)

    def addPoint(self,p):
        self.points.append(p)
        item=EditablePolygonPoint(len(self.points)-1)
        item.brush_color=self._brush_color
        item.pen_color=self._pen_color
        item.signals.moved.connect(self.point_moved_slot)
        item.signals.deleted.connect(self.point_deleted_slot)
        item.signals.doubleClicked.connect(self.point_double_clicked)
        self.scene().addItem(item)
        item.setPos(p)
        self.controls.append(item)
        self.setPolygon(QtGui.QPolygonF(self.points))

    def insertPoint(self,index,p):
        self.points.insert(index, p)
        item=EditablePolygonPoint(index)
        item.brush_color=self._brush_color
        item.pen_color=self._pen_color
        item.signals.moved.connect(self.point_moved_slot)
        item.signals.deleted.connect(self.point_deleted_slot)
        item.signals.doubleClicked.connect(self.point_double_clicked)
        self.scene().addItem(item)
        item.setPos(p)
        self.controls.insert(index, item)
        self.setPolygon(QtGui.QPolygonF(self.points))

    def delete_polygon(self):
        while self.points:
            self.points.pop()
            it=self.controls.pop()
            self.scene().removeItem(it)
            del it
        self.scene().removeItem(self)

    def contextMenuEvent(self,evt: QGraphicsSceneContextMenuEvent) -> None:

        menu = QMenu()
        delete_polygon_action = menu.addAction("Delete")
        if self.tag:
            result=self._labels_dao.fetch_all(self.tag.dataset)
            if len(result) > 0:
                labels_menu=menu.addMenu("labels")
                for vo in result:
                    action = labels_menu.addAction(vo.name)
                    action.setData(vo)

        action = menu.exec_(evt.screenPos())
        if action == delete_polygon_action:
            self.delete_polygon()
            self.signals.deleted.emit(self)
        elif action and  isinstance(action.data(),LabelVO):
            self.label = action.data()


    def point_moved_slot(self,item: EditablePolygonPoint,pos: QPointF):
        self.points[item.index]=self.mapFromScene(pos)
        self.setPolygon(QtGui.QPolygonF(self.points))

    def update_indexes(self):
        for idx in range(len(self.points)):
            self.controls[idx].index = idx

    def point_deleted_slot(self,index: int):
        del self.points[index]
        del self.controls[index]
        self.setPolygon(QtGui.QPolygonF(self.points))
        self.update_indexes()

    def point_double_clicked(self,item: EditablePolygonPoint):
        pos = self.points[item.index]
        self.insertPoint(item.index+1,pos)
        self.update_indexes()

    def hoverEnterEvent(self, event):
        self.setBrush(self._brush_color)
        super(EditablePolygon,self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        super(EditablePolygon,self).hoverLeaveEvent(event)

    def move_item(self, index, pos):
        if 0 <= index < len(self.controls):
            item = self.controls[index]
            item.setEnabled(False)
            item.setPos(pos)
            item.setEnabled(True)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            for i, point in enumerate(self.points):
                self.move_item(i, self.mapToScene(point))
        return super(EditablePolygon,self).itemChange(change,value)