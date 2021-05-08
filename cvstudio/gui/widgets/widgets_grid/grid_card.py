import typing

from cvstudio.pyqt import (
    QtCore,
    QObject,
    QFrame,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
    QHBoxLayout,
    QPushButton,
    QWidget,
    Signal,
    QMouseEvent,
)


class WidgetsGridCard(QFrame, QObject):

    def __init__(self, parent=None, debug=False, with_actions=True, with_title=True):
        super(WidgetsGridCard, self).__init__(parent)
        self._card_actions = []
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self.setLayout(self._content_layout)
        self._title_widget = QLabel()
        self._title_widget.setStyleSheet("QLabel { font-size : 14px;}")
        self._title_widget.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self._title_widget.setScaledContents(True)
        self._sub_title_widget = QLabel()
        self._sub_title_widget.setStyleSheet("QLabel { font-size : 10px;}")
        self._sub_title_widget.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
        )
        self._sub_title_widget.setScaledContents(True)
        self._body_widget = None
        # layouts
        self._body_frame = QFrame()
        # self._body_frame.setMinimumWidth(width)
        self._body_frame.setObjectName("image_container")
        self._body_frame.setLayout(QVBoxLayout())
        self._body_frame.layout().setContentsMargins(2, 2, 2, 2)
        self._body_frame.layout().setAlignment(QtCore.Qt.AlignHCenter)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setVerticalStretch(4)
        self._body_frame.setSizePolicy(size_policy)
        self._title_frame = QFrame()
        self._title_frame.setLayout(QVBoxLayout())
        self._title_frame.layout().setContentsMargins(2, 2, 2, 2)
        self._title_frame.layout().addWidget(self._title_widget)
        self._title_frame.layout().addWidget(self._sub_title_widget)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setVerticalStretch(1)
        self._title_frame.setSizePolicy(size_policy)
        self._actions_frame = QFrame()
        self._actions_frame.setLayout(QHBoxLayout())
        self._actions_frame.setFixedHeight(30)
        self._actions_frame.layout().setContentsMargins(0, 0, 0, 0)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setVerticalStretch(2)
        self._actions_frame.setSizePolicy(size_policy)
        # self._body_frame.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Ex)
        # self._title_frame.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        # self._actions_frame.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self._content_layout.addWidget(self._body_frame)
        if with_title:
            self._content_layout.addWidget(self._title_frame)
        if with_actions:
            self._content_layout.addWidget(
                self._actions_frame, alignment=QtCore.Qt.AlignCenter
            )
        if debug:
            self.setFrameStyle(QFrame.Box)
            self._body_frame.setFrameStyle(QFrame.Box)
            self._title_frame.setFrameStyle(QFrame.Box)
            self._actions_frame.setFrameStyle(QFrame.Box)

    def add_actions(self, args: typing.Union[QPushButton, list]):
        if isinstance(args, QPushButton):
            self._actions_frame.layout().addWidget(args)
        else:
            for btn in args:
                if isinstance(btn, QPushButton):
                    self._actions_frame.layout().addWidget(btn)

    @property
    def body(self) -> QWidget:
        return self._body_widget

    @body.setter
    def body(self, value):
        self._body_widget = value
        self._body_frame.layout().addWidget(value)

    @property
    def body_frame(self):
        return self._body_frame

    @property
    def title(self):
        return self._title_widget

    @title.setter
    def title(self, value):
        self._title_widget.setText(value)

    @property
    def subtitle(self):
        return self._sub_title_widget

    @subtitle.setter
    def subtitle(self, value):
        self._sub_title_widget.setText(value)

    @property
    def card_actions(self):
        return self._card_actions

    @card_actions.setter
    def card_actions(self, value: dict):
        self._card_actions = value
        for action_btn in self._card_actions:
            self._actions_frame.layout().addWidget(action_btn)

