from cvstudio.pyqt import (
    QDialog,
    QLineEdit,
    QTextEdit,
    QFormLayout,
    QDialogButtonBox,
    Qt,
)

from cvstudio.util import GUIUtils


class DatasetForm(QDialog):
    def __init__(self, parent=None):
        super(DatasetForm, self).__init__(parent)
        self.resize(361, 218)

        self.setWindowTitle("New Dataset")
        txt_name = QLineEdit()
        txt_name.setObjectName("txt_name")

        txt_description = QTextEdit()
        txt_description.setObjectName("txt_description")

        layout = QFormLayout(self)
        layout.addRow(self.tr("Name:"), txt_name)
        layout.addRow(self.tr("Description:"), txt_description)

        buttons_box = QDialogButtonBox()
        buttons_box.setOrientation(Qt.Horizontal)
        buttons_box.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        layout.addWidget(buttons_box)
        buttons_box.accepted.connect(self.accept)
        buttons_box.rejected.connect(self.reject)

    name = GUIUtils.bind("txt_name", "text", str)
    description = GUIUtils.bind("txt_description", "plainText", str)

    def accept(self) -> None:
        if not self.name:
            GUIUtils.show_error_message("The field name is required", "Info")
            return
        return super(DatasetForm, self).accept()

    def reject(self) -> None:
        return super(DatasetForm, self).reject()
