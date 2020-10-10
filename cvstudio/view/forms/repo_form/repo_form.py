from PyQt5.QtWidgets import QDialog

from cvstudio.util import GUIUtilities
from .base_repo_form import Ui_NewRepo


class NewRepoForm(QDialog, Ui_NewRepo):
    def __init__(self, parent=None):
        super(NewRepoForm, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("New Repository".title())
        self.setWindowIcon(GUIUtilities.get_icon("polygon.png"))
        self._result = None

    @property
    def result(self) -> str:
        return self._result

    def accept(self) -> None:
        repo = self.nameLineEdit.text()
        if repo:
            self._result = repo
        return QDialog.accept(self)
