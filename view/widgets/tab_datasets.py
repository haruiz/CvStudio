from PyQt5 import QtCore
from PyQt5.QtCore import QThreadPool,QSize,QObject,pyqtSignal
from PyQt5.QtWidgets import QScrollArea,QWidget,QFrame,QListWidget,QMessageBox,QDialog

from dao.dataset_dao import DatasetDao
from decor import gui_exception,work_exception
from util import GUIUtilities,Worker
from view.forms import DatasetForm
from vo import DatasetVO
from .response_grid_card import GridCard
from .loading_dialog import QLoadingDialog
from .response_grid import ResponseGridLayout
from .image_button import ImageButton


class DatasetGridWidget(QWidget,QObject):
    new_dataset_action_signal = pyqtSignal()
    delete_dataset_action_signal=pyqtSignal(DatasetVO)
    def __init__(self, parent=None):
        super(DatasetGridWidget, self).__init__(parent)
        self.grid_layout = ResponseGridLayout()
        self.setLayout(self.grid_layout)
        self._datasets = None
        self.layout().setAlignment(QtCore.Qt.AlignTop)

    @property
    def datasets(self):
        return self._datasets

    @datasets.setter
    def datasets(self, value):
        self._datasets = value
        self.update()

    def new_ds_card_factory(self,ds: DatasetVO):
        card_widget: GridCard=GridCard(debug=False)
        card_widget.label=ds.name.title()
        btn_delete=ImageButton(GUIUtilities.get_icon("delete.png"),size=QSize(15,15))
        btn_edit=ImageButton(GUIUtilities.get_icon("edit.png"),size=QSize(15,15))
        btn_view=ImageButton(GUIUtilities.get_icon("search.png"),size=QSize(15,15))
        btn_delete.clicked.connect(lambda evt: self.delete_dataset_on_click(ds))
        card_widget.add_buttons([btn_delete,btn_edit,btn_view])
        icon_file = "images_folder.png" if ds.data_type == "Images" else "videos_folder.png"
        icon = GUIUtilities.get_icon(icon_file)
        card_widget.body=ImageButton(icon)
        return card_widget

    def new_ds_button_factory(self):
        new_dataset_widget: GridCard=GridCard(with_actions=False,with_title=False)
        btn_new_dataset=ImageButton(GUIUtilities.get_icon("new_folder.png"))
        new_dataset_widget.body=btn_new_dataset
        btn_new_dataset.clicked.connect(self.btn_new_dataset_on_click)
        return new_dataset_widget

    def update(self) -> None:
        cards_list = []
        new_dataset_button = self.new_ds_button_factory()
        cards_list.append(new_dataset_button)
        for ds in self.datasets:
            card_widget = self.new_ds_card_factory(ds)
            cards_list.append(card_widget)
        self.grid_layout.widgets = cards_list
        super(DatasetGridWidget, self).update()

    def btn_new_dataset_on_click(self):
        self.new_dataset_action_signal.emit()

    def delete_dataset_on_click(self, vo: DatasetVO):
        self.delete_dataset_action_signal.emit(vo)



class DatasetTabWidget(QScrollArea):
    def __init__(self, parent=None):
        super(DatasetTabWidget,self).__init__(parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.central_widget=DatasetGridWidget()
        self.central_widget.new_dataset_action_signal.connect(self.btn_new_dataset_on_click)
        self.central_widget.delete_dataset_action_signal.connect(self.btn_delete_dataset_on_click)
        self.setWidget(self.central_widget)
        self.setWidgetResizable(True)
        self.thread_pool=QThreadPool()
        self.loading_dialog=QLoadingDialog()
        self.ds_dao = DatasetDao()
        self.load()

    # def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
    #     menu=QMenu(self)
    #     quitAction=menu.addAction("Quit")
    #     action=menu.exec_(self.mapToGlobal(event.pos()))
    #     if action == quitAction:
    #         self.close()

    @gui_exception
    def load(self):

        @work_exception
        def do_work():
            results = self.ds_dao.fetch_all()
            return results, None

        @gui_exception
        def done_work(result):
            data,error=result
            if error:
                raise error
            self.widget().datasets = data
        worker=Worker(do_work)
        worker.signals.result.connect(done_work)
        self.thread_pool.start(worker)

    @QtCore.pyqtSlot()
    @gui_exception
    def btn_new_dataset_on_click(self):
        form=DatasetForm()
        if form.exec_() == QDialog.Accepted:
            vo : DatasetVO = form.value
            self.ds_dao.save(vo)
            self.load()

    @QtCore.pyqtSlot(DatasetVO)
    @gui_exception
    def btn_delete_dataset_on_click(self, vo: DatasetVO):
        self.ds_dao.delete(vo.id)
        self.load()
    #
    # @QtCore.pyqtSlot(QObject)
    # def view_btn_card_action_slot(self,sender: DataSetTabWidgetCard):
    #     ds_id=sender.vo.id
    #     tab_widget = MediaTabWidget()
    #     tab_widget_manager: QTabWidget = self.window().tab_widget_manager
    #     for i in range(tab_widget_manager.count()):
    #         curr_tab_widget = tab_widget_manager.widget(i)
    #         if isinstance(curr_tab_widget, MediaTabWidget):
    #             tab_widget_manager.removeTab(i)
    #     tab_widget_manager.addTab(tab_widget,sender.vo.name)
    #     tab_widget_manager.setCurrentIndex(1)









