from abc import abstractmethod, ABCMeta
from pathlib import Path

from cvstudio.pyqt import (
    QWidget,
    QtCore,
    QFrame,
    QVBoxLayout,
    Qt,
    QScrollArea,
    QLabel,
    QObject,
    QMovie,
)
from cvstudio.util import GUIUtils
from .grid_layout import WidgetsGridLayout


class WidgetsGrid(QWidget, QObject):
    __metaclass__ = ABCMeta

    def __init__(self, parent=None, ncols=8):
        super(WidgetsGrid, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.loading_gif = None
        self.no_data_message = "Not data"
        self._is_loading = False
        self.items = []
        self.ncols = ncols
        self.bind()

    @property
    def is_loading(self):
        return self._is_loading

    @is_loading.setter
    def is_loading(self, value):
        self._is_loading = value
        self.bind()

    @abstractmethod
    def build(self, item: object) -> QWidget:
        raise NotImplemented

    def clear(self):
        GUIUtils.clear_layout(self.layout)

    def bind(self):
        self.clear()
        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)
        if self.is_loading:
            label_loading = QLabel("is loading....")
            if self.loading_gif and Path(self.loading_gif).exists():
                movie = QMovie(str(self.loading_gif))
                label_loading.setMovie(movie)
                movie.start()
            center_widget = QWidget()
            center_widget_layout = QVBoxLayout(center_widget)
            center_widget_layout.setAlignment(QtCore.Qt.AlignCenter)
            center_widget_layout.addWidget(label_loading)
            scroll_area.setWidget(center_widget)
        else:
            if self.items:
                widgets = []
                grid_widget = QWidget()
                grid_layout = WidgetsGridLayout(grid_widget)
                grid_layout.cols = self.ncols
                grid_layout.setAlignment(QtCore.Qt.AlignTop)
                for data_item in self.items:
                    item_frame = QFrame()
                    item_frame_layout = QVBoxLayout(item_frame)
                    item_frame_layout.setContentsMargins(0, 0, 0, 0)
                    item_widget: QWidget = self.build(data_item)
                    item_widget.setProperty("data", data_item)
                    item_frame_layout.addWidget(item_widget, alignment=Qt.AlignTop)
                    widgets.append(item_frame)
                grid_layout.widgets = widgets
                scroll_area.setWidget(grid_widget)
            else:
                center_widget = QWidget()
                center_widget_layout = QVBoxLayout(center_widget)
                center_widget_layout.setContentsMargins(0, 0, 0, 0)
                center_widget_layout.setAlignment(QtCore.Qt.AlignCenter)
                center_widget_layout.addWidget(QLabel(self.no_data_message))
                scroll_area.setWidget(center_widget)
