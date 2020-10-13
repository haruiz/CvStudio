from cvstudio.pyqt import QWidget, QGridLayout, QObject
from cvstudio.util import GUIUtils


class WidgetsGridLayout(QGridLayout, QObject):
    def __init__(self, parent=None):
        super(WidgetsGridLayout, self).__init__(parent)
        self._widgets = None
        self.setContentsMargins(0,0,0,0)
        self._cols = 5

    @property
    def widgets(self):
        return self._widgets

    @widgets.setter
    def widgets(self, value):
        self._widgets = value
        self.notify_property_changed()

    @property
    def cols(self):
        return self._cols

    @cols.setter
    def cols(self, value):
        self._cols = value
        self.notify_property_changed()

    def notify_property_changed(self):
        self.update()

    def update(self) -> None:
        self.clear()
        if self.widgets:
            row = 0
            col = 0
            n = max(len(self.widgets), self.cols)
            for idx in range(n):
                #self.setColumnStretch(col, 1)
                #self.setRowStretch(row, 1)
                if idx < len(self.widgets):
                    widget = self.widgets[idx]
                    self.addWidget(widget, row, col)
                else:
                    self.addWidget(QWidget(), row, col)
                col += 1
                if col % self.cols == 0:
                    row += 1
                    col = 0

    def initialize(self, n_items):
        self.clear()
        row = 0
        col = 0
        n = max(n_items, self.cols)
        for idx in range(n):
            self.setColumnStretch(col, 1)
            self.setRowStretch(row, 1)
            self.addWidget(QWidget(), row, col)
            col += 1
            if col % self.cols == 0:
                row += 1
                col = 0

    def clear(self):
        GUIUtils.clear_layout(self)  # clear the gridlayout
