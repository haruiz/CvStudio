from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget, QGridLayout

from cvstudio.util import GUIUtilities


class ResponseGridLayout(QGridLayout, QObject):
    def __init__(self, parent=None):
        super(ResponseGridLayout, self).__init__(parent)
        self._widgets = None
        self._cols = 5

    @property
    def widgets(self):
        return self._widgets

    @widgets.setter
    def widgets(self, value):
        self._widgets = value
        self.update()

    @property
    def cols(self):
        return self._cols

    @cols.setter
    def cols(self, value):
        self._cols = value
        self.update()

    def update(self) -> None:
        GUIUtilities.clear_layout(self)
        if self.widgets and len(self.widgets) > 0:
            row = col = 0
            n = max(len(self.widgets), self.cols)
            for idx in range(n):
                self.setColumnStretch(col, 1)
                self.setRowStretch(row, 1)
                if idx < len(self.widgets):
                    widget = self.widgets[idx]
                    self.addWidget(widget, row, col)
                else:
                    self.addWidget(QWidget(), row, col)
                col += 1
                if col % self.cols == 0:
                    row += 1
                    col = 0

    def add_widget(self):
        pass
