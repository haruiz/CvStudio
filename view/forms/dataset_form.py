import os

from PyQt5.QtWidgets import QDialog

from util import GUIUtilities,FileUtilities
from vo import DatasetVO
from .base_dataset_form import Ui_Base_DatasetDialog


class DatasetForm(QDialog, Ui_Base_DatasetDialog):
    def __init__(self, parent=None):
        super(DatasetForm, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Create new dataset".title())
        self.setWindowIcon(GUIUtilities.get_icon("python.png"))
        self._value = None

    @property
    def value(self):
        return self._value

    def accept(self) -> None:
        usr_folder = FileUtilities.get_data_path()
        ds_folder = os.path.basename(FileUtilities.create_new_folder(usr_folder))
        vo = DatasetVO()
        vo.folder = ds_folder
        vo.name = self.nameLineEdit.text()
        vo.description = self.descriptionEditText.toPlainText()
        vo.data_type = self.typeComboBox.currentText()
        self._value = vo
        return QDialog.accept(self)

    def reject(self) -> None:
        return QDialog.reject(self)
