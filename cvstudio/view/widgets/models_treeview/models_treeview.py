from PyQt5 import QtCore
from PyQt5.QtCore import QSize, QModelIndex, QThreadPool, QObject, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QTreeView, QAbstractItemView, QMenu, QAction

from cvstudio.util import GUIUtilities as gui
from cvstudio.view.widgets.loading_dialog import QLoadingDialog
from cvstudio.vo import HubVO
from ..common import CustomModel, CustomNode


class ModelsTreeview(QTreeView, QObject):
    action_click = pyqtSignal(QAction)
    CTX_MENU_ADD_REPOSITORY_ACTION = "Add new repository"
    CTX_MENU_DELETE_REPO_ACTION = "Delete repository"
    CTX_MENU_UPDATE_REPO_ACTION = "Update repository"
    CTX_MENU_AUTO_LABEL_ACTION = "Auto-Label"

    def __init__(self, parent=None):
        super(ModelsTreeview, self).__init__(parent)
        self.setIconSize(QSize(18, 18))
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setDropIndicatorShown(True)
        self._thread_pool = QThreadPool()
        self._loading_dialog = QLoadingDialog()
        model: CustomModel = CustomModel(["Name", "Uri"])
        self._root_node = CustomNode(["Models", ""], level=1, status=1, success_icon=gui.get_icon("database.png"))
        model.addChild(self._root_node)
        self.setModel(model)
        # self.selectionModel().selectionChanged.connect(self.selectionChangedSlot)

    def contextMenuEvent(self, evt: QContextMenuEvent) -> None:
        index: QModelIndex = self.indexAt(evt.pos())
        actions = []
        if index.isValid():
            node: CustomNode = index.internalPointer()
            index: QModelIndex = self.indexAt(evt.pos())
            menu = QMenu()
            menu.triggered.connect(self.context_menu_actions_handler)
            if node.level == 1:
                actions = [
                    QAction(gui.get_icon('new_folder.png'), self.CTX_MENU_ADD_REPOSITORY_ACTION)
                ]
            elif node.level == 2:
                actions = [
                    QAction(gui.get_icon('delete.png'), self.CTX_MENU_DELETE_REPO_ACTION),
                    QAction(gui.get_icon('refresh.png'), self.CTX_MENU_UPDATE_REPO_ACTION)
                ]
            elif node.level == 3:
                actions = [
                    QAction(gui.get_icon('robotic-hand.png'), self.CTX_MENU_AUTO_LABEL_ACTION)
                ]
            if actions:
                for act in actions:
                    act.setData(index)
                    menu.addAction(act)
            menu.exec_(self.mapToGlobal(evt.pos()))

    def _update_model(self):
        self.model().layoutChanged.emit()

    def add_node(self, vo: HubVO):

        parent_node = CustomNode(
            [vo.path, ""],
            level=2,
            tag=vo,
            status=1,
            success_icon=gui.get_icon("github.png")
        )
        self._root_node.addChild(parent_node)
        for m in vo.models:
            child_node = CustomNode(
                [m.name, ""],
                level=3,
                tooltip=m.description,
                tag=m,
                status=1,
                success_icon=gui.get_icon("cube.png")
            )
            parent_node.addChild(child_node)
        self._update_model()

    def context_menu_actions_handler(self, action: QAction):
        self.action_click.emit(action)
