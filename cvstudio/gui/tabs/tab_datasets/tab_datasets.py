from cvstudio.dao import DatasetDao
from cvstudio.decor import gui_exception, work_exception
from cvstudio.gui.forms import DatasetForm
from cvstudio.gui.tabs.tab_datasets.datasets_grid import DatasetsGrid
from cvstudio.gui.widgets import ImageButton
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
from ..tab_media import MediaTabWidget
from ...widgets.widgets_grid import WidgetsGridPaginator


class DatasetTabWidget(QWidget):
    ITEMS_PER_PAGE = 100

    def __init__(self, parent=None):
        super(DatasetTabWidget, self).__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._thread_pool = QThreadPool()

        icon = GUIUtils.get_icon("new_folder.png")
        self.btn_add_new_dataset = ImageButton(icon, size=QSize(32, 32))
        self.toolbox = QWidget()
        self.toolbox_layout = QHBoxLayout(self.toolbox)
        self.toolbox_layout.addWidget(self.btn_add_new_dataset)
        self.btn_add_new_dataset.clicked.connect(self.btn_add_new_dataset_click)

        self.data_grid = DatasetsGrid()

        self.data_grid.bind()
        self.data_grid.action_signal.connect(self.grid_card_action_dispatch)
        self.data_grid.double_click_action_signal.connect(self.grid_card_double_click)
        self.data_grid_paginator = WidgetsGridPaginator()
        self.data_grid_paginator.paginate.connect(self.page_changed)

        self.layout.addWidget(self.toolbox, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.data_grid)
        self.layout.addWidget(
            self.data_grid_paginator, alignment=QtCore.Qt.AlignHCenter
        )
        self.datasets_dao = DatasetDao()
        self.load_paginator()

    def page_changed(self, curr_page, _):
        self.load_grid(page_number=curr_page + 1)

    def refresh_grid(self):
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
                self.data_grid_paginator.page_size = self.ITEMS_PER_PAGE
                self.data_grid_paginator.items_count = count
                self.data_grid_paginator.bind()

        worker = Worker(do_work)  # async worker
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)  # start worker

    @gui_exception
    def load_grid(self, page_number=1):
        self.data_grid.is_loading = True

        @work_exception
        def do_work():
            results = self.datasets_dao.fetch(page_number, self.ITEMS_PER_PAGE)
            return results, None

        @gui_exception
        def done_work(result):
            items, error = result
            if error:
                raise error
            self.data_grid.items = items
            self.data_grid.is_loading = False
            self.data_grid.bind()

        worker = Worker(do_work)  # async worker
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)  # start worker

    def grid_card_action_dispatch(self, action_name, item):
        if action_name == "delete":
            reply = QMessageBox.question(
                self,
                "Confirmation",
                "Are you sure?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.datasets_dao.delete(item.id)
                self.refresh_grid()

    @gui_exception
    def grid_card_double_click(self, vo):
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
            vo = form.vo
            self.datasets_dao.save(vo)
            curr_page = self.data_grid_paginator.current_page
            self.load_grid(curr_page)
            self.load_paginator()
