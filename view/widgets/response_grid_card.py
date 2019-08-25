import typing
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import QSize,QObject,pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QFrame,QVBoxLayout,QLabel,QWidget,QHBoxLayout,QPushButton,QSizePolicy

from util import GUIUtilities
from .image_button import ImageButton


class GridCard(QFrame, QObject):
    def __init__(self, parent=None, debug=False, with_actions= True, with_title=True):
        super(GridCard,self).__init__(parent)
        self._buttons=[]

        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0,0,0,0)
        self._content_layout.setSpacing(0)
        self.setLayout(self._content_layout)
        self.setFixedHeight(150)

        self._title_widget = QLabel()
        self._title_widget.setStyleSheet("QLabel { font-size : 14px;}")
        self._title_widget.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self._title_widget.setScaledContents(True)
        self._body_widget = None

        # layouts

        self._body_frame = QFrame()
        self._body_frame.setMinimumWidth(150)
        self._body_frame.setObjectName("image_container")
        self._body_frame.setLayout(QVBoxLayout())
        self._body_frame.layout().setContentsMargins(2,2,2,2)
        self._body_frame.layout().setAlignment(QtCore.Qt.AlignHCenter)
        size_policy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        size_policy.setVerticalStretch(4)
        self._body_frame.setSizePolicy(size_policy)

        self._title_frame=QFrame()
        self._title_frame.setLayout(QVBoxLayout())
        self._title_frame.layout().setContentsMargins(2,2,2,2)
        self._title_frame.layout().addWidget(self._title_widget)
        size_policy=QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        size_policy.setVerticalStretch(1)
        self._title_frame.setSizePolicy(size_policy)

        self._actions_frame=QFrame()
        self._actions_frame.setLayout(QHBoxLayout())
        self._actions_frame.layout().setContentsMargins(2,2,2,2)
        size_policy=QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        size_policy.setVerticalStretch(2)
        self._actions_frame.setSizePolicy(size_policy)

        # self._body_frame.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Ex)
        # self._title_frame.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        # self._actions_frame.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)

        self._content_layout.addWidget(self._body_frame)
        if with_title:
            self._content_layout.addWidget(self._title_frame)
        if with_actions:
            self._content_layout.addWidget(self._actions_frame, alignment=QtCore.Qt.AlignCenter)

        if debug:
            self.setFrameStyle(QFrame.Box)
            self._body_frame.setFrameStyle(QFrame.Box)
            self._title_frame.setFrameStyle(QFrame.Box)
            self._actions_frame.setFrameStyle(QFrame.Box)

    def add_buttons(self, args: typing.Any):
        if isinstance(args,QPushButton):
            self._actions_frame.layout().addWidget(args)
        else:
            for btn in args:
                if isinstance(btn, QPushButton):
                    self._actions_frame.layout().addWidget(btn)

    @property
    def body(self)->QWidget:
        return self._body_widget

    @body.setter
    def body(self,value):
        self._body_widget = value
        self._body_frame.layout().addWidget(value)

    @property
    def body_frame(self):
        return self._body_frame

    @property
    def label(self):
        return  self._title_widget.text()

    @label.setter
    def label(self, value):
        self._title_widget.setText(value)

    @property
    def buttons(self):
        return self._buttons

    @buttons.setter
    def buttons(self, value):
        self._buttons = value
        for btn in self._buttons:
            self._actions_frame.layout().addWidget(btn)



