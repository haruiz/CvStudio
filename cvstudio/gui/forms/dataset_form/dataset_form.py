from cvstudio.pyqt import (
    QDialog,
    QFormLayout,
    Qt,
    QLineEdit,
    QPlainTextEdit,
    QtWidgets,
    QtCore,
)
from cvstudio.util import GUIUtils
from cvstudio.vo import DatasetVO


class DatasetForm(QDialog):
    def __init__(self, vo=None, parent=None):
        super(DatasetForm, self).__init__(parent)
        self.resize(341, 146)
        self.setWindowTitle("New Dataset")
        self.setWindowIcon(GUIUtils.get_icon("polygon.png"))
        self.form_layout = QFormLayout(self)
        self.nameLineEdit = QLineEdit()
        self.descriptionEditText = QPlainTextEdit()
        self.form_layout.addRow(self.tr("Name"), self.nameLineEdit)
        self.form_layout.addRow(self.tr("Description"), self.descriptionEditText)
        self.buttonsbox = QtWidgets.QDialogButtonBox()
        self.buttonsbox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonsbox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.form_layout.addWidget(self.buttonsbox)
        self.buttonsbox.accepted.connect(self.accept)
        self.buttonsbox.rejected.connect(self.reject)
        self._vo = vo
        self.initialize_form()

    def initialize_form(self):
        if self._vo:
            self.nameLineEdit.setText(self._value.name)
            self.descriptionEditText.setPlainText(self._value.description)

    @property
    def vo(self):
        return self._vo

    @vo.setter
    def vo(self, value):
        self._vo = value

    def accept(self) -> None:
        if not self.nameLineEdit.text():
            GUIUtils.show_info_message("The name field is required", "info")
            return
        if self._vo is None:
            self.vo = DatasetVO()
        self.vo.name = self.nameLineEdit.text()
        self.vo.description = self.descriptionEditText.toPlainText()
        return QDialog.accept(self)

    def reject(self) -> None:
        return QDialog.reject(self)
