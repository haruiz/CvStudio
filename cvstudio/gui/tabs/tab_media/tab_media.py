from pathlib import Path

import cv2
import dask
from hurry.filesize import size, alternative

from cvstudio.dao import DatasetDao
from cvstudio.decor import gui_exception, work_exception
from cvstudio.gui.tabs.tab_media.media_grid import MediaDataGrid
from cvstudio.gui.tabs.tab_media.media_grid_item import MediaDataGridItem
from cvstudio.gui.widgets import (
    ImageButton,
)
from cvstudio.gui.widgets.widgets_grid import WidgetsGridPaginator
from cvstudio.pyqt import (
    QtCore,
    QVBoxLayout,
    QHBoxLayout,
    QSize,
    QThreadPool,
    QWidget,
    QPixmap,
    Qt,
)
from cvstudio.util import GUIUtils, Worker
from cvstudio.vo import DatasetVO, DatasetEntryVO


class MediaTabWidget(QWidget):
    ITEMS_PER_PAGE = 50

    def __init__(self, dataset_vo: DatasetVO, parent=None):
        super(MediaTabWidget, self).__init__(parent)
        self._thread_pool = QThreadPool()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        icon = GUIUtils.get_icon("new_folder.png")
        self.btn_add_new_dataset = ImageButton(icon, size=QSize(32, 32))
        self.toolbox = QWidget()
        self.toolbox_layout = QHBoxLayout(self.toolbox)

        assets_path = GUIUtils.get_assets_path()
        loading_gif = assets_path.joinpath("icons/loading.gif")
        self.media_grid = MediaDataGrid()
        self.media_grid.loading_gif = loading_gif
        #self.media_grid.files_dropped.connect(self.data_grid_files_dropped_dispatch)
        #self.media_grid.double_click.connect(self.grid_card_double_click)

        self.media_grid_paginator = WidgetsGridPaginator()
        self.media_grid_paginator.bind()
        #self.media_grid_paginator.paginate.connect(self.page_changed)

        self.layout.addWidget(self.toolbox, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.media_grid)
        self.layout.addWidget(
            self.media_grid_paginator, alignment=QtCore.Qt.AlignHCenter
        )
        self.datasets_dao = DatasetDao()
        self.dataset_vo = dataset_vo

        self.load_data()

    def load_data(self):
        self.load_paginator()
        self.load_grid()

    @gui_exception
    def load_paginator(self):

        @work_exception
        def do_work():
            results = self.datasets_dao.count_files(self.dataset_vo.id)
            return results, None

        @gui_exception
        def done_work(result):
            count, error = result
            if error:
                raise error
            if count:
                self.media_grid_paginator.page_size = self.ITEMS_PER_PAGE
                self.media_grid_paginator.items_count = count
                self.media_grid_paginator.bind()

        worker = Worker(do_work)   # async worker
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)  # start worker

    def page_changed(self, curr_page, _):
        self.load_grid(page_number=curr_page + 1)

    @gui_exception
    def load_grid(self, page_number=1):
        pass





    #     self.load_paginator()
    #
    # @gui_exception
    # def data_grid_files_dropped_dispatch(self, files):
    #     # save the files into the db
    #     self.media_grid.is_loading = True
    #     self.media_grid_paginator.disable_actions()
    #
    #     @work_exception
    #     def do_work():
    #         delayed_tasks = map(lambda f: dask.delayed(f.stat().st_size), files)
    #         files_sizes = dask.compute(*delayed_tasks)
    #         entries = []
    #         for file_path, file_size in zip(files, files_sizes):
    #             vo = DatasetEntryVO()
    #             vo.file_path = file_path
    #             vo.file_size = file_size
    #             vo.dataset = self.dataset_vo.id
    #             entries.append(vo)
    #         self.datasets_dao.add_files(entries)
    #         return None, None
    #
    #     @gui_exception
    #     def done_work(result):
    #         items, error = result
    #         if error:
    #             raise error
    #         self.refresh_grid()
    #         self.media_grid.is_loading = False
    #         self.media_grid_paginator.disable_actions(False)
    #
    #     worker = Worker(do_work)
    #     worker.signals.result.connect(done_work)
    #     self._thread_pool.start(worker)
    #
    # @gui_exception
    # def load_grid(self, page_number=1):
    #     self.media_grid.is_loading = True
    #     self.media_grid_paginator.disable_actions()
    #
    #     @work_exception
    #     def do_work():
    #         results = self.datasets_dao.fetch_files(
    #             self.dataset_vo.id, page_number, self.ITEMS_PER_PAGE
    #         )
    #
    #         # load images from
    #         @dask.delayed
    #         def load_image(media_item_vo):
    #             media_item = MediaDataGridItem()
    #             # image = QImage(media_item_vo.file_path)
    #             # pixmap = QPixmap(media_item_vo.file_path)  # QPixmap.fromImage(image)image = cv2.imread(file_path)
    #
    #             image = cv2.imread(media_item_vo.file_path)
    #             image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #             pixmap = GUIUtils.array_to_qimage(image)
    #             pixmap = QPixmap.fromImage(pixmap)
    #             w = min(pixmap.width(), 150)
    #             h = min(pixmap.height(), 150)
    #             pixmap = pixmap.scaled(
    #                 w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation
    #             )
    #             media_item.thumbnail = pixmap
    #             file_size = int(media_item_vo.file_size)
    #             media_item.title = Path(media_item_vo.file_path).name
    #             file_sz_str = (
    #                 size(file_size, system=alternative) if file_size > 0 else "0 MB"
    #             )
    #             media_item.subtitle = (
    #                 f"({image.shape[0]}px x {image.shape[1]}px) \n {file_sz_str}"
    #             )
    #             media_item.tag = media_item_vo
    #             del image
    #             return media_item
    #
    #         return dask.compute(*map(load_image, results)), None
    #
    #     @gui_exception
    #     def done_work(result):
    #         items, error = result
    #         if error:
    #             raise error
    #
    #         self.media_grid.items = items
    #         self.media_grid.is_loading = False
    #         self.media_grid.bind()
    #         self.media_grid_paginator.disable_actions(False)
    #
    #     worker = Worker(do_work)  # async worker
    #     worker.signals.result.connect(done_work)
    #     self._thread_pool.start(worker)  # start worker
    #

    #
    # def refresh_grid(self):
    #     self.load_paginator()
    #     self.load_grid()
    #
    # def grid_card_double_click(self, item):
    #     print(item.file_path)
