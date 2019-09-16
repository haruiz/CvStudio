import os
import time

from PyQt5 import QtCore
from PyQt5.QtCore import QThreadPool,pyqtSlot,QThread
from PyQt5.QtWidgets import QScrollArea,QTabWidget,QWidget,QVBoxLayout

import vo
from dao import DatasetDao
from decor import gui_exception
from util import Worker
from view.widgets.gallery.card import GalleryCard
from view.widgets.image_viewer import ImageViewer
from view.widgets.image_viewer.image_viewer import ImageViewerWidget
from vo import DatasetEntryVO
from .gallery import Gallery
from .loading_dialog import QLoadingDialog


class MediaTabWidget(QWidget):
    def __init__(self, ds_id , parent=None):
        super(MediaTabWidget, self).__init__(parent)
        self.media_grid = Gallery()
        self.media_grid.filesDropped.connect(self.gallery_files_dropped_slot)
        self.media_grid.doubleClicked.connect(self.gallery_card_double_click_slot)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().addWidget(self.media_grid)
        self._thread_pool=QThreadPool()
        self._loading_dialog = QLoadingDialog()
        self._ds_dao = DatasetDao()
        self._ds_id = ds_id
        self.load()

    def load(self):
        ds_id = self._ds_id

        def do_work():
            entries = self._ds_dao.fetch_entries(ds_id)
            entries = [vo.file_path for vo in entries]
            return entries

        def done_work(result):
            self.media_grid.items = result
            self.media_grid.bind()
            self.media_grid.tag = ds_id
            self._loading_dialog.close()

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)
        self._loading_dialog.exec_()

    @pyqtSlot(GalleryCard, Gallery)
    def gallery_card_double_click_slot(self, card: GalleryCard, gallery: Gallery):
        tab_widget_manager: QTabWidget = self.window().tab_widget_manager
        image_path = card.tag
        dataset_id = gallery.tag
        tab_widget = ImageViewerWidget()
        tab_widget.image_path = image_path
        tab_widget.image_dataset = dataset_id
        tab_widget.bind()
        tab_widget_manager.addTab(tab_widget,card.tag)
        tab_widget_manager.setCurrentIndex(1)

    @pyqtSlot(list)
    @gui_exception
    def gallery_files_dropped_slot(self, files: []):
        if self._ds_id is None:
            return
        entries_list = []
        for file_path in files:
            vo = DatasetEntryVO()
            vo.file_path = file_path
            vo.file_size = os.path.getsize(file_path)
            vo.dataset = self._ds_id
            entries_list.append(vo)
        self._ds_dao.add_entries(entries_list)
