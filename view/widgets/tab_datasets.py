import json
import os
import itertools
from hurry.filesize import size, alternative

from PyQt5 import QtCore
from PyQt5.QtCore import QThreadPool, QSize, QObject, pyqtSignal
from PyQt5.QtWidgets import QScrollArea,QWidget,QMessageBox,QDialog,QTabWidget,QFileDialog
from marshmallow import pprint

from dao import AnnotaDao
from dao.dataset_dao import DatasetDao
from decor import gui_exception, work_exception
from util import GUIUtilities, Worker, FileUtilities
from view.forms import DatasetForm
from .tab_media import MediaTabWidget
from vo import DatasetVO
from .response_grid import GridCard
from .loading_dialog import QLoadingDialog
from .response_grid import ResponseGridLayout
from .image_button import ImageButton
from schemas import ImageSchemeVO,AnnotSchemeVO,AnnotSchema,ImageScheme


class DatasetGridWidget(QWidget, QObject):
    new_dataset_action_signal = pyqtSignal()
    open_dataset_action_signal = pyqtSignal(DatasetVO)
    delete_dataset_action_signal = pyqtSignal(DatasetVO)
    refresh_dataset_action_signal = pyqtSignal(DatasetVO)
    edit_dataset_action_signal = pyqtSignal(DatasetVO)
    download_anno_action_signal = pyqtSignal(DatasetVO)

    def __init__(self, parent=None):
        super(DatasetGridWidget, self).__init__(parent)
        self.grid_layout = ResponseGridLayout()
        self.grid_layout.cols = 8
        self.setLayout(self.grid_layout)
        self._entries = None
        self.layout().setAlignment(QtCore.Qt.AlignTop)

    @property
    def data_source(self):
        return self._entries

    @data_source.setter
    def data_source(self, value):
        self._entries = value

    def create_ds_card(self, ds: DatasetVO):
        card_widget: GridCard = GridCard(debug=False)
        card_widget.label = "{} \n {}".format(ds.name, size(ds.size, system=alternative) if ds.size else "0 MB")
        btn_delete = ImageButton(GUIUtilities.get_icon("delete.png"), size=QSize(15, 15))
        btn_delete.setToolTip("Delete dataset")
        btn_edit = ImageButton(GUIUtilities.get_icon("edit.png"), size=QSize(15, 15))
        btn_edit.setToolTip("Edit dataset")
        btn_refresh = ImageButton(GUIUtilities.get_icon("refresh.png"), size=QSize(15, 15))
        btn_refresh.setToolTip("Refresh dataset")
        btn_download_annotations = ImageButton(GUIUtilities.get_icon("download.png"), size=QSize(15, 15))
        btn_download_annotations.setToolTip("Download annotations")

        card_widget.add_buttons([btn_delete, btn_edit, btn_refresh, btn_download_annotations])
        icon_file = "folder_empty.png"
        icon = GUIUtilities.get_icon(icon_file)
        # events
        btn_delete.clicked.connect(lambda: self.delete_dataset_action_signal.emit(ds))
        btn_edit.clicked.connect(lambda: self.edit_dataset_action_signal.emit(ds))
        btn_download_annotations.clicked.connect(lambda: self.download_anno_action_signal.emit(ds))
        card_widget.body = ImageButton(icon)
        btn_refresh.clicked.connect(lambda: self.refresh_dataset_action_signal.emit(ds))
        card_widget.body.doubleClicked.connect(lambda evt: self.open_dataset_action_signal.emit(ds))

        return card_widget

    def create_new_ds_button(self):
        new_dataset_widget: GridCard = GridCard(with_actions=False, with_title=False)
        btn_new_dataset = ImageButton(GUIUtilities.get_icon("new_folder.png"))
        new_dataset_widget.body = btn_new_dataset
        btn_new_dataset.clicked.connect(lambda: self.new_dataset_action_signal.emit())

        return new_dataset_widget

    def bind(self) -> None:
        cards_list = []
        new_dataset_button = self.create_new_ds_button()
        cards_list.append(new_dataset_button)
        for ds in self.data_source:
            card_widget = self.create_ds_card(ds)
            cards_list.append(card_widget)
        self.grid_layout.widgets = cards_list
        super(DatasetGridWidget, self).update()


class DatasetTabWidget(QScrollArea):
    def __init__(self, parent=None):
        super(DatasetTabWidget, self).__init__(parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.datasets_grid = DatasetGridWidget()
        self.datasets_grid.new_dataset_action_signal.connect(self.btn_new_dataset_on_slot)
        self.datasets_grid.delete_dataset_action_signal.connect(self.btn_delete_dataset_on_slot)
        self.datasets_grid.refresh_dataset_action_signal.connect(self.refresh_dataset_action_slot)
        self.datasets_grid.edit_dataset_action_signal.connect(self.edit_dataset_action_slot)
        self.datasets_grid.open_dataset_action_signal.connect(self.open_dataset_action_slot)
        self.datasets_grid.download_anno_action_signal.connect(self.download_annot_action_slot)
        self.setWidget(self.datasets_grid)
        self.setWidgetResizable(True)
        self.thread_pool = QThreadPool()
        self.loading_dialog = QLoadingDialog()
        self.ds_dao = DatasetDao()
        self.annot_dao = AnnotaDao()
        self.load()

    @gui_exception
    def load(self):
        @work_exception
        def do_work():
            results = self.ds_dao.fetch_all_with_size()
            return results, None

        @gui_exception
        def done_work(result):
            data, error = result
            if error:
                raise error
            self.datasets_grid.data_source = data
            self.datasets_grid.bind()

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self.thread_pool.start(worker)

    def _close_tab(self, tab_class):
        tab_widget_manager: QTabWidget = self.window().tab_widget_manager
        for i in range(tab_widget_manager.count()):
            curr_tab_widget = tab_widget_manager.widget(i)
            if isinstance(curr_tab_widget, tab_class):
                tab_widget_manager.removeTab(i)

    @QtCore.pyqtSlot()
    @gui_exception
    def btn_new_dataset_on_slot(self):
        form = DatasetForm()
        if form.exec_() == QDialog.Accepted:
            vo: DatasetVO = form.value
            self.ds_dao.save(vo)
            self.load()

    @QtCore.pyqtSlot(DatasetVO)
    @gui_exception
    def btn_delete_dataset_on_slot(self, vo: DatasetVO):
        reply = QMessageBox.question(self, 'Confirmation', "Are you sure?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.ds_dao.delete(vo.id)
            usr_folder = FileUtilities.get_usr_folder()
            ds_folder = os.path.join(usr_folder, vo.folder)
            FileUtilities.delete_folder(ds_folder)
            self.load()

    @QtCore.pyqtSlot(DatasetVO)
    @gui_exception
    def edit_dataset_action_slot(self, vo: DatasetVO):
        form = DatasetForm(vo)
        if form.exec_() == QDialog.Accepted:
            vo: DatasetVO = form.value
            self.ds_dao.save(vo)
            self.load()

    @QtCore.pyqtSlot(DatasetVO)
    def refresh_dataset_action_slot(self, vo: DatasetVO):
        self.load()

    @QtCore.pyqtSlot(DatasetVO)
    def open_dataset_action_slot(self, vo: DatasetVO):
        tab_widget_manager: QTabWidget = self.window().tab_widget_manager
        tab_widget = MediaTabWidget(vo)
        self._close_tab(MediaTabWidget)
        index = tab_widget_manager.addTab(tab_widget, vo.name)
        tab_widget_manager.setCurrentIndex(index)

    @gui_exception
    def download_annot_action_slot(self, vo: DatasetVO):
        @work_exception
        def do_work():
            results = self.annot_dao.fetch_all_by_dataset(vo.id)
            return results, None

        @gui_exception
        def done_work(result):
            data, error = result
            if error:
                raise error
            groups = itertools.groupby(data, lambda x: x["image"])
            annot_list = []
            for key, annotations in groups:
                image = ImageSchemeVO()
                image.path = key
                for annot_dict in list(annotations):
                    annot =AnnotSchemeVO()
                    annot.kind = annot_dict["annot_kind"]
                    annot.points=annot_dict["annot_points"]
                    annot.label_name=annot_dict["label_name"]
                    annot.label_color=annot_dict["label_color"]
                    image.regions.append(annot)
                annot_list.append(image)
            scheme = ImageScheme(many=True)
            options=QFileDialog.Options()
            options|=QFileDialog.DontUseNativeDialog
            default_file = os.path.join(os.path.expanduser('~'), "annotations.json")
            fileName,_=QFileDialog.getSaveFileName(self,"Export annotations",default_file,"Json Files (*.json)",options=options)
            if fileName:
                with open(fileName,'w') as f:
                    json.dump(scheme.dump(annot_list),f, indent=3)
        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self.thread_pool.start(worker)
