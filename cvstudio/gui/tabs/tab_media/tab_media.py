import math
import mimetypes
from pathlib import Path
import dask
from cvstudio.dao import DatasetDao
from cvstudio.decor import gui_exception, work_exception
from cvstudio.gui.widgets import (
    WidgetsGrid,
    ImageButton,
    WidgetsGridPaginator,
    WidgetsGridCard,
)
from hurry.filesize import size, alternative
from cvstudio.pyqt import (
    QtCore,
    QVBoxLayout,
    QHBoxLayout,
    QSize,
    QThreadPool,
    QWidget,
    QDialog,
    QtGui,
    QObject,
    Signal,
    QLabel,
    QPixmap,
    Qt
)
from cvstudio.util import GUIUtils, Worker
from cvstudio.vo import DatasetVO, DatasetEntryVO, dataset_vo
import cv2
import numpy as np
import imutils

# class ImageCard(WidgetsGridCard):
#     def __init__(self, parent=None):
#         super(ImageCard, self).__init__(parent)
#         # self.setFont(QtGui.QFont("Times", 2, QtGui.QFont.Bold) )
#         self._image_source = None
#
#         self._image_widget = LabelHovered()
#         self._image_widget.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
#         self.thumbnail = self._image_widget
#         self._image_widget.hoverTimeout.connect(self.hover_timeout_slot)
#
#     def hover_timeout_slot(self):
#         if self.file_path and not self.is_broken:
#             viewer = ImageDialog(self.file_path)
#             viewer.exec_()
#
#     @property
#     def source(self):
#         return self._image_source
#
#     @source.setter
#     def source(self, pixmap):
#         self._image_source = pixmap
#         self._image_widget.setPixmap(pixmap)


class MediaDataGrid(WidgetsGrid, QObject):
    files_dropped = Signal(list)

    def __init__(self, parent=None, ncols=8):
        super(MediaDataGrid, self).__init__(parent, ncols)
        self.setAcceptDrops(True)

    def create_widget(self, item: DatasetEntryVO) -> QWidget:
        # image = cv2.imread(item.file_path)
        # h, w, _ = np.shape(image)
        # if w > h:
        #     thumbnail_array = imutils.resize(image, width=self._item_height)
        # else:
        #     thumbnail_array = imutils.resize(image, height=self._item_height)
        # thumbnail_array = cv2.cvtColor(thumbnail_array, cv2.COLOR_BGR2RGB)
        # thumbnail = GUIUtils.array_to_qimage(thumbnail_array)
        #thumbnail = QPixmap(item.file_path)  # QPixmap.fromImage(thumbnail)
        # if thumbnail.width() > thumbnail.height():
        #     thumbnail = thumbnail.scaledToWidth(
        #         200, mode=QtCore.Qt.SmoothTransformation
        #     )
        # else:
        #     thumbnail = thumbnail.scaledToHeight(
        #         200, mode=QtCore.Qt.SmoothTransformation
        #     )
        # thumbnail = thumbnail.scaled(
        #     200, 200#,mode=QtCore.Qt.SmoothTransformation
        # )
        card = WidgetsGridCard(debug=False)
        label = QLabel()
        label.setFixedSize(QSize(150,150))
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        pixmap = QPixmap(item.file_path)  # QPixmap.fromImage(thumbnail)
        w = min(pixmap.width(), label.maximumWidth())
        h = min(pixmap.height(), label.maximumHeight())
        pixmap = pixmap.scaled(
            w,
            h,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        label.setPixmap(pixmap)
        file_size = int(item.file_size)
        file_sz_str = size(file_size, system=alternative) if file_size > 0 else "0 MB"
        card.label2.setText(f"({pixmap.width()}px x {pixmap.height()}px) \n {file_sz_str}")
        card.body = label
        card.label = Path(item.file_path).name
        btn_delete = ImageButton(GUIUtils.get_icon("delete.png"), size=QSize(15, 15))
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setToolTip("Delete dataset")
        btn_edit = ImageButton(GUIUtils.get_icon("annotations.png"), size=QSize(15, 15))
        btn_edit.setToolTip("Annotate")
        btn_edit.setCursor(Qt.PointingHandCursor)
        card.add_buttons(
            [
                btn_delete,
                btn_edit
            ]
        )

        return card

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        data = event.mimeData()
        if data.hasUrls():
            if any(url.isLocalFile() for url in data.urls()):
                event.accept()
                return
        else:
            event.ignore()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            return
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        valid_files = []
        files = [Path(u.toLocalFile()) for u in event.mimeData().urls()]
        for f in files:
            if f.is_file():
                mime_type, encoding = mimetypes.guess_type(str(f))
                if mime_type.find("image") != -1:
                    valid_files.append(f)
        valid_files = sorted(valid_files, key=lambda f: f.name)
        self.files_dropped.emit(valid_files)


class MediaTabWidget(QWidget):
    ITEMS_PER_PAGE = 100

    def __init__(self, dataset_vo: DatasetVO, parent=None):
        super(MediaTabWidget, self).__init__(parent)
        self._thread_pool = QThreadPool()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        icon = GUIUtils.get_icon("new_folder.png")
        self.btn_add_new_dataset = ImageButton(icon, size=QSize(32, 32))
        self.toolbox = QWidget()
        self.toolbox_layout = QHBoxLayout(self.toolbox)
        # self.toolbox_layout.addWidget(self.btn_add_new_dataset)
        # self.btn_add_new_dataset.clicked.connect(self.btn_add_new_dataset_click)

        self.data_grid = MediaDataGrid()
        self.data_grid.files_dropped.connect(self.data_grid_files_dropped_dispatch)
        self.data_grid.bind()
        # self.data_grid.action_signal.connect(self.grid_card_action_dispatch)
        # self.data_grid.double_click_action_signal.connect(self.grid_card_double_click)
        self.data_grid_paginator = WidgetsGridPaginator()
        self.data_grid_paginator.paginate.connect(self.page_changed)

        self.layout.addWidget(self.toolbox, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.data_grid)
        self.layout.addWidget(
            self.data_grid_paginator, alignment=QtCore.Qt.AlignHCenter
        )
        self.datasets_dao = DatasetDao()
        self.dataset_vo = dataset_vo
        self.load_paginator()

    @gui_exception
    def data_grid_files_dropped_dispatch(self, files):
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
            GUIUtils.show_info_message("Files loaded successfully")

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)

    @gui_exception
    def load_grid(self, page_number=1):
        @work_exception
        def do_work():
            results = self.datasets_dao.fetch_files(
                self.dataset_vo.id, page_number, self.ITEMS_PER_PAGE
            )
            return results, None

        @gui_exception
        def done_work(result):
            items, error = result
            if error:
                raise error
            self.data_grid.items = items
            self.data_grid.bind()

        worker = Worker(do_work)  # async worker
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)  # start worker

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
                self.data_grid_paginator.page_size = self.ITEMS_PER_PAGE
                self.data_grid_paginator.items_count = count
                self.data_grid_paginator.bind()

        worker = Worker(do_work)  # async worker
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)  # start worker

    def page_changed(self, curr_page, _):
        self.load_grid(page_number=curr_page + 1)
