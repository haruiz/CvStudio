import os
import typing
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import QObject,pyqtSignal,pyqtSlot,QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget,QPushButton,QLabel
from abc  import abstractmethod
from util import GUIUtilities
from ..image_button import ImageButton
from .gallery_action import GalleryAction
from .label_hovered import LabelHovered
from .base_card import Ui_GalleryCard
from .video_dialog import VideoDialog
from .image_dialog import ImageDialog


class GalleryCard(QWidget, Ui_GalleryCard, QObject):
    doubleClicked = pyqtSignal(QWidget)
    actionClicked = pyqtSignal(str,object)
    selected_style ="""
               QFrame {
                   background-color: gray;
                    border-width: 1px;
                    border-radius: 8px
                }
            """

    unselected_style = """
               QFrame {
                   background-color: black;
                    border-width: 1px;
                    border-radius: 8px
                }
            """

    def __init__(self, parent=None):
        super(GalleryCard, self).__init__(parent)
        self.setupUi(self)
        self.label_text.setStyleSheet("QLabel{ font-size: 12px; }")
        self.buttons_layout.setAlignment(QtCore.Qt.AlignCenter)
        self._is_selected = False
        self._tag = None
        self._file_path = None

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

    @property
    @abstractmethod
    def source(self):
        raise NotImplementedError

    @source.setter
    @abstractmethod
    def source(self, value):
        raise NotImplementedError

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    @property
    def thumbnail(self):
        if self.thumbnail_layout.count() > 0:
            return self.thumbnail_layout.itemAt(0)
        else:
            return None

    @thumbnail.setter
    def thumbnail(self, widget: QWidget):
        GUIUtilities.clear_layout(self.thumbnail_layout)
        widget.setCursor(QtCore.Qt.PointingHandCursor)
        widget.setStyleSheet(self.unselected_style)
        self.thumbnail_layout.addWidget(widget)

    @property
    def label(self):
        return self.label_text

    @label.setter
    def label(self, value):
        self.label_text.setText(value)
        
    @property
    def is_selected(self):
        return self._is_selected
    
    @is_selected.setter
    def is_selected(self, value):
        self._is_selected  = value
        if self.is_selected and self.thumbnail:
            self.thumbnail.widget().setStyleSheet(self.selected_style)
        else:
            self.thumbnail.widget().setStyleSheet(self.unselected_style)

    def mouseDoubleClickEvent(self, evt: QtGui.QMouseEvent) -> None:
        if self.childAt(evt.pos()) == self.thumbnail.widget():
            self.doubleClicked.emit(self)

    def mousePressEvent(self, evt: QtGui.QMouseEvent) -> None:
        if evt.button() == QtCore.Qt.LeftButton:
            if self.childAt(evt.pos()) == self.thumbnail.widget():
                self.is_selected=not self.is_selected

    def add_buttons(self, args: typing.Any):
        if isinstance(args,GalleryAction):
            button = ImageButton(args.icon)
            button.tag = args.name
            button.setToolTip(args.tooltip)
            button.clicked.connect(self.action_clicked_slot)
            self.buttons_layout.addWidget(button)
        else:
            for action in args:
                if isinstance(action, GalleryAction):
                    button=ImageButton(action.icon, size=QSize(15,15))
                    button.tag= action.name
                    button.setToolTip(action.tooltip)
                    button.clicked.connect(self.action_clicked_slot)
                    button.setFixedWidth(30)
                    self.buttons_layout.addWidget(button)

    def action_clicked_slot(self):
        self.actionClicked.emit(self.sender().tag, self.tag)




class ImageCard(GalleryCard):
    def __init__(self, parent=None):
        super(ImageCard, self).__init__(parent)
        # self.setFont(QtGui.QFont("Times", 2, QtGui.QFont.Bold) )
        self._image_source = None
        self._image_widget = LabelHovered()
        self._image_widget.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.thumbnail = self._image_widget
        self._image_widget.hoverTimeout.connect(self.hover_timeout_slot)

    @pyqtSlot(QLabel)
    def hover_timeout_slot(self):
        if self.file_path:
            viewer=ImageDialog(self.file_path)
            viewer.exec_()

    @property
    def source(self):
        return self._image_source

    @source.setter
    def source(self,pixmap):
        self._image_source = pixmap
        self._image_widget.setPixmap(pixmap)



class   VideoCard(GalleryCard):
    def __init__(self, parent=None):
        super(VideoCard, self).__init__(parent)
        self._duration = None
        self._video_source=None
        self._video_widget=LabelHovered()
        self._video_widget.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.thumbnail=self._video_widget
        self._video_widget.hoverTimeout.connect(self.hover_timeout_slot)

    @pyqtSlot(QLabel)
    def hover_timeout_slot(self):
        if self.file_path:
            viewer = VideoDialog(self.tag)
            viewer.exec_()

    @property
    def source(self):
        return self._video_source

    @source.setter
    def source(self,value):
        self._video_source=value
        qimage=GUIUtilities.array_to_qimage(self._video_source)
        pixmap = QPixmap.fromImage(qimage)
        pixmap=pixmap.scaledToHeight(120,mode=QtCore.Qt.SmoothTransformation)
        # pixmap=pixmap.scaled(QSize(150,150),aspectRatioMode=QtCore.Qt.KeepAspectRatio,transformMode=QtCore.Qt.SmoothTransformation)
        # image_widget.setScaledContents(True)
        self._video_widget.setPixmap(pixmap)

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration = value






