from pathlib import Path

from cvstudio.pyqt import QListWidget, QThreadPool, QAbstractItemView, Qt, QListWidgetItem
from cvstudio.dao import DatasetDao
from cvstudio.util import GUIUtils, Worker
from cvstudio.decor import gui_exception, work_exception


class ImageListWidget(QListWidget):
    def __init__(self, current_image, *args, **kwargs):
        super(ImageListWidget, self).__init__(*args, **kwargs)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setCursor(Qt.PointingHandCursor)
        self._current_image = current_image
        self._ds_dao = DatasetDao()
        self._thread_pool = QThreadPool()
        self.load_data()

    @gui_exception
    def load_data(self):
        dataset_id = self._current_image.dataset
        curr_image_id = self._current_image.id

        @work_exception
        def do_work():
            images = self._ds_dao.fetch_files_by_ds(dataset_id)
            return images, None

        @gui_exception
        def done_work(args):
            images, error = args
            if error:
                raise error
            icon = GUIUtils.get_icon("image.png")
            selected_item = None
            for img in images:
                img_file = Path(img.file_path)
                if img_file.exists():
                    item = QListWidgetItem(img_file.name)
                    item.setIcon(icon)
                    item.setData(Qt.UserRole, img)
                    self.addItem(item)
                    if curr_image_id == img.id:
                        selected_item = item
            self.setCurrentItem(selected_item)

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)
