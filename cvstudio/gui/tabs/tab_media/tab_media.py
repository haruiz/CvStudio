from pathlib import Path

import dask
import numpy as np
from PIL import Image
from hurry.filesize import size, alternative

from cvstudio.dao import DatasetDao
from cvstudio.decor import gui_exception, work_exception
from cvstudio.gui.tabs.tab_media.media_grid import MediaDataGrid
from cvstudio.gui.tabs.tab_media.media_grid_item import MediaDataGridItem
from cvstudio.gui.widgets import (
    ImageButton,
)
from cvstudio.gui.widgets.image_viewer import ImageViewer
from cvstudio.gui.widgets.widgets_grid import WidgetsGridPaginator
from cvstudio.pyqt import (
    QtCore,
    QVBoxLayout,
    QHBoxLayout,
    QSize,
    QThreadPool,
    QWidget,
    QPixmap,
    QMessageBox,
    QTabWidget,
)
from cvstudio.util import GUIUtils, Worker
from cvstudio.vo import DatasetVO, DatasetEntryVO


class MediaTabWidget(QWidget):
    ITEMS_PER_PAGE = 50
    IMAGE_DIMS = 150, 150

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
        self.media_grid.files_dropped.connect(self.data_grid_files_dropped)
        self.media_grid.item_double_click.connect(self.grid_card_double_click)
        self.media_grid.item_action_click.connect(self.grid_item_action_click)

        self.media_grid_paginator = WidgetsGridPaginator()
        self.media_grid_paginator.bind()
        self.media_grid_paginator.paginate.connect(self.page_changed)

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

        worker = Worker(do_work)  # async worker
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)  # start worker

    def page_changed(self, curr_page, _):
        self.load_grid(page_number=curr_page + 1)

    @gui_exception
    def load_grid(self, page_number=1):
        self.media_grid.is_loading = True
        self.media_grid_paginator.disable_actions()

        @work_exception
        def do_work():
            results = self.datasets_dao.fetch_files_by_page(
                self.dataset_vo.id, page_number, self.ITEMS_PER_PAGE
            )

            @dask.delayed
            def load_image(data_item):
                media_item = MediaDataGridItem()
                media_file = Path(data_item.file_path)
                if media_file.exists():
                    image = Image.open(data_item.file_path)
                    img_width = image.width
                    img_height = image.height
                    image.thumbnail(self.IMAGE_DIMS)
                    image = np.array(image)
                    qimage = GUIUtils.array_to_qimage(image)
                    pixmap = QPixmap.fromImage(qimage)
                    media_item.thumbnail = pixmap
                    media_item.data_item = data_item
                    media_item.title = media_file.name
                    file_size = int(data_item.file_size)
                    media_item.title = Path(data_item.file_path).name
                    file_sz_str = (
                        size(file_size, system=alternative) if file_size > 0 else "0 MB"
                    )
                    media_item.subtitle = (
                        f"({img_width}px x {img_height}px) \n {file_sz_str}"
                    )
                else:
                    thumbnail = GUIUtils.get_image("placeholder.png")
                    thumbnail = thumbnail.scaledToHeight(self.IMAGE_DIMS[0])
                    media_item.thumbnail = thumbnail
                    media_item.enabled = False
                    media_item.title = media_file.name
                    media_item.data_item = data_item
                    media_item.subtitle = "Not Found"
                return media_item

            return dask.compute(*map(load_image, results)), None

        @gui_exception
        def done_work(result):
            items, error = result
            if error:
                raise error

            self.media_grid.items = items
            self.media_grid.is_loading = False
            self.media_grid.bind()
            self.media_grid_paginator.disable_actions(False)

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)

    @gui_exception
    def data_grid_files_dropped(self, files):
        self.media_grid.is_loading = True
        self.media_grid_paginator.disable_actions()

        @work_exception
        def do_work():
            delayed_tasks = map(lambda f: dask.delayed(f.stat().st_size), files)
            files_sizes = dask.compute(*delayed_tasks)
            entries = []
            for file_path, file_size in zip(files, files_sizes):
                vo = DatasetEntryVO()
                vo.file_path = file_path
                vo.file_size = file_size
                vo.dataset = self.dataset_vo.id
                entries.append(vo)
            self.datasets_dao.add_files(entries)
            return None, None

        @gui_exception
        def done_work(result):
            items, error = result
            if error:
                raise error
            self.load_data()
            self.media_grid.is_loading = False
            self.media_grid_paginator.disable_actions(False)

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)

    def open_file(self, image_entry):
        tab_widget_manager = self.window().tabs_manager
        tab_widget = ImageViewer(image_entry)
        image_path = image_entry.file_path
        tab_widget.image = Image.open(image_path)
        self.window().close_tab_by_type(ImageViewer)
        img_name = Path(image_entry.file_path).name
        index = tab_widget_manager.addTab(tab_widget, img_name)
        tab_widget_manager.setCurrentIndex(index)

    def grid_card_double_click(self, item: QWidget):
        image_entry = item.property("data").data_item
        self.open_file(image_entry)

    def grid_item_action_click(self, action_name, item):
        item = item.property("data").data_item
        item_id = item.id
        if action_name == "delete":
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Are you sure?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.datasets_dao.delete_file(item_id)
                self.load_data()
