from PyQt5 import QtGui,QtWidgets,QtCore
from PyQt5.QtCore import QObject,pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsRectItem,QMenu,QGraphicsSceneContextMenuEvent,QAction,QGraphicsItem

from dao import LabelDao
from vo import LabelVo,DatasetEntryVO


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
        self._pen_color = QColor(235,72,40)
        self.setPen(QtGui.QPen(self._pen_color,1))
        self._brush_color = QColor(255, 0, 0, 100)
        self._tag = None
        self._labels_dao = LabelDao()
        self._label=LabelVo()

    @property
    def tag(self)-> DatasetEntryVO:
        return self._tag

    @tag.setter
    def tag(self,value):
        self._tag = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self,value: LabelVo):
        self._label=value
        if self._label:
            self._pen_color=QColor(self._label.color)
            self.setPen(QtGui.QPen(self._pen_color,1))
            self._brush_color=QColor(self._label.color)
            self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))

    def contextMenuEvent(self,evt: QGraphicsSceneContextMenuEvent) -> None:
        menu=QMenu()
        action_delete: QAction=menu.addAction("Delete")
        if self.tag:
            result=self._labels_dao.fetch_all(self.tag.dataset)
            if len(result) > 0:
                labels_menu=menu.addMenu("labels")
                for vo in result:
                    action=labels_menu.addAction(vo.name)
                    action.setData(vo)
        action=menu.exec_(evt.screenPos())
        if action == action_delete:
            self.scene().removeItem(self)
            self.signals.deleted.emit(self)
        elif action and  isinstance(action.data(),LabelVo):
            self.label=action.data()

            
    def hoverEnterEvent(self, event):
        self.setBrush(self._brush_color)
        self.setPen(QtGui.QPen(self._pen_color,2))

        super(EditableBox,self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        self.setPen(QtGui.QPen(self._pen_color,2))

        super(EditableBox,self).hoverLeaveEvent(event)


