from PyQt5 import QtCore
from PyQt5.QtCore import QObject,QSize,pyqtSignal,QModelIndex,QThreadPool
from PyQt5.QtGui import QStandardItemModel,QContextMenuEvent,QIcon,QStandardItem
from PyQt5.QtWidgets import QTreeView,QLabel,QAction,QMenu,QAbstractItemView

from util import GUIUtilities
from view.widgets.common import CustomModel,CustomNode
from view.widgets.loading_dialog import QLoadingDialog
from vo import LabelVo


class LabelsTreeView(QTreeView, QObject):
    action_click=pyqtSignal(QAction)
    CTX_MENU_ADD_LABEL="Add Label"
    CTX_MENU_DELETE_LABEL="Delete Label"
    def __init__(self, parent=None):
        super(LabelsTreeView, self).__init__(parent)
        self.setIconSize(QSize(18,18))
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setDropIndicatorShown(True)
        self._thread_pool=QThreadPool()
        self._loading_dialog=QLoadingDialog()
        model: CustomModel=CustomModel(["Name","Uri"])
        self._root_node=CustomNode(["Models",""],level=1,status=1,success_icon=GUIUtilities.get_icon("database.png"))
        model.addChild(self._root_node)
        self.setModel(model)

    def add_node(self, vo: LabelVo):
        pass


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



