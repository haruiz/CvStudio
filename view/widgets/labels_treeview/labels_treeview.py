from PyQt5 import QtCore
from PyQt5.QtCore import QObject,QSize,pyqtSignal,QModelIndex
from PyQt5.QtGui import QStandardItemModel,QContextMenuEvent,QIcon,QStandardItem
from PyQt5.QtWidgets import QTreeView,QLabel,QAction,QMenu

from util import GUIUtilities
from vo import LabelVo


class LabelsTreeView(QTreeView, QObject):
    action_click=pyqtSignal(QAction)
    CTX_MENU_ADD_LABEL="Add Label"
    CTX_MENU_DELETE_LABEL="Delete Label"
    def __init__(self, parent=None):
        super(LabelsTreeView, self).__init__(parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._model=QStandardItemModel(0,2)
        self._model.setHeaderData(0,QtCore.Qt.Horizontal,"Name")
        self._model.setHeaderData(1,QtCore.Qt.Horizontal,"Color")
        self.setModel(self._model)

    def add_node(self, vo: LabelVo):
        self._model.insertRow(0)
        self._model.setData(self._model.index(0,0),vo.name)
        color_label=QLabel()
        color_label.setProperty("tag", vo)
        color_label.setFixedSize(QSize(20,20))
        color_label.setStyleSheet("QLabel { background-color : %s; } " % vo.color)
        self.setIndexWidget(self._model.index(0,1),color_label)


    def contextMenuEvent(self, evt: QContextMenuEvent) -> None:
        menu=QMenu()
        menu.triggered.connect(self.context_menu_actions_handler)
        index: QModelIndex = self.indexAt(evt.pos())
        if index.isValid():
            icon: QIcon=GUIUtilities.get_icon('delete_label.png')
            action=menu.addAction(icon,self.CTX_MENU_DELETE_LABEL)
            action.setData(index)
        else:
            icon: QIcon=GUIUtilities.get_icon('new_label.png')
            menu.addAction(icon,self.CTX_MENU_ADD_LABEL)
        menu.exec_(self.mapToGlobal(evt.pos()))

    def context_menu_actions_handler(self, action: QAction):
        self.action_click.emit(action)



