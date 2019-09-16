import itertools
from typing import List,Any

import typing
from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex,pyqtSignal,QObject
from PyQt5.QtGui import QColor


class CustomNode(object):
    def __init__(self,data=None,success_icon = None, hover_icon = None, error_icon = None, level = -1, tag=None, status=1, tooltip=None):
        self._data=data
        if isinstance(data, tuple):
            self._data=list(data)
        if isinstance(data, str):
            self._data=[data]
        self._tag=tag
        self._enable = False
        self._success_icon = success_icon
        self._error_icon = error_icon if error_icon else  success_icon
        self._hover_icon = hover_icon if hover_icon else  success_icon
        self._children=[]
        self._parent=None
        self._level = level
        self._row=0
        self._status = status
        self._tooltip_content=tooltip

    def get_data(self,column):
        if 0 <= column < len(self._data):
            return self._data[column]

    def set_data(self, column, value):
        self._data[column] = value

    def columnCount(self):
        return len(self._data) if self._data else 0

    @property
    def tooltip_content(self):
        return self._tooltip_content

    @tooltip_content.setter
    def tooltip_content(self, value):
        self._tooltip_content = value

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self,val):
        self._tag=val

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def success_icon(self):
        return self._success_icon

    @success_icon.setter
    def success_icon(self, value):
        self._success_icon = value

    @property
    def error_icon(self):
        return self._error_icon

    @error_icon.setter
    def error_icon(self, value):
        self._error_icon = value

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, value):
        self._children = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = value

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, value):
        self._row = value

    def child(self,index):
        if 0 <= index < len(self.children):
            return self.children[index]

    def addChild(self,child):
        child._parent=self
        child._row=len(self.children)  # get the last index
        self.children.append(child)

    def removeChild(self,position):
        if position < 0 or position > len(self._children):
            return False
        child=self._children.pop(position)
        child._parent=None
        return True


class CustomModelSignals(QObject):
    data_changed = pyqtSignal(CustomNode, int, str, str)

class CustomModel(QtCore.QAbstractItemModel):
    def __init__(self,columns):
        QtCore.QAbstractItemModel.__init__(self)
        self._root=CustomNode(list(itertools.repeat("",len(columns))))
        self.signals = CustomModelSignals()
        self._columns = columns

    @property
    def root(self):
        return self._root


    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        if role == QtCore.Qt.DisplayRole:
            return self._columns[section]

        return super(CustomModel, self).headerData(section, orientation, role)

    def addChild(self,node,parent=None):
        if not parent or not parent.isValid():
            parent = self._root
        else:
            parent = parent.internalPointer()
        parent.addChild(node)

    def setData(self, index: QModelIndex, value: Any, role=None):
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                node : CustomNode=index.internalPointer()
                if value:
                    old_val = node.get_data(0)
                    node.set_data(0, value)
                    self.signals.data_changed.emit(node, role, old_val, value)
                    return True
                else:
                    return False
        return False


    def removeChild(self, index: QModelIndex):
        self.beginRemoveRows(index.parent(),index.row(),index.row())
        success=self.removeRow(index.row(),parent=index.parent())
        self.endRemoveRows()
        return success

    def removeRow(self,row,parent):
        #if not parent
        if not parent.isValid():
            parentNode=self._root
        else:
            parentNode=parent.internalPointer()  # the node
        parentNode.removeChild(row)
        return True


    def data(self, index: QModelIndex, role=None):
        if not index.isValid():
            return None
        node : CustomNode=index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.get_data(index.column())
        elif role== QtCore.Qt.DecorationRole and index.column() == 0:
            if node.status == 1:
                return  node.success_icon
            else:
                return node.error_icon
        elif role == QtCore.Qt.TextColorRole:
            if node.level == 2 and node.status == -1:
                return  QColor(255, 0, 0)
        elif role == QtCore.Qt.ToolTipRole:
            return node.tooltip_content
        return None


    def flags(self, index: QModelIndex):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        flags=super(CustomModel, self).flags(index)
        node : CustomNode = index.internalPointer()
        # if node.level == 1:
        #     return (flags | QtCore.Qt.ItemIsEditable   )
        # else:
        #     return (flags | QtCore.Qt.ItemIsSelectable)
        return (flags | QtCore.Qt.ItemIsEditable)


    def rowCount(self, parent:QModelIndex=None, *args, **kwargs):
            if parent.isValid():  # internal nodes
                child: CustomNode=parent.internalPointer()
                return len(child.children)
            return len(self._root.children)  # first level nodes

    def columnCount(self,parent: QModelIndex=None, *args, **kwargs):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        return self._root.columnCount()

    def parent(self, in_index: QModelIndex=None):
        if in_index.isValid():
            parent=in_index.internalPointer().parent
            if parent:
                return QtCore.QAbstractItemModel.createIndex(self,parent.row,0,parent)
        return QtCore.QModelIndex()

    def index(self,  row: int, column: int, parent=None, *args, **kwargs):
        if not parent or not parent.isValid():
            parent_node=self._root
        else:
            parent_node=parent.internalPointer()

        if not QtCore.QAbstractItemModel.hasIndex(self,row,column,parent):
            return QtCore.QModelIndex()
        child=parent_node.child(row)
        if child:
            return QtCore.QAbstractItemModel.createIndex(self,row,column,child)
        else:
            return QtCore.QModelIndex()






