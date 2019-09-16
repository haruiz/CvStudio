from PyQt5 import QtCore
from PyQt5.QtCore import QSize,QModelIndex,QItemSelection,QThreadPool,QObject,pyqtSignal
from PyQt5.QtGui import QContextMenuEvent,QIcon
from PyQt5.QtWidgets import QTreeView,QAbstractItemView,QMenu,QAction,QDialog,QTabWidget,QWidget

from core import HubFactory,HubProvider
from dao.hub_dao import HubDao
from util import GUIUtilities,Worker
from view.forms import NewRepoForm
from view.widgets.loading_dialog import QLoadingDialog
from vo import DatasetVO,HubVO
from ..common import CustomModel, CustomNode

class ModelsTreeview(QTreeView, QObject):
    action_click = pyqtSignal(QAction)
    CTX_MENU_NEW_DATASET_ACTION = "Add new repository"
    CTX_MENU_AUTO_LABEL_ACTION= "Auto-label"

    def __init__(self, parent=None):
        super(ModelsTreeview, self).__init__(parent)
        self.setIconSize(QSize(18,18))
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setDropIndicatorShown(True)
        self._thread_pool = QThreadPool()
        self._loading_dialog = QLoadingDialog()
        model: CustomModel=CustomModel(["Name","Uri"])
        self._root_node = CustomNode(["Models",""],level=1,status=1,success_icon=GUIUtilities.get_icon("database.png"))
        model.addChild(self._root_node)
        self.hub_dao = HubDao()
        self.setModel(model)

        #self.selectionModel().selectionChanged.connect(self.selectionChangedSlot)

    def contextMenuEvent(self, evt: QContextMenuEvent) -> None:
        index: QModelIndex=self.indexAt(evt.pos())
        if index.isValid():
            node: CustomNode=index.internalPointer()
            menu=QMenu()
            menu.triggered.connect(self.context_menu_actions_handler)
            if node.level == 1:
                icon: QIcon = GUIUtilities.get_icon('delete-dataset.png')
                action: QAction=menu.addAction(icon, self.CTX_MENU_NEW_DATASET_ACTION)
                action.setData(node)
            elif node.level == 3:
                icon: QIcon=GUIUtilities.get_icon('delete-dataset.png')
                action: QAction=menu.addAction(icon,self.CTX_MENU_AUTO_LABEL_ACTION)
                action.setData(node)
            menu.exec_(self.mapToGlobal(evt.pos()))

    def _update_model(self):
        self.model().layoutChanged.emit()

    def add_node(self, vo: HubVO):

        parent_node=CustomNode(
            [vo.path,""],
            level=2,
            status=1,
            success_icon=GUIUtilities.get_icon("github.png")
        )
        self._root_node.addChild(parent_node)
        for m in vo.models:
            child_node=CustomNode(
                [m.name,""],
                level=3,
                tooltip=m.description,
                status=1,
                success_icon=GUIUtilities.get_icon("cube.png")
            )
            parent_node.addChild(child_node)
        self._update_model()

    def context_menu_actions_handler(self,action: QAction):
        self.action_click.emit(action)








