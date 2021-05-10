import dask

from cvstudio.dao import DatasetDao, LabelDao, AnnDao
from cvstudio.gui.widgets import LabelsTable, LoadingDialog
from cvstudio.pyqt import (
    QWidget,
    QSplitter,
    Qt,
    QVBoxLayout,
    QTabWidget,
    QToolBox,
    QSizePolicy,
    QThreadPool,
)
from .image_graphicsview import ImageGraphicsView
from .image_viewer_toolbox import ImageViewerToolBox
from .selection_tool import SELECTION_TOOL
from cvstudio.decor import gui_exception, work_exception
from cvstudio.util import Worker

class ImageViewer(QWidget):
    def __init__(self, image_entry, *args, **kwargs):
        super(ImageViewer, self).__init__(*args, **kwargs)
        self.layout = QVBoxLayout(self)

        self.ann_toolbox = ImageViewerToolBox()
        self.ann_toolbox.onAction.connect(self.current_tool_changed)
        self.ann_toolbox.setFixedWidth(50)
        self.img_viewer = ImageGraphicsView()
        self.vsplitter = QSplitter(Qt.Vertical)
        self.vsplitter.setFixedWidth(300)

        hsplitter = QSplitter(Qt.Horizontal)
        hsplitter.addWidget(self.ann_toolbox)
        hsplitter.addWidget(self.img_viewer)
        hsplitter.addWidget(self.vsplitter)
        self.layout.addWidget(hsplitter)

        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        size_policy.setVerticalStretch(1)

        self._loading_dialog = LoadingDialog()
        self.labels_table = LabelsTable()

        tab_manager = QTabWidget()
        tab_manager.addTab(self.labels_table, "Labels")
        tab_manager.addTab(QWidget(), "Models Hub")
        tab_manager.setFixedHeight(400)
        tab_manager.setSizePolicy(size_policy)
        self.vsplitter.addWidget(tab_manager)

        toolbox = QToolBox()
        toolbox.addItem(QWidget(), "Images")
        toolbox.addItem(QWidget(), "Processing")
        toolbox.setSizePolicy(size_policy)
        self.vsplitter.addWidget(toolbox)
        self.vsplitter.setStretchFactor(0, 1)
        self.vsplitter.setStretchFactor(1, 1)

        self._ds_dao = DatasetDao()
        self._labels_dao = LabelDao()
        self._ann_dao = AnnDao()
        self._thread_pool = QThreadPool()
        self._image_entry = image_entry
        self.init()

    @property
    def image_entry(self):
        return self._image_entry

    @image_entry.setter
    def image_entry(self, value):
        self._image_entry = value

    @property
    def image(self):
        return self.img_viewer.image

    @image.setter
    def image(self, value):
        self.img_viewer.image = value

    def current_tool_changed(self, action_tag):
        tools_dict = {
            "polygon": SELECTION_TOOL.POLYGON,
            "box": SELECTION_TOOL.BOX,
            "ellipse": SELECTION_TOOL.ELLIPSE,
            "free": SELECTION_TOOL.FREE,
            "points": SELECTION_TOOL.EXTREME_POINTS,
            "pointer": SELECTION_TOOL.POINTER,
        }
        if action_tag in tools_dict:
            self.image_viewer.current_tool = tools_dict[action_tag]

    @dask.delayed
    def load_labels(self):
        dataset_id = self.image_entry.dataset
        return self._labels_dao.fetch_all(dataset_id)

    @dask.delayed
    def load_images(self):
        dataset_id = self.image_entry.dataset
        return self._ds_dao.fetch_files_by_page(dataset_id)

    @gui_exception
    def init(self):

        @work_exception
        def do_work():
            return dask.compute(*[
                self.load_labels()
            ]), None

        @gui_exception
        def done_work(args):
            result, error = args
            if result:
                pass


        self._loading_dialog.show()
        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)
