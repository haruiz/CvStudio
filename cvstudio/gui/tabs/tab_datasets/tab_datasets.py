from cvstudio.dao import DatasetDao
from cvstudio.decor import gui_exception, work_exception
from cvstudio.gui.forms import DatasetForm
from cvstudio.gui.widgets import ImageButton, WidgetsGridPaginator
from cvstudio.pyqt import (
    QtCore,
    QVBoxLayout,
    QHBoxLayout,
    QSize,
    QThreadPool,
    QWidget,
    QDialog,
    QMessageBox,
)
from cvstudio.util import GUIUtils, Worker
from cvstudio.vo import DatasetVO
from .datasets_grid import DatasetsGrid
from ..tab_media import MediaTabWidget


class DatasetTabWidget(QWidget):
    ITEMS_PER_PAGE = 50

    def __init__(self, parent=None):
        super(DatasetTabWidget, self).__init__(parent)

        self.datasets_dao = DatasetDao()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._thread_pool = QThreadPool()

        icon = GUIUtils.get_icon("new_folder.png")
        self.btn_add_new_dataset = ImageButton(icon, size=QSize(32, 32))
        self.toolbox = QWidget()
        self.toolbox.setFixedHeight(50)
        self.toolbox_layout = QHBoxLayout(self.toolbox)
        self.toolbox_layout.addWidget(self.btn_add_new_dataset)
        self.btn_add_new_dataset.clicked.connect(self.btn_add_new_dataset_click)

        self.datasets_grid = DatasetsGrid()
        self.datasets_grid.item_action_click.connect(self.grid_item_action_click)
        self.datasets_grid.item_double_click.connect(self.grid_item_double_click)

        self.datasets_grid_paginator = WidgetsGridPaginator()
        self.datasets_grid_paginator.paginate.connect(self.page_changed)
        self.datasets_grid_paginator.bind()

        self.load_data()

        self.layout.addWidget(self.toolbox, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.datasets_grid)
        self.layout.addWidget(
            self.datasets_grid_paginator, alignment=QtCore.Qt.AlignHCenter
        )

    def page_changed(self, curr_page, _):
        self.load_grid(page_number=curr_page + 1)

    def load_data(self):
        self.load_paginator()
        self.load_grid()

    @gui_exception
    def load_paginator(self):
        @work_exception
        def do_work():
            results = self.datasets_dao.count()
            return results, None

        @gui_exception
        def done_work(result):
            count, error = result
            if error:
                raise error
            if count:
                self.datasets_grid_paginator.page_size = self.ITEMS_PER_PAGE
                self.datasets_grid_paginator.items_count = count
                self.datasets_grid_paginator.bind()

        worker = Worker(do_work)  # async worker
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)  # start worker

    #
    @gui_exception
    def load_grid(self, page_number=1):
        self.datasets_grid.is_loading = True

        @work_exception
        def do_work():
            results = self.datasets_dao.fetch_all_with_size(
                page_number, self.ITEMS_PER_PAGE
            )
            return results, None

        @gui_exception
        def done_work(result):
            items, error = result
            if error:
                raise error
            self.datasets_grid.items = items
            self.datasets_grid.is_loading = False
            self.datasets_grid.bind()

        worker = Worker(do_work)  # async worker
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)  # start worker

    def grid_item_action_click(self, action_name, item: QWidget):
        item_id = item.property("data").id
        if action_name == "delete":
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Are you sure?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.datasets_dao.delete(item_id)
                self.load_data()

    @gui_exception
    def grid_item_double_click(self, item: QWidget):
        vo = item.property("data")
        tab_widget_manager = self.window().tabs_manager
        tab_widget = MediaTabWidget(vo)
        self.window().close_tab_by_type(MediaTabWidget)
        # for i in range(tab_widget_manager.count()):
        #     tab_widget_manager.removeTab(i)
        index = tab_widget_manager.addTab(tab_widget, vo.name)
        tab_widget_manager.setCurrentIndex(index)

    @gui_exception
    def btn_add_new_dataset_click(self, _):
        form = DatasetForm()
        if form.exec_() == QDialog.Accepted:
            vo = DatasetVO()
            vo.name = form.name
            vo.description = form.description
            self.datasets_dao.save(vo)
            curr_page = self.datasets_grid_paginator.current_page
            self.load_grid(curr_page)
            self.load_paginator()
