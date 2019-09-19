import os

from PyQt5.QtWidgets import QDialog

from util import GUIUtilities,FileUtilities
from vo import DatasetVO
from .base_dataset_form import Ui_Base_DatasetDialog


class DatasetForm(QDialog, Ui_Base_DatasetDialog):
    def __init__(self,vo: DatasetVO = None, parent=None):
        super(DatasetForm, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Create new dataset".title())
        self.setWindowIcon(GUIUtilities.get_icon("pytorch.png"))
        self._value = vo
        self.initialize_form()

    def initialize_form(self):
        if self._value:
            self.nameLineEdit.setText(self._value.name)
            self.descriptionEditText.setPlainText(self._value.description)
            self.typeComboBox.setCurrentText(self._value.data_type)

    @property
    def value(self)-> DatasetVO:
        return self._value

    def accept(self) -> None:
        if not self.nameLineEdit.text():
            GUIUtilities.show_info_message("The name field is required","info")
            return
        if self._value is None:
            usr_folder=FileUtilities.get_usr_folder()
            new_folder=FileUtilities.create_new_folder(usr_folder)
            vo=DatasetVO()
            ds_folder=os.path.basename(new_folder)
            vo.folder=ds_folder
            self._value = vo
        else:
            vo = self._value
        vo.name=self.nameLineEdit.text()
        vo.description=self.descriptionEditText.toPlainText()
        vo.data_type=self.typeComboBox.currentText()
        return QDialog.accept(self)

    def reject(self) -> None:
        return QDialog.reject(self)
