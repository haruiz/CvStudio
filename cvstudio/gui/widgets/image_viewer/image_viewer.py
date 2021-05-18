from PIL import Image

from cvstudio.dao import DatasetDao, LabelDao, AnnDao
from cvstudio.gui.widgets import DatasetLabelsTable, LoadingDialog, ImageListWidget
from cvstudio.pyqt import (
    QWidget,
    QSplitter,
    Qt,
    QVBoxLayout,
    QTabWidget,
    QToolBox,
    QSizePolicy,
    QThreadPool,
    QtGui,
    Qt,
    QListWidgetItem
)
from .image_graphicsview import ImageGraphicsView
from .image_viewer_toolbox import ImageViewerToolBox
from .selection_tool import SELECTION_TOOL
from cvstudio.decor import gui_exception, work_exception

class ImageViewer(QWidget):
    def __init__(self, image_entry, *args, **kwargs):
        super(ImageViewer, self).__init__(*args, **kwargs)
        self.layout = QVBoxLayout(self)

        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.ann_toolbox = ImageViewerToolBox()
        self.ann_toolbox.onAction.connect(self.current_tool_changed)
        self.ann_toolbox.setFixedWidth(50)
        self.ann_toolbox.setSizePolicy(size_policy)

        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(4)
        size_policy.setVerticalStretch(0)
        self.img_viewer = ImageGraphicsView()
        self.img_viewer.setSizePolicy(size_policy)

        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.vsplitter = QSplitter(Qt.Vertical)
        self.vsplitter.setMinimumWidth(300)
        self.vsplitter.setSizePolicy(size_policy)

        hsplitter = QSplitter(Qt.Horizontal)
        hsplitter.addWidget(self.ann_toolbox)
        hsplitter.addWidget(self.img_viewer)
        hsplitter.addWidget(self.vsplitter)
        self.layout.addWidget(hsplitter)

        dataset_id = image_entry.dataset
        self._loading_dialog = LoadingDialog()
        self._ds_labels_table = DatasetLabelsTable(dataset_id)
        self._image_list_widget = ImageListWidget(image_entry)
        self._image_list_widget.currentItemChanged.connect(self.image_list_selection_changed)

        tab_manager = QTabWidget()
        tab_manager.addTab(self._ds_labels_table, "Labels")
        # tab_manager.addTab(QWidget(), "Models Hub")
        self.vsplitter.addWidget(tab_manager)

        toolbox = QToolBox()
        toolbox.addItem(self._image_list_widget, "Images")
        # toolbox.addItem(QWidget(), "Processing")
        self.vsplitter.addWidget(toolbox)

        # self.vsplitter.setStretchFactor(0, 1)
        # self.vsplitter.setStretchFactor(1, 1)
        #self.vsplitter.setSizes([1, 1])

        self._ds_dao = DatasetDao()
        self._labels_dao = LabelDao()
        self._ann_dao = AnnDao()
        self._thread_pool = QThreadPool()
        self._image_entry = image_entry

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
            self.img_viewer.current_tool = tools_dict[action_tag]


    @gui_exception
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        row = self._image_list_widget.currentRow()
        last_index = self._image_list_widget.count() - 1
        if event.key() == Qt.Key_A:
            if row > 0:
                self._image_list_widget.setCurrentRow(row - 1)
            else:
                self._image_list_widget.setCurrentRow(last_index)
        elif event.key() == Qt.Key_D:
            if row < last_index:
                self._image_list_widget.setCurrentRow(row + 1)
            else:
                self._image_list_widget.setCurrentRow(0)
                
        super(ImageViewer, self).keyPressEvent(event)

    @gui_exception
    def image_list_selection_changed(self, selected_item: QListWidgetItem, prev):
        curr_image_entry = selected_item.data(Qt.UserRole)
        self.image = Image.open(curr_image_entry.file_path)
        self.img_viewer.update_viewer()
