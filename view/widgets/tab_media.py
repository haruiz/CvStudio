import math
import os
import time
import numpy as np
import cv2
import imutils
from PyQt5 import QtCore
from PyQt5.QtCore import QThreadPool,QModelIndex,QFileInfo,QObject,QSize
from PyQt5.QtGui import QDropEvent,QPixmap,QImage
from PyQt5.QtWidgets import QScrollArea,QFrame,QVBoxLayout,QLabel,QWidget,QGridLayout,QHBoxLayout

from util import Worker,GUIUtilities
from .response_grid_card import GridCard
from .response_grid import ResponseGridLayout
from .image_button import ImageButton
from .loading_dialog import QLoadingDialog

class ImagesGridWidget(QWidget):
    def __init__(self, parent=None):
        super(ImagesGridWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.grid_layout=ResponseGridLayout()
        #self.grid_layout.cols = 6
        self.setLayout(self.grid_layout)
        self._images=None

    @property
    def images(self):
        return self._images

    @images.setter
    def images(self,value):
        self._images=value
        self.update()

    def dragEnterEvent(self,event):
        m=event.mimeData()
        if m.hasUrls():
            if any(url.isLocalFile() for url in m.urls()):
                event.accept()
                return
        else:
            event.ignore()

    def dragMoveEvent(self,event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            return
        else:
            event.ignore()

    def dropEvent(self,event: QDropEvent):
        if event.source():
            QFrame.dropEvent(self,event)
        else:
            m = event.mimeData()
            if m.hasUrls():
                url_locals = [url for url in m.urls() if url.isLocalFile()]
                paths = []
                for urlLocal in url_locals:
                    path=urlLocal.toLocalFile()
                    info=QFileInfo(path)
                    paths.append(info.absoluteFilePath())
                paths=sorted(paths)
                self.images = paths

    def new_image_card_factory(self,image_path: str):
        _, ext = os.path.splitext(image_path)
        if ext == ".jpg":
            card_widget: GridCard=GridCard()
            card_widget.setFixedHeight(200)
            btn_delete=ImageButton(GUIUtilities.get_icon("delete.png"),size=QSize(15,15))
            btn_edit=ImageButton(GUIUtilities.get_icon("annotations.png"),size=QSize(15,15))
            btn_view=ImageButton(GUIUtilities.get_icon("search.png"),size=QSize(15,15))
            card_widget.add_buttons([btn_delete,btn_edit,btn_view])

            pixmap=QPixmap(image_path)
            pixmap=pixmap.scaled(QSize(150,150),aspectRatioMode=QtCore.Qt.KeepAspectRatio,transformMode=QtCore.Qt.SmoothTransformation)
            card_widget.label="({0}px / {1}px)".format(pixmap.width(),pixmap.height())

            image_widget=QLabel()
            image_widget.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            #image_widget.setScaledContents(True)
            image_widget.setStyleSheet("QLabel { background-color : black;}")

            image_widget.setPixmap(pixmap)
            card_widget.body=image_widget
            card_widget.body_frame.setObjectName("image_card")

            return card_widget
        return None

    def update(self) -> None:
        list_widgets = []
        for img in self.images:
            card = self.new_image_card_factory(img)
            if card:
                list_widgets.append(card)
        self.grid_layout.widgets = list_widgets
        super(ImagesGridWidget, self).update()

class MediaTabWidget(QScrollArea):
    def __init__(self, parent=None):
        super(MediaTabWidget, self).__init__(parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.central_widget = ImagesGridWidget()
        self.setWidget(self.central_widget)
        self.setWidgetResizable(True)
        self.thread_pool=QThreadPool()
        self.loading_dialog = QLoadingDialog()
        self.load()

    def load(self):
        def do_work():
            pass

        def done_work(result):
            self.loading_dialog.close()

        worker=Worker(do_work)
        worker.signals.result.connect(done_work)
        self.thread_pool.start(worker)
        self.loading_dialog.exec_()