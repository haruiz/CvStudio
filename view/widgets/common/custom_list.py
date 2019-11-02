from PyQt5.QtWidgets import QListWidgetItem


class CustomListWidgetItem(QListWidgetItem):
    def __init__(self,*args, **kwargs):
        super(CustomListWidgetItem, self).__init__(*args, **kwargs)
        self._tag = None

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value