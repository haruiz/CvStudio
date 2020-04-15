from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QThreadPool, pyqtSignal
from PyQt5.QtWidgets import QWidget, QScrollArea

from util import GUIUtilities
from view.widgets import ImageButton
from view.widgets.loading_dialog import QLoadingDialog
from view.widgets.response_grid import ResponseGridLayout, GridCard
from view.wizard import ModelWizard


class ModelsGridWidget(QWidget, QObject):
    new_item_action = pyqtSignal()

    def __init__(self, parent=None):
        super(ModelsGridWidget, self).__init__(parent)
        self.grid_layout = ResponseGridLayout()
        self.grid_layout.setAlignment(QtCore.Qt.AlignTop)
        self.grid_layout.cols = 8
        self.setLayout(self.grid_layout)
        self._entries = None

    def build_new_button(self):
        new_item_widget: GridCard = GridCard(with_actions=False, with_title=False)
        btn_new_item = ImageButton(GUIUtilities.get_icon("new_folder.png"))
        btn_new_item.clicked.connect(lambda: self.new_item_action.emit())
        new_item_widget.body = btn_new_item
        return new_item_widget

    def bind(self):
        cards_list = []
        new_item_button = self.build_new_button()
        cards_list.append(new_item_button)
        self.grid_layout.widgets = cards_list
        super(ModelsGridWidget, self).update()


class ModelsTabWidget(QScrollArea):
    def __init__(self, parent=None):
        super(ModelsTabWidget, self).__init__(parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_grid = ModelsGridWidget()
        self.data_grid.new_item_action.connect(self.data_grid_new_item_action_slot)
        self.setWidget(self.data_grid)
        self.setWidgetResizable(True)
        self._thread_pool = QThreadPool()
        self._loading_dialog = QLoadingDialog()
        self.load()

    def data_grid_new_item_action_slot(self):
        new_model_wizard = ModelWizard()
        new_model_wizard.exec_()

    def load(self):
        self.data_grid.bind()
