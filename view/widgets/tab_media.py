import os

import cv2
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout

from dao import DatasetDao
from decor import gui_exception
from util import Worker, GUIUtilities as gui
from view.widgets.gallery import GalleryAction
from view.widgets.gallery.card import GalleryCard
from view.widgets.image_viewer.image_viewer_widget import ImageViewerWidget
from vo import DatasetEntryVO, DatasetVO
from .gallery import Gallery
from .loading_dialog import QLoadingDialog


class MediaTabWidget(QWidget):

    def __init__(self, ds, parent=None):
        super(MediaTabWidget, self).__init__(parent)
        self.media_grid = Gallery()
        self.media_grid.filesDropped.connect(self.gallery_files_dropped_slot)
        self.media_grid.doubleClicked.connect(self.gallery_card_double_click_slot)
        delete_action = GalleryAction(gui.get_icon("delete.png"), name="delete", tooltip="delete image")
        edit_action = GalleryAction(gui.get_icon("annotations.png"), name="edit", tooltip="edit annotations")
        # view_action=GalleryAction(gui.get_icon("search.png"),name="view")
        self.media_grid.actions = [delete_action, edit_action]
        self.media_grid.cardActionClicked.connect(self.card_action_clicked_slot)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.media_grid)
        self._thread_pool = QThreadPool()
        self._loading_dialog = QLoadingDialog()
        self._ds_dao = DatasetDao()
        self._ds: DatasetVO = ds
        self.load()

    def load(self):
        ds_id = self._ds.id

        def do_work():
            entries = self._ds_dao.fetch_entries(ds_id)
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

    def gallery_card_double_click_slot(self, card: GalleryCard, gallery: Gallery):
        # self.open_file(card.tag)
        pass

    @gui_exception
    def gallery_files_dropped_slot(self, files: []):
        entries_list = []
        for file_path in files:
            vo = DatasetEntryVO()
            vo.file_path = file_path
            vo.file_size = os.path.getsize(file_path)
            vo.dataset = self._ds.id
            entries_list.append(vo)

        def do_work():
            self._ds_dao.add_entries(entries_list)

        def done_work():
            self.load()

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)

    def open_file(self, entry: DatasetEntryVO):
        tab_widget_manager: QTabWidget = self.window().tab_widget_manager
        tab_widget = ImageViewerWidget()
        tab_widget.image = cv2.imread(entry.file_path)
        tab_widget.tag = entry
        tab_widget.bind()
        tab_widget.layout().setContentsMargins(0, 0, 0, 0)
        index = tab_widget_manager.addTab(tab_widget, entry.file_path)
        tab_widget_manager.setCurrentIndex(index)

    @gui_exception
    def card_action_clicked_slot(self, action_name: str, item: DatasetEntryVO):
        if action_name == "delete":
            self._ds_dao.delete_entry(item.id)
            self.load()
        elif action_name == "edit":
            self.open_file(item)
