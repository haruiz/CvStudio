import math

from cvstudio.gui.widgets import ImageButton, Separator
from cvstudio.util import GUIUtils
from cvstudio.pyqt import QObject, Signal, QSize, QFrame, QHBoxLayout, QLabel


class WidgetsGridPaginator(QFrame, QObject):
    paginate = Signal(int, int)

    def __init__(self, parent=None):
        super(WidgetsGridPaginator, self).__init__(parent)
        self.layout = QHBoxLayout(self)
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
        self.label.setText(f"Number of entries: {self._items_count}, items per page {self._page_size},  Page: {self.current_page} of {self._pages_count}  ")
        self.paginate.emit(self._current_page, self._page_size)

    def disable_actions(self, flag=True):
        self.btn_first.setDisabled(flag)
        self.btn_next.setDisabled(flag)
        self.btn_prev.setDisabled(flag)
        self.btn_last.setDisabled(flag)

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