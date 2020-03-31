import abc
import math

from PyQt5 import QtGui,QtWidgets,QtCore
from PyQt5.QtCore import QObject,pyqtSignal,QPointF,QRectF
from PyQt5.QtGui import QColor,QPalette
from PyQt5.QtWidgets import QGraphicsRectItem,QMenu,QGraphicsSceneContextMenuEvent,QAction,QGraphicsItem, \
    QGraphicsEllipseItem,QAbstractGraphicsShapeItem,QGraphicsSceneMouseEvent,QApplication
from dao import LabelDao
from vo import LabelVO
import numpy as np

class EditableItemSignals(QObject):
    deleted=pyqtSignal(QGraphicsItem)
    moved=pyqtSignal(QGraphicsItem,QPointF)
    doubleClicked=pyqtSignal(QGraphicsItem)
    clicked = pyqtSignal(QGraphicsItem)




class EditableItem(QAbstractGraphicsShapeItem):
    def __init__(self, *args, **kwargs):
        super(EditableItem, self).__init__(*args, **kwargs)
        self.setZValue(10)
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable,True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges,True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setOpacity(0.5)
        self.signals=EditableItemSignals()
        self._labels_dao = LabelDao()
        self._label = LabelVO()
        self._tag=None
        self._shape_type = None

        app=QApplication.instance()
        color=app.palette().color(QPalette.Highlight)
        self._pen_color = color
        self._pen_width = 2
        self._brush_color = color

        self.setPen(QtGui.QPen(self._pen_color,self._pen_width))


    @property
    def pen_color(self):
        return self._pen_color

    @pen_color.setter
    def pen_color(self, value):
        self._pen_color = value
        self.setPen(QtGui.QPen(self._pen_color,self._pen_width))

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
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self,value: LabelVO):
        self._label=value
        if self._label:
            self._pen_color=QColor(self._label.color)
            self.setPen(QtGui.QPen(self._pen_color,1))
            self._brush_color=QColor(self._label.color)
            self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))

    def hoverEnterEvent(self, event):
        self.setBrush(self._brush_color)
        self.setPen(QtGui.QPen(self._pen_color,self._pen_width))
        super(EditableItem, self).hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        self.setPen(QtGui.QPen(self._pen_color,self._pen_width))
        super(EditableItem, self).hoverLeaveEvent(event)

    def contextMenuEvent(self, evt: QGraphicsSceneContextMenuEvent) -> None:
        menu=QMenu()
        action_delete: QAction=menu.addAction("Delete")
        if self.tag:
            dataset = self.tag
            result = self._labels_dao\
                 .fetch_all(dataset)
            if result:
                labels_menu=menu.addMenu("labels")
                for vo in result:
                    action=labels_menu.addAction(vo.name)
                    action.setData(vo)
        action=menu.exec_(evt.screenPos())
        if action == action_delete:
            self.delete_item()
            self.signals.deleted.emit(self)
        elif action and isinstance(action.data(),LabelVO):
            self.label = action.data()

    def delete_item(self):
        self.scene().removeItem(self)

    @abc.abstractmethod
    def coordinates(self,offset=QPointF(0,0)):
        raise NotImplementedError


class EditableBox(QGraphicsRectItem, EditableItem):
    def __init__(self, parent=None):
        super(EditableBox, self).__init__(parent)
        self.shape_type = "box"

    def coordinates(self,offset=QPointF(0,0)):
        item_box: QRectF = self.sceneBoundingRect()
        x1=math.floor(item_box.topLeft().x()+offset.x())
        y1=math.floor(item_box.topRight().y()+offset.y())
        x2=math.floor(item_box.bottomRight().x()+offset.x())
        y2=math.floor(item_box.bottomRight().y()+offset.y())
        return ",".join(map(str,[x1,y1,x2,y2]))


class EditableEllipse(QGraphicsEllipseItem, EditableItem):
    def __init__(self, parent=None):
        super(EditableEllipse, self).__init__(parent)
        self.shape_type = "ellipse"

    def coordinates(self,offset=QPointF(0,0)):
        item_box: QRectF=self.sceneBoundingRect()
        x1=math.floor(item_box.topLeft().x()+offset.x())
        y1=math.floor(item_box.topRight().y()+offset.y())
        x2=math.floor(item_box.bottomRight().x()+offset.x())
        y2=math.floor(item_box.bottomRight().y()+offset.y())
        return ",".join(map(str,[x1,y1,x2,y2]))


class EditablePolygonPointSignals(QObject):
    deleted=pyqtSignal(int)
    moved=pyqtSignal(QGraphicsItem,QPointF)
    doubleClicked=pyqtSignal(QGraphicsItem)

class EditablePolygonPoint(QtWidgets.QGraphicsPathItem):
    circle=QtGui.QPainterPath()
    circle.addRect(QtCore.QRectF(-1,-1,2,2))
    square=QtGui.QPainterPath()
    square.addRect(QtCore.QRectF(-3,-3,6,6))

    def __init__(self,index=None):
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

        app=QApplication.instance()
        color=app.palette().color(QPalette.Highlight)
        self._pen_color=color
        self._pen_width=2
        self._brush_color=color

        self.setPen(QtGui.QPen(self._pen_color,self._pen_width))
        self.setBrush(self._brush_color)

    @property
    def pen_color(self):
        return self._pen_color

    @pen_color.setter
    def pen_color(self,value):
        self._pen_color=value
        self.setPen(QtGui.QPen(self._pen_color,self._pen_width))

    @property
    def brush_color(self):
        return self._brush_color

    @brush_color.setter
    def brush_color(self,value):
        self._brush_color=value
        self.setBrush(self._brush_color)

    @property
    def pen_width(self):
        return self._pen_width

    @pen_width.setter
    def pen_width(self,value):
        self._pen_width=value
        self.pen().setWidth(self._pen_width)


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



class EditablePolygon(QtWidgets.QGraphicsPolygonItem, EditableItem):
    def __init__(self, parent=None):
        super(EditablePolygon, self).__init__(parent)
        self.shape_type = "polygon"
        self._points=[]
        self._controls=[]

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        self._points = value

    @property
    def controls(self):
        return self._controls

    @controls.setter
    def controls(self, value):
        self._controls = value

    @property
    def last_point(self):
        return self._points[-1]

    @property
    def count(self):
        return len(self._points)

    @EditableItem.label.setter
    def label(self,value: LabelVO):
        super(EditablePolygon, EditablePolygon).label.__set__(self, value)
        if len(self._controls) > 0:
            for point_control in self._controls:
                point_control.brush_color=self._brush_color
                point_control.pen_color=self._pen_color

    def delete_polygon(self):
        while self.points:
            self.points.pop()
            it=self.controls.pop()
            self.scene().removeItem(it)
            del it
        self.scene().removeItem(self)

    def addPoint(self,p):
        self._points.append(p)
        item=EditablePolygonPoint(len(self._points)-1)
        item.brush_color=self._brush_color
        item.pen_color=self._pen_color
        item.pen_width = self._pen_width
        item.signals.moved.connect(self.point_moved_slot)
        item.signals.deleted.connect(self.point_deleted_slot)
        item.signals.doubleClicked.connect(self.point_double_clicked)
        self.scene().addItem(item)
        item.setPos(p)
        self._controls.append(item)
        self.setPolygon(QtGui.QPolygonF(self.points))

    def insertPoint(self,index,p):
        self.points.insert(index,p)
        item=EditablePolygonPoint(index)
        item.brush_color=self._brush_color
        item.pen_color=self._pen_color
        item.signals.moved.connect(self.point_moved_slot)
        item.signals.deleted.connect(self.point_deleted_slot)
        item.signals.doubleClicked.connect(self.point_double_clicked)
        self.scene().addItem(item)
        item.setPos(p)
        self.controls.insert(index,item)
        self.setPolygon(QtGui.QPolygonF(self.points))

    def update_indexes(self):
        for idx in range(len(self.points)):
            self.controls[idx].index=idx

    def point_moved_slot(self,item: EditablePolygonPoint,pos: QPointF):
        self.points[item.index]=self.mapFromScene(pos)
        self.setPolygon(QtGui.QPolygonF(self.points))

    def point_deleted_slot(self,index: int):
        del self.points[index]
        del self.controls[index]
        self.setPolygon(QtGui.QPolygonF(self.points))
        self.update_indexes()

    def point_double_clicked(self,item: EditablePolygonPoint):
        pos=self.points[item.index]
        self.insertPoint(item.index+1,pos)
        self.update_indexes()

    def move_item(self,index,pos):
        if 0 <= index < len(self.controls):
            item=self.controls[index]
            item.setEnabled(False)
            item.setPos(pos)
            item.setEnabled(True)

    def itemChange(self,change,value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            for i,point in enumerate(self.points):
                self.move_item(i,self.mapToScene(point))
        return super(EditablePolygon,self).itemChange(change,value)

    def delete_item(self):
        self.delete_polygon()

    def coordinates(self,offset=QPointF(0,0)):
        points=[[math.floor(pt.x()+offset.x()),math.floor(pt.y()+offset.y())] for pt in self.points]
        points=np.asarray(points).flatten().tolist()
        return ",".join(map(str,points))


