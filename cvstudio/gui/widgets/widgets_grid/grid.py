import math
from abc import abstractmethod, ABCMeta

from cvstudio.gui.widgets import ImageButton, Separator
from cvstudio.pyqt import (
    QWidget,
    QtCore,
    QHBoxLayout,
    QFrame,
    QVBoxLayout,
    Qt,
    QScrollArea,
    QSize,
    QLabel,
    QObject,
    Signal,
)
from cvstudio.util import GUIUtils
from .grid_layout import WidgetsGridLayout


class WidgetsGridPaginator(QWidget, QObject):
    paginate = Signal(int, int)

    def __init__(self, parent=None):
        super(WidgetsGridPaginator, self).__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self._page_size = 10
        self._pages_count = 0
        self._current_page = 0
        self._items_count = 0

        icon = GUIUtils.get_icon("right.png")
        self.btn_next = ImageButton(icon, size=QSize(20, 20))
        self.btn_next.setFixedWidth(40)
        self.btn_next.clicked.connect(self.btn_next_page_click)

        icon = GUIUtils.get_icon("left.png")
        self.btn_prev = ImageButton(icon, size=QSize(20, 20))
        self.btn_prev.setFixedWidth(40)
        self.btn_prev.clicked.connect(self.btn_prev_page_click)

        icon = GUIUtils.get_icon("last.png")
        self.btn_last = ImageButton(icon, size=QSize(20, 20))
        self.btn_last.setFixedWidth(40)
        self.btn_last.clicked.connect(self.btn_last_page_click)

        icon = GUIUtils.get_icon("first.png")
        self.btn_first = ImageButton(icon, size=QSize(20, 20))
        self.btn_first.setFixedWidth(40)
        self.btn_first.clicked.connect(self.btn_first_page_click)

        self.label = QLabel()
        self.label.setFixedWidth(100)
        self.layout.addWidget(self.btn_first)
        self.layout.addWidget(self.btn_prev)
        self.layout.addWidget(Separator())
        self.layout.addWidget(self.label)
        self.layout.addWidget(Separator())
        self.layout.addWidget(self.btn_next)
        self.layout.addWidget(self.btn_last)

    @property
    def items_count(self):
        return self._items_count

    @items_count.setter
    def items_count(self, value):
        assert value > 0, "Invalid items count parameter"
        self._items_count = value


    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self, value):
        assert value > 0, "Invalid page size parameter"
        self._page_size = value

    @property
    def current_page(self):
        return self._current_page + 1

    @current_page.setter
    def current_page(self, val):
        self._current_page = val
        self._current_page = self._current_page % self._pages_count

    def bind(self):
        self._pages_count = math.ceil(self._items_count / self._page_size)
        self.label.setText(f"{self.current_page} of {self._pages_count}")
        self.paginate.emit(self._current_page, self._page_size)

    def btn_next_page_click(self):
        self._current_page += 1
        self.current_page = self._current_page
        self.bind()

    def btn_last_page_click(self):
        self._current_page = self._pages_count - 1
        self.bind()

    def btn_first_page_click(self):
        self._current_page = 0
        self.bind()

    def btn_prev_page_click(self):
        self._current_page -= 1
        self.current_page = self._current_page
        self.bind()


class WidgetsGrid(QScrollArea, QObject):
    __metaclass__ = ABCMeta

    def __init__(self, parent=None, ncols=8):
        super(WidgetsGrid, self).__init__(parent)
        self._items = []
        self._empty_widget = QLabel("Not Data Found")
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid_layout = WidgetsGridLayout(self.grid_widget)
        self.grid_layout.cols = ncols
        self.grid_layout.setAlignment(QtCore.Qt.AlignTop)


    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, value):
        self._items = value

    @abstractmethod
    def create_widget(self, item: object) -> QWidget:
        raise NotImplemented

    @property
    def empty_widget(self):
        return self._empty_widget

    @empty_widget.setter
    def empty_widget(self, value):
        self._empty_widget = value

    def bind(self):
        widgets = []
        if self._items:
            if self.widget() != self.grid_widget:
                self.setWidget(self.grid_widget)
            for curr_item in self._items:
                item_frame = QFrame()
                item_frame_layout = QVBoxLayout(item_frame)
                item_frame_layout.setContentsMargins(0, 0, 0, 0)
                curr_widget: QWidget = self.create_widget(curr_item)
                item_frame_layout.addWidget(curr_widget, alignment=Qt.AlignTop)
                widgets.append(item_frame)
            self.grid_layout.widgets = widgets
        else:
            center_widget = QWidget()
            center_layout = QVBoxLayout(center_widget)
            center_layout.setAlignment(QtCore.Qt.AlignCenter)
            center_layout.addWidget(self._empty_widget)
            self.setWidget(center_widget)
