import mimetypes
import os
from enum import Enum,auto

import cv2
import dask
import imutils
import numpy as np
from PyQt5 import QtGui,QtCore
from PyQt5.QtCore import QObject,QSize,pyqtSignal,QThreadPool
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget,QGridLayout,QLabel,QLayoutItem,QVBoxLayout
from hurry.filesize import size,alternative
from util import GUIUtilities,MiscUtilities,Worker
from view.widgets.image_button import ImageButton
from view.widgets.loading_dialog import QLoadingDialog
from .base_gallery import Ui_Gallery
from .card import GalleryCard,ImageCard


class GalleryViewMode(Enum):
    GRID_MODE=auto()
    LIST_MODE=auto()


class GalleryLayout(QGridLayout,QObject):

    def __init__(self,parent=None):
        super(GalleryLayout,self).__init__(parent)
        self.setAlignment(QtCore.Qt.AlignTop)
        self._items=[]
        self._view_mode=GalleryViewMode.GRID_MODE
        self._cols=8

    @property
    def view_mode(self):
        return self._view_mode

    @view_mode.setter
    def view_mode(self,value):
        self._view_mode=value

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self,value):
        self._items=value

    @property
    def cols(self):
        return self._cols

    @cols.setter
    def cols(self,value):
        self._cols=value
        self.notify_property_changed()

    def notify_property_changed(self):
        self.update()

    def arrange(self) -> None:
        self.clear()
        if len(self.items) > 0:
            row=col=0
            n=max(len(self.items),self.cols)
            for idx in range(n):
                self.setColumnStretch(col,1)
                self.setRowStretch(row,1)
                if idx < len(self.items):
                    widget=self.items[idx]
                    self.addWidget(widget,row,col)
                else:
                    self.addWidget(QWidget(),row,col)
                col+=1
                if col%self.cols == 0:
                    row+=1
                    col=0

    def initialize(self,n_items):
        self.clear()
        row=col=0
        n=max(n_items,self.cols)
        for idx in range(n):
            self.setColumnStretch(col,1)
            self.setRowStretch(row,1)
            self.addWidget(QWidget(),row,col)
            col+=1
            if col%self.cols == 0:
                row+=1
                col=0

    def add_item(self,widget: QWidget):
        if self.rowCount() > 0:
            cols=self.columnCount()
            rows=self.rowCount()
            for r in range(rows):
                for c in range(cols):
                    item: QLayoutItem=self.itemAtPosition(r,c)
                    if not isinstance(item.widget(),type(widget)):
                        self.removeWidget(item.widget())
                        self.addWidget(widget,r,c)
                        self.items.append(widget)
                        # self.update()
                        return

    def clear(self):
        GUIUtilities.clear_layout(self)  # clear the gridlayout


class Gallery(QWidget,Ui_Gallery,QObject):
    doubleClicked=pyqtSignal(GalleryCard,QWidget)
    filesDropped=pyqtSignal(list)
    cardActionClicked=pyqtSignal(str,object)

    def __init__(self,parent=None):
        super(Gallery,self).__init__(parent)
        self.setupUi(self)
        self.setup_toolbar()
        self.setup_paginator()
        self._items: []=[]
        self._pages=[]
        self._page_size=50
        self._curr_page=0
        self._thread_pool=QThreadPool()
        self.setAcceptDrops(True)
        self.center_widget=None
        self.center_layout=None
        self._content_type="Images"
        self._tag=None
        self._actions=[]
        self._loading_dialog=QLoadingDialog(parent=self)

    def setup_toolbar(self):
        uncheck_all_icon=GUIUtilities.get_icon("uncheck_all.png")
        self.btn_uncheck_all=ImageButton(icon=uncheck_all_icon,size=QSize(20,20))
        check_all_icon=GUIUtilities.get_icon("check_all.png")
        self.btn_check_all=ImageButton(icon=check_all_icon,size=QSize(20,20))
        self.btn_check_all.setFixedWidth(40)
        self.btn_uncheck_all.setFixedWidth(40)
        self.btn_check_all.clicked.connect(self.btn_check_all_on_click_slot)
        self.btn_uncheck_all.clicked.connect(self.btn_uncheck_all_on_click_slot)

    @property
    def actions(self):
        return self._actions

    @actions.setter
    def actions(self,value):
        self._actions=value


    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self,value):
        self._content_type=value

    def enable_paginator(self,val):
        self.btn_check_all.setEnabled(val)
        self.btn_uncheck_all.setEnabled(val)
        self.btn_next_page.setEnabled(val)
        self.btn_prev_page.setEnabled(val)
        self.btn_last_page.setEnabled(val)
        self.btn_first_page.setEnabled(val)

    def setup_paginator(self):
        self.grid_actions_layout.addWidget(self.btn_check_all)
        self.grid_actions_layout.addWidget(self.btn_uncheck_all)
        self.btn_next_page.clicked.connect(self.btn_next_page_on_click)
        self.btn_prev_page.clicked.connect(self.btn_prev_page_on_click)
        self.btn_last_page.clicked.connect(self.btn_last_page_on_click)
        self.btn_first_page.clicked.connect(self.btn_first_page_on_click)
        self.btn_first_page.setIcon(GUIUtilities.get_icon("first.png"))
        self.btn_prev_page.setIcon(GUIUtilities.get_icon("left.png"))
        self.btn_next_page.setIcon(GUIUtilities.get_icon("right.png"))
        self.btn_last_page.setIcon(GUIUtilities.get_icon("last.png"))
        self.btn_first_page.setStyleSheet('QPushButton{border: 0px solid;}')
        self.btn_prev_page.setStyleSheet('QPushButton{border: 0px solid;}')
        self.btn_last_page.setStyleSheet('QPushButton{border: 0px solid;}')
        self.btn_next_page.setStyleSheet('QPushButton{border: 0px solid;}')
        self.grid_actions_layout.setAlignment(QtCore.Qt.AlignCenter)

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self,value):
        self._tag=value

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self,value):
        self._items=value

    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self,value):
        self._page_size=value
        self.update_pager()

    @property
    def current_page(self):
        return self._curr_page+1

    @current_page.setter
    def current_page(self,val):
        self._curr_page=val
        self._curr_page=self._curr_page%self.total_pages
        self.lbl_current_page.setText(str(self.current_page))
        self.bind()

    @property
    def total_pages(self):
        return len(self._pages)

    def update_pager(self):
        self._pages=list(MiscUtilities.chunk(self._items,self._page_size))
        self.lbl_total_pages.setText("{}".format(len(self._pages)))
        self.lbl_current_page.setText(str(self.current_page))

    def btn_next_page_on_click(self):
        if len(self._pages) == 0:
            return
        self._curr_page+=1
        self.current_page=self._curr_page

    def btn_last_page_on_click(self):
        if len(self._pages) == 0:
            return
        self.current_page=len(self._pages)-1

    def btn_first_page_on_click(self):
        if len(self._pages) == 0:
            return
        self.current_page=0

    def btn_prev_page_on_click(self):
        if len(self._pages) == 0:
            return
        self._curr_page-=1
        self.current_page=self._curr_page

    def dragEnterEvent(self,event: QtGui.QDragEnterEvent) -> None:
        data=event.mimeData()
        if data.hasUrls():
            if any(url.isLocalFile() for url in data.urls()):
                event.accept()
                return
        else:
            event.ignore()

    def dragMoveEvent(self,event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            return
        else:
            event.ignore()

    def dropEvent(self,event: QtGui.QDropEvent) -> None:
        valid_files=[]
        files=[u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            if os.path.isfile(f):
                mime_type,encoding=mimetypes.guess_type(f)  # magic.from_file(f,mime=True)
                if mime_type.find("video") != -1 and self.content_type == "Videos":
                    valid_files.append(f)
                elif mime_type.find("image") != -1 and self.content_type == "Images":
                    valid_files.append(f)
        valid_files=sorted(valid_files,key=lambda v: os.path.basename(v))
        self.filesDropped.emit(valid_files)

    def load_images(self):

        def do_work():
            page=self._curr_page
            items=self._pages[page]

            def create_thumbnail(item):
                file_path=item.file_path
                if os.path.isfile(file_path):
                    image=cv2.imread(file_path)
                    h,w,_=np.shape(image)
                    if w > h:
                        thumbnail_array=imutils.resize(image,width=150)
                    else:
                        thumbnail_array=imutils.resize(image,height=150)
                    thumbnail_array=cv2.cvtColor(thumbnail_array,cv2.COLOR_BGR2RGB)
                    thumbnail=GUIUtilities.array_to_qimage(thumbnail_array)
                    thumbnail=QPixmap.fromImage(thumbnail)
                    del thumbnail_array
                    del image
                    return item,h,w,thumbnail,os.path.getsize(file_path), False
                thumbnail = GUIUtilities.get_image("placeholder.png")
                thumbnail = thumbnail.scaledToHeight(100)
                h, w = thumbnail.height(), thumbnail.width()
                return item, h, w, thumbnail, 0, True
            delayed_tasks=[dask.delayed(create_thumbnail)(item) for item in items]
            images=dask.compute(*delayed_tasks)
            return images

        def done_work(images):
            for img in images:
                if img:
                    item,h,w,thumbnail,file_size, is_broken=img
                    image_card=ImageCard()
                    image_card.is_broken = is_broken
                    image_card.tag=item
                    image_card.source=thumbnail
                    image_card.file_path=item.file_path
                    image_size_str = size(file_size,system=alternative) if file_size > 0 else "0 MB"
                    image_card.label.setText("\n ({0}px / {1}px) \n {2}".format(w,h, image_size_str))
                    image_card.setFixedHeight(240)
                    image_card.doubleClicked.connect(self.gallery_card_double_click)
                    image_card.add_buttons(self.actions)
                    if self.actions:
                        image_card.actionClicked.connect(lambda name,item: self.cardActionClicked.emit(name,item))
                    self.center_layout.add_item(image_card)

        def finished_work():
            self._loading_dialog.close()
            self.enable_paginator(True)

        worker=Worker(do_work)
        worker.signals.result.connect(done_work)
        worker.signals.finished.connect(finished_work)
        self._thread_pool.start(worker)
        self.enable_paginator(False)
        self._loading_dialog.show()

    def bind(self):
        self.update_pager()
        if len(self._pages) > 0:
            self.center_widget=QWidget()
            self.center_layout=GalleryLayout()
            self.center_widget.setLayout(self.center_layout)
            self.center_layout.setAlignment(QtCore.Qt.AlignTop)
            self.scrollArea.setWidget(self.center_widget)
            self.center_layout.initialize(n_items=self.page_size)
            if self.content_type == "Images":
                self.load_images()
            else:
                raise NotImplementedError
        else:
            self.center_widget=QWidget()
            self.center_layout=QVBoxLayout()
            self.center_widget.setLayout(self.center_layout)
            self.center_layout.setAlignment(QtCore.Qt.AlignCenter)
            self.center_layout.addWidget(QLabel("Drag and Drop your files"))
            self.scrollArea.setWidget(self.center_widget)

    def gallery_card_double_click(self,card: GalleryCard):
        self.doubleClicked.emit(card,self)

    def btn_check_all_on_click_slot(self):
        if self.items is None:
            return
        layout=self.scrollArea.widget().layout()
        for i in reversed(range(layout.count())):
            child=layout.itemAt(i)
            widget=child.widget()
            if isinstance(child.widget(),GalleryCard):
                widget.is_selected=True

    def btn_uncheck_all_on_click_slot(self):
        if self.items is None:
            return
        layout=self.scrollArea.widget().layout()
        for i in reversed(range(layout.count())):
            child=layout.itemAt(i)
            widget=child.widget()
            if isinstance(child.widget(),GalleryCard):
                widget.is_selected=False
