from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QWizard,QWizardPage,QComboBox,QFormLayout,QSpinBox,QWidget,QVBoxLayout,QDoubleSpinBox
from core import  Framework, ApiClient, ApiClientFactory
from PyQt5 import QtCore

from core.pytorch_api_client import PytorchCVDataset
from dao import DatasetDao
from util import GUIUtilities,Worker


class ModelPicker(QComboBox):
    def __init__(self, parent=None, provider = Framework.PyTorch):
        super(ModelPicker,self).__init__(parent)
        self._api_client = ApiClientFactory.create(provider)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        models = self._api_client.list_models()
        for m in models:
            self.addItem(m)


class DatasetPicker(QComboBox):
    def __init__(self, parent=None):
        super(DatasetPicker, self).__init__(parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._thread_pool=QThreadPool()
        self.load()

    def load(self):
        def do_work():
            ds_dao=DatasetDao()
            return ds_dao.fetch_all()

        def done_work(result):
            for ds in result:
                self.addItem(ds.name, ds.id)

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)


class BaseModelSelectionPage(QWizardPage):
    def __init__(self, parent=None):
        super(BaseModelSelectionPage, self).__init__(parent)
        self.setTitle("Base Model Selection")
        self._layout = QVBoxLayout(self)
        _model_section_widget = QWidget()
        _section_layout = QFormLayout(_model_section_widget)
        self.ds_picker = DatasetPicker()
        self._arch_picker = ModelPicker()
        self._num_of_epochs_picker = QSpinBox()
        self._num_of_workers_picker=QSpinBox()
        self._batch_size_picker=QSpinBox()
        self._learning_rate_picker = QDoubleSpinBox()
        self._learning_momentum_picker=QDoubleSpinBox()
        self._learning_weight_decay_picker=QDoubleSpinBox()
        self._learning_weight_decay_picker=QDoubleSpinBox()
        _section_layout.addRow(self.tr("Dataset: "),self.ds_picker)
        _section_layout.addRow(self.tr("Architecture: "), self._arch_picker)
        _section_layout.addRow(self.tr("Number of epochs: "),self._num_of_epochs_picker)
        _section_layout.addRow(self.tr("Number of workers: "),self._num_of_workers_picker)
        _section_layout.addRow(self.tr("Batch Size: "),self._batch_size_picker)
        _section_layout.addRow(self.tr("Learning rate: "),self._learning_rate_picker)
        self._layout.addWidget(GUIUtilities.wrap_with_groupbox(_model_section_widget,"Model Details"))




class ModelWizard(QWizard):
    def __init__(self, parent=None):
        super(ModelWizard, self).__init__(parent)
        self.setWindowIcon(GUIUtilities.get_icon("pytorch.png"))
        self.setWindowTitle("New Model")
        self.resize(800, 600)
        self.setWizardStyle(QWizard.ClassicStyle)
        self._model_selection_page = BaseModelSelectionPage()
        self.addPage(self._model_selection_page)
        self.button(QWizard.FinishButton).clicked.connect(self.finish_button_click)

    def finish_button_click(self):
        index = self._model_selection_page.ds_picker.currentIndex()
        ds_id = self._model_selection_page.ds_picker.itemData(index)
        api_client = ApiClientFactory.create(Framework.PyTorch)
        dataset = api_client.build_dataset(ds_id)


        #apiClient = ApiClientFactory.create(Framework.PyTorch)
        #apiClient.build_dataset()