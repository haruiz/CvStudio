import math
import time
import numpy as np
import cv2
import imutils
from PyQt5 import QtCore
from PyQt5.QtCore import QThreadPool,QModelIndex,QFileInfo,QObject,QSize
from PyQt5.QtGui import QDropEvent,QPixmap,QImage
from PyQt5.QtWidgets import QScrollArea,QFrame,QVBoxLayout,QLabel,QWidget,QGridLayout,QHBoxLayout

from util import Worker,GUIUtilities
from .image_button import ImageButton
from .loading_dialog import QLoadingDialog


class ImageCard(QFrame):
    def __init__(self, parent=None):
        super(ImageCard, self).__init__(parent)
        #self.setFrameStyle(QFrame.Box)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0,0,0,0)
        content_layout.setSpacing(0)
        self.setLayout(content_layout)

        self._image_widget = QLabel()
        self._image_widget.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        #self._image_widget.setScaledContents(True)
        self._image_widget.setStyleSheet("QLabel { background-color : black;}")
        self._image_widget.setObjectName("image_container")

        self._title_widget = QLabel()
        self._title_widget.setStyleSheet("QLabel { font-size : 12px;}")
        self._title_widget.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self._title_widget.setScaledContents(True)
        self._actions_widget = QWidget()

        # layouts
        image_container = QFrame()
        #image_container.setFrameStyle(QFrame.Box)
        image_container.setFixedHeight(200)
        image_container.setLayout(QVBoxLayout())
        #image_container.layout().setContentsMargins(2,2,2,2)
        image_container.layout().addWidget(self._image_widget)

        title_container=QFrame()
        #title_container.setFrameStyle(QFrame.Box)
        title_container.setFixedHeight(30)
        title_container.setLayout(QVBoxLayout())
        title_container.layout().setContentsMargins(2,2,2,2)
        title_container.layout().addWidget(self._title_widget)

        actions_container=QFrame()
        actions_container.setFixedHeight(30)
        actions_container.setFixedWidth(80)
        actions_container.setLayout(QHBoxLayout())
        actions_container.layout().setContentsMargins(0,0,0,0)

        self.btn_delete_action=ImageButton(GUIUtilities.get_icon("delete.png"),size=QSize(15,15))
        self.btn_delete_action.setToolTip("delete")
        self.btn_edit_action=ImageButton(GUIUtilities.get_icon("edit.png"),size=QSize(15,15))
        self.btn_delete_action.setToolTip("edit")
        self.btn_view_action=ImageButton(GUIUtilities.get_icon("search.png"),size=QSize(15,15))
        self.btn_delete_action.setToolTip("view")
        actions_container.layout().addWidget(self.btn_delete_action)
        actions_container.layout().addWidget(self.btn_edit_action)
        actions_container.layout().addWidget(self.btn_view_action)

        #actions_container.setFrameStyle(QFrame.Box)

        content_layout.addWidget(image_container, alignment=QtCore.Qt.AlignHCenter)
        content_layout.addWidget(title_container,alignment=QtCore.Qt.AlignHCenter)
        content_layout.addWidget(actions_container,alignment=QtCore.Qt.AlignHCenter)

    @property
    def image(self):
        return self._image_widget

    @image.setter
    def image(self, value):
        img: np.ndarray = cv2.imread(value)
        if isinstance(img, np.ndarray):
            # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # img = imutils.resize(img, height=200, width=200)
            # height,width,_=img.shape
            # q_img=QImage(img.data,width,height,img.strides[0],QImage.Format_RGB888)
            # pixmap=QPixmap.fromImage(q_img)
            # #pixmap = pixmap.scaled(width, height,aspectRatioMode=QtCore.Qt.KeepAspectRatio)
            # self._image_widget.setPixmap(pixmap)
            # self._image_widget.setScaledContents(True)
            pixmap=QPixmap(value)
            self.label="({0}px / {1}px)".format(pixmap.width(),pixmap.height())
            pixmap=pixmap.scaled(QSize(200,200),aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)
            self._image_widget.setPixmap(pixmap)

    @property
    def label(self):
        return  self._title_widget.text()

    @label.setter
    def label(self, value):
        self._title_widget.setText(value)


class ImagesGridLayout(QGridLayout, QObject):

    def __init__(self, parent=None):
        super(ImagesGridLayout, self).__init__(parent)
        self._images = None
        self._images_by_row = 4

    @property
    def images(self):
        return self._images

    @images.setter
    def images(self,value):
        self._images = value
        self.update()

    @property
    def images_by_row(self):
        return self._images_by_row

    @images_by_row.setter
    def images_by_row(self, value):
        self._images_by_row = value

    def update(self) -> None:
        GUIUtilities.clear_layout(self)
        if self.images and len(self.images) > 0:
            row=col=0
            for idx,img in enumerate(self.images):
                media_card = ImageCard()
                media_card.image = img
                #media_card.setFixedHeight(self._preferred_height)
                self.addWidget(media_card,row,col)
                self.setColumnStretch(col,1)
                self.setRowStretch(row,1)
                col += 1
                if col%self.images_by_row == 0:
                    row+= 1
                    col = 0
        super(ImagesGridLayout, self).update()


class ImagesGridWidget(QWidget):
    def __init__(self, parent=None):
        super(ImagesGridWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setLayout(ImagesGridLayout())


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
                self.import_images(paths)

    def import_images(self, images: []):
        images_grid_layout = self.layout()
        images_grid_layout.images_by_row=5
        images_grid_layout.images = images


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