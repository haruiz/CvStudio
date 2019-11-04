from enum import Enum,auto

from PyQt5 import QtGui
from PyQt5.QtCore import QSize,Qt,QObject,pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QMenu,QPushButton,QFrame,QSizePolicy,QGraphicsDropShadowEffect
from view.widgets.image_button import ImageButton

class LateralMenuItemLoc(Enum):
    TOP = auto()
    BOTTOM = auto()


class LateralMenu(QWidget, QObject):
    item_click_signal=pyqtSignal(str)

    def __init__(self, parent=None):
        super(LateralMenu, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.top_frame = QFrame()
        #size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        #self.frame.setSizePolicy(size_policy)
        #self.top_frame.setFixedWidth(90)
        self.top_frame.setFrameStyle(QFrame.NoFrame)
        self.top_frame_layout = QVBoxLayout()
        self.top_frame_layout.setContentsMargins(2,2,2,2)
        self.top_frame_layout.setAlignment(Qt.AlignTop)
        self.top_frame.setLayout(self.top_frame_layout)

        self.bottom_frame=QFrame()
        #self.bottom_frame.setFixedWidth(90)
        self.bottom_frame.setFrameStyle(QFrame.NoFrame)
        self.bottom_frame_layout=QVBoxLayout()
        self.bottom_frame_layout.setContentsMargins(2,2,2,2)
        self.bottom_frame_layout.setAlignment(Qt.AlignBottom)
        self.bottom_frame.setLayout(self.bottom_frame_layout)

        self.layout().addWidget(self.top_frame)
        self.layout().addWidget(self.bottom_frame)
        self.items = []


    def add_item(self, icon: QIcon, tooltip_text: str, name: str, loc=LateralMenuItemLoc.TOP):
        button : ImageButton = ImageButton(icon=icon, size=QSize(64,64))
        button.setToolTip(tooltip_text)
        button.setObjectName('lateral_menu_button')
        button.clicked.connect(self.menu_button_on_click_event)
        button.setObjectName(name)
        if loc == LateralMenuItemLoc.TOP:
            self.top_frame_layout.setSpacing(30)
            self.top_frame_layout.addWidget(button)
        else:
            self.bottom_frame_layout.setSpacing(30)
            self.bottom_frame_layout.addWidget(button)
        self.items.append(button)

    def menu_button_on_click_event(self):
        self.item_click_signal.emit(self.sender().objectName())

