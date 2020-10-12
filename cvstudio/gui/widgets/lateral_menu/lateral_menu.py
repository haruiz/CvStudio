from enum import Enum, auto

from cvstudio.gui.widgets import ImageButton
from cvstudio.pyqt import (
    QWidget,
    QObject,
    Signal,
    QVBoxLayout,
    QFrame,
    Qt,
    QIcon,
    QSize,
)


class ItemLocation(Enum):
    TOP = auto()
    BOTTOM = auto()


class LateralMenu(QWidget, QObject):
    item_click = Signal(str)

    def __init__(self, parent=None, width=80):
        super(LateralMenu, self).__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        self.top_layout = QVBoxLayout()
        self.top_layout.setContentsMargins(5, 5, 5, 5)
        self.top_layout.setAlignment(Qt.AlignTop)

        self.bottom_layout = QVBoxLayout()
        self.bottom_layout.setContentsMargins(5, 5, 5, 5)
        self.bottom_layout.setAlignment(Qt.AlignBottom)

        self.bottom_frame = QFrame()
        self.bottom_frame.setFrameStyle(QFrame.NoFrame)
        self.bottom_frame.setLayout(self.bottom_layout)

        self.top_frame = QFrame()
        self.top_frame.setFrameStyle(QFrame.NoFrame)
        self.top_frame.setLayout(self.top_layout)

        layout.addWidget(self.top_frame)
        layout.addWidget(self.bottom_frame)

        self.setFixedWidth(width)

    def add_item(self, icon: QIcon, tooltip_text: str, name: str, loc=ItemLocation.TOP):
        button: ImageButton = ImageButton(icon=icon, size=QSize(64, 64))
        button.setToolTip(tooltip_text)
        button.clicked.connect(self.menu_item_on_click)
        button.setObjectName(name)
        layout = self.top_layout
        if loc == ItemLocation.BOTTOM:
            layout = self.bottom_layout
        layout.setSpacing(30)
        layout.addWidget(button, alignment=Qt.AlignHCenter)

    def menu_item_on_click(self):
        self.item_click.emit(self.sender().objectName())
