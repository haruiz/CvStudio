import math
from enum import Enum,auto

import cv2
import imutils
import numpy as np
from PIL import Image
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtCore import QObject,pyqtSignal,QSize,QThreadPool,QPointF,QPoint,QRect,QRectF,QItemSelection,QModelIndex
from PyQt5.QtGui import QWheelEvent,QBrush,QColor,QPixmap,QPen,QPainterPath,QIcon,QStandardItemModel,QStandardItem, \
    QPainter,QPalette
from PyQt5.QtWidgets import QWidget,QGraphicsView,QGraphicsLineItem, \
    QRubberBand,QGraphicsItem,QGraphicsPathItem,QTreeWidgetItem,QTreeWidget,QAbstractItemView,QDialog,QAction, \
    QGraphicsSceneHoverEvent,QGraphicsSceneMouseEvent,QTreeView,QLabel

from core import HubFactory,HubProvider
from dao import DatasetDao
from dao.hub_dao import HubDao
from dao.label_dao import LabelDao
from decor import gui_exception,work_exception
from util import GUIUtilities,Worker
from view.forms import NewRepoForm
from view.forms.label_form import NewLabelForm
from view.widgets.labels_treeview import LabelsTreeView
from view.widgets.loading_dialog import QLoadingDialog
from view.widgets.models_treeview import ModelsTreeview
from vo import HubVO,LabelVo
from .base_image_viewer import Ui_Image_Viewer_Widget
from .box import EditableBox
from .image_pixmap import ImagePixmap
from .image_viewer_scene import ImageViewerScene
from .polygon import EditablePolygon
from ..image_button import ImageButton


class SELECTION_MODE(Enum):
    POLYGON=auto()
    BOX=auto()
    FREE=auto()
    NONE=auto()


class ImageViewer(QGraphicsView,QObject):
    polygonAdded=pyqtSignal(list)
    boxAdded=pyqtSignal(int,int,int,int)

    def __init__(self,parent=None):
        super(ImageViewer,self).__init__(parent)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        #self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        #self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        #self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self._scene=ImageViewerScene(self)
        self.setScene(self._scene)
        self._create_grid()
        self._create_grid_lines()
        self._pixmap=None
        self._selection_mode=SELECTION_MODE.NONE

        # polygon selection
        _polygon_guide_line_pen=QPen(QtGui.QColor(235,72,40))
        _polygon_guide_line_pen.setWidth(2)
        _polygon_guide_line_pen.setStyle(QtCore.Qt.DotLine)
        self._polygon_guide_line=QGraphicsLineItem()
        self._polygon_guide_line.setVisible(False)
        self._polygon_guide_line.setPen(_polygon_guide_line_pen)
        self._scene.addItem(self._polygon_guide_line)
        self._current_polygon=None

        # rectangle selection
        self._box_origin=QPoint()
        self._box_picker=QRubberBand(QRubberBand.Rectangle,self)

        # free selection
        self._current_free_path=None
        self._is_drawing=False
        self._last_point_drawn=QPoint()
        self._current_label = None


    @property
    def current_label(self)-> LabelVo:
        return self._current_label

    @current_label.setter
    def current_label(self, value):
        pal = QPalette()
        pal.setBrush(QPalette.Highlight,QBrush(QColor(value.color)))
        self._box_picker.setPalette(pal);
        self._current_label = value

    def remove_annotations(self):
        for item in self._scene.items():
            if isinstance(item, EditableBox):
                self._scene.removeItem(item)
            elif isinstance(item, EditablePolygon):
                item.delete_polygon()

    def enable_items(self, value):
        for item in self._scene.items():
            if isinstance(item,EditablePolygon) or isinstance(item,EditableBox):
                item.setEnabled(value)


    @property
    def pixmap(self):
        return self._pixmap

    @pixmap.setter
    def pixmap(self, value: QPixmap):
        self.selection_mode = SELECTION_MODE.NONE
        self.resetTransform()
        if self.pixmap:
            self._scene.removeItem(self._pixmap)
        self.remove_annotations()
        self._pixmap = ImagePixmap()
        self._pixmap.setPixmap(value)
        self._pixmap.setOffset(-value.width()/2, -value.height()/2)
        self._pixmap.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self._pixmap.signals.hoverEnterEventSgn.connect(self.pixmap_hoverEnterEvent_slot)
        self._pixmap.signals.hoverLeaveEventSgn.connect(self.pixmap_hoverLeaveEvent_slot)
        self._pixmap.signals.hoverMoveEventSgn.connect(self.pixmap_hoverMoveEvent_slot)
        self._scene.addItem(self._pixmap)
        # rect=self._scene.addRect(QtCore.QRectF(0,0,100,100), QtGui.QPen(QtGui.QColor("red")))
        # rect.setZValue(1.0)
        self.fit_to_window()
    

    @property
    def selection_mode(self):
        return self._selection_mode

    @selection_mode.setter
    def selection_mode(self,value):
        self._polygon_guide_line.hide()
        self._current_polygon=None
        self._current_free_path=None
        self._is_drawing=value == SELECTION_MODE.FREE
        if value == SELECTION_MODE.NONE:
            self.enable_items(True)
        else:
            self.enable_items(False)
        self._selection_mode=value


    def _create_grid(self):
        gridSize=15
        backgroundPixmap=QtGui.QPixmap(gridSize*2,gridSize*2)
        #backgroundPixmap.fill(QtGui.QColor("white"))
        backgroundPixmap.fill(QtGui.QColor(20,20,20))
        #backgroundPixmap.fill(QtGui.QColor("powderblue"))
        painter=QtGui.QPainter(backgroundPixmap)
        #backgroundColor=QtGui.QColor("palegoldenrod")
        #backgroundColor=QtGui.QColor(237,237,237)
        backgroundColor=QtGui.QColor(0,0,0)
        painter.fillRect(0,0,gridSize,gridSize,backgroundColor)
        painter.fillRect(gridSize,gridSize,gridSize,gridSize,backgroundColor)
        painter.end()
        self._scene.setBackgroundBrush(QtGui.QBrush(backgroundPixmap))

    def _create_grid_lines(self):
        pen_color=QColor(255,255,255,255)
        pen=QPen(pen_color)
        pen.setWidth(2)
        pen.setStyle(QtCore.Qt.DotLine)
        self.vline=QGraphicsLineItem()
        self.vline.setVisible(False)
        self.vline.setPen(pen)
        self.hline=QGraphicsLineItem()
        self.hline.setVisible(False)
        self.hline.setPen(pen)
        self._scene.addItem(self.vline)
        self._scene.addItem(self.hline)

    def wheelEvent(self,event: QWheelEvent):
        adj=(event.angleDelta().y()/120)*0.1
        self.scale(1+adj,1+adj)

    def fit_to_window(self):
        """Fit image within view."""
        if not self.pixmap or  not self._pixmap.pixmap():
            return
        #self._pixmap.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self.fitInView(self._pixmap,QtCore.Qt.KeepAspectRatio)

    def show_guide_lines(self):
        if self.hline and self.vline:
            self.hline.show()
            self.vline.show()

    def hide_guide_lines(self):
        if self.hline and self.vline:
            self.hline.hide()
            self.vline.hide()

    def pixmap_hoverEnterEvent_slot(self):
        self.show_guide_lines()


    def pixmap_hoverLeaveEvent_slot(self):
        self.hide_guide_lines()


    def pixmap_hoverMoveEvent_slot(self,evt: QGraphicsSceneHoverEvent, x,y):
        bbox: QRect  =self._pixmap.boundingRect()
        offset = QPointF(bbox.width() / 2, bbox.height() / 2)
        self.vline.setLine(x,-offset.y(),x,bbox.height()- offset.y())
        self.vline.setZValue(1)
        self.hline.setLine(-offset.x(),y,bbox.width()-offset.x(),y)
        self.hline.setZValue(1)


    def mouseMoveEvent(self, evt: QtGui.QMouseEvent) -> None:
        if self.selection_mode == SELECTION_MODE.BOX:
            if not self._box_origin.isNull():
                self._box_picker.setGeometry(QRect(self._box_origin,evt.pos()).normalized())
        elif self.selection_mode == SELECTION_MODE.POLYGON:
            if self._current_polygon:
                if self._current_polygon.count > 0:
                    last_point: QPointF=self._current_polygon.last_point
                    self._polygon_guide_line.setZValue(1)
                    self._polygon_guide_line.show()
                    mouse_pos=self.mapToScene(evt.pos())
                    self._polygon_guide_line.setLine(last_point.x(),last_point.y(),mouse_pos.x(),mouse_pos.y())
            else:
                self._polygon_guide_line.hide()

        elif self.selection_mode == SELECTION_MODE.FREE and evt.buttons() and QtCore.Qt.LeftButton:
            if self._current_free_path:
                painter: QPainterPath=self._current_free_path.path()
                self._last_point_drawn=self.mapToScene(evt.pos())
                painter.lineTo(self._last_point_drawn)
                self._current_free_path.setPath(painter)

        super(ImageViewer, self).mouseMoveEvent(evt)

    def mousePressEvent(self, evt: QtGui.QMouseEvent) -> None:


        if evt.buttons() == QtCore.Qt.LeftButton:
            if self.selection_mode == SELECTION_MODE.BOX:
                self.setDragMode(QGraphicsView.NoDrag)
                self._box_origin=evt.pos()
                self._box_picker.setGeometry(QRect(self._box_origin,QSize()))
                self._box_picker.show()

            elif self._selection_mode == SELECTION_MODE.POLYGON:
                pixmap_rect: QRectF=self._pixmap.boundingRect()
                new_point=self.mapToScene(evt.pos())
                # consider only the points intothe image
                if  pixmap_rect.contains(new_point):
                    if self._current_polygon is None:
                        self._current_polygon=EditablePolygon()
                        if self.current_label:
                            _polygon_guide_line_pen=QPen(QtGui.QColor(self.current_label.color))
                            _polygon_guide_line_pen.setWidth(2)
                            _polygon_guide_line_pen.setStyle(QtCore.Qt.DotLine)
                            self._polygon_guide_line.setPen(_polygon_guide_line_pen)
                            self._current_polygon.pen_color=QColor(self.current_label.color)
                            self._current_polygon.brush_color=QColor(self.current_label.color)
                        self._current_polygon.signals.deleted.connect(self.delete_polygon_slot)
                        self._scene.addItem(self._current_polygon)
                        self._current_polygon.addPoint(new_point)
                    else:
                        self._current_polygon.addPoint(new_point)

            elif self._selection_mode == SELECTION_MODE.FREE:
                # start drawing
                new_point=self.mapToScene(evt.pos())
                pixmap_rect: QRectF=self._pixmap.boundingRect()
                # consider only the points intothe image
                if  pixmap_rect.contains(new_point):
                    self.setDragMode(QGraphicsView.NoDrag)

                    pen=QPen(QtGui.QColor(235,72,40))
                    pen.setWidth(10)
                    self._last_point_drawn=new_point
                    self._current_free_path=QGraphicsPathItem()
                    self._current_free_path.setOpacity(0.6)
                    self._current_free_path.setPen(pen)
                    painter=QPainterPath()
                    painter.moveTo(self._last_point_drawn)
                    self._current_free_path.setPath(painter)
                    self._scene.addItem(self._current_free_path)
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)

        super(ImageViewer,self).mousePressEvent(evt)

    def mouseReleaseEvent(self, evt: QtGui.QMouseEvent) -> None:
        if evt.button() == QtCore.Qt.LeftButton:
            if self.selection_mode == SELECTION_MODE.BOX:
                roi: QRect=self._box_picker.geometry()
                roi: QRectF=self.mapToScene(roi).boundingRect()
                pixmap_rect = self._pixmap.boundingRect()
                self._box_picker.hide()
                if pixmap_rect == roi.united(pixmap_rect):
                    rect=EditableBox(roi)
                    if self.current_label:
                        rect.pen_color=QColor(self.current_label.color)
                        rect.brush_color = QColor(self.current_label.color)
                    self._scene.addItem(rect)
                    self.selection_mode=SELECTION_MODE.NONE
                    self.setDragMode(QGraphicsView.ScrollHandDrag)

            elif self.selection_mode == SELECTION_MODE.FREE and self._current_free_path:
                # create polygon
                self._current_free_path: QGraphicsPathItem
                path_rect = self._current_free_path.boundingRect()
                pixmap_rect=self._pixmap.boundingRect()
                if pixmap_rect == path_rect.united(pixmap_rect):
                    path=self._current_free_path.path()
                    path_polygon=EditablePolygon()
                    self._scene.addItem(path_polygon)
                    for i in range(0,path.elementCount(),10):
                        x,y=path.elementAt(i).x,path.elementAt(i).y
                        path_polygon.addPoint(QPointF(x,y))
                self._scene.removeItem(self._current_free_path)
                self.selection_mode=SELECTION_MODE.NONE
                self.setDragMode(QGraphicsView.ScrollHandDrag)


        super(ImageViewer, self).mouseReleaseEvent(evt)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if self._current_polygon and event.key() == QtCore.Qt.Key_Space:
            points=self._current_polygon.points
            self._current_polygon=None
            self.selection_mode = SELECTION_MODE.NONE
            self._polygon_guide_line.hide()
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super(ImageViewer, self).keyPressEvent(event)

    def delete_polygon_slot(self,polygon: EditablePolygon):
        self._current_polygon=None
        self.selection_mode=SELECTION_MODE.NONE
        self._polygon_guide_line.hide()


class ImageViewerWidget(QWidget,Ui_Image_Viewer_Widget):
    def __init__(self,parent=None):
        super(ImageViewerWidget,self).__init__(parent)
        self.setupUi(self)
        self.viewer=ImageViewer()
        self.center_layout.addWidget(self.viewer)
        self.actions_layout.setAlignment(QtCore.Qt.AlignCenter)
        self._ds_dao =  DatasetDao()
        self._hub_dao = HubDao()
        self._labels_dao = LabelDao()
        self._thread_pool=QThreadPool()
        self._loading_dialog=QLoadingDialog()
        self._image_path = None
        self._image_dataset = None
        self._image = None
        self.images_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection )
        self.images_list_widget.currentItemChanged.connect(self.image_list_sel_changed_slot)

        self.treeview_models=ModelsTreeview()
        self.treeview_models.setColumnWidth(0,300)
        self.tree_view_models_layout.addWidget(self.treeview_models)
        self.treeview_models.action_click.connect(self.trv_models_action_click_slot)

        self.treeview_labels = LabelsTreeView()
        self.treeview_labels.action_click.connect(self.trv_labels_action_click_slot)
        self.tree_view_labels_layout.addWidget(self.treeview_labels)
        self.treeview_labels.selectionModel().selectionChanged.connect(self.default_label_changed_slot)
        #self.treeview_labels.add_node("cat", "red")
        #self.treeview_labels.add_node("dog","yellow")
        #self.treeview_labels.add_node("person","blue")
        self.create_actions_bar()

    def default_label_changed_slot(self, selection: QItemSelection):
        index=self.treeview_labels.currentIndex()
        widget_item: QWidget=self.treeview_labels.indexWidget(index)
        print(widget_item)
        if widget_item:
            current_label: LabelVo=widget_item.property("tag")
            self.viewer.current_label=current_label


    def image_list_sel_changed_slot(self, curr: QStandardItem, prev: QStandardItem):
        if curr: self.image_path = curr.text()

    @property
    def image(self):
        return self._image

    @property
    def image_path(self):
        return self._image_path

    @image_path.setter
    def image_path(self,value):
        self._image_path = value
        self._image=Image.open(value)
        self.viewer.pixmap = QPixmap(value)

    @property
    def image_dataset(self):
        return self._image_dataset

    @image_dataset.setter
    def image_dataset(self,value):
        self._image_dataset = value

    @gui_exception
    def load_images(self):
        @work_exception
        def do_work():
            entries=self._ds_dao.fetch_entries(self._image_dataset)
            return entries,None

        @gui_exception
        def done_work(result):
            data,error=result
            for vo in data:
                self.images_list_widget.addItem(vo.file_path)

        worker=Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)


    @gui_exception
    def load_models(self):
        @work_exception
        def do_work():
            results =self._hub_dao.fetch_all()
            return results, None

        @gui_exception
        def done_work(result):
            result, error = result
            if error is None:
                for entry in result:
                    self.treeview_models.add_node(entry)
        worker=Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)


    @gui_exception
    def load_labels(self):
        @work_exception
        def do_work():
            results =self._labels_dao.fetch_all(self.image_dataset)
            return results, None

        @gui_exception
        def done_work(result):
            result, error = result
            if error is None:
                for entry in result:
                    self.treeview_labels.add_node(entry)
        worker=Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)

    @gui_exception
    def add_repository(self):

        @work_exception
        def do_work(repo):
            hub_client=HubFactory.create(HubProvider.PyTorch)
            hub=hub_client.fetch_model(repo,force_reload=True)
            self._hub_dao.save(hub)
            return hub,None

        @gui_exception
        def done_work(result):
            data,error=result
            if error is None:
                self.treeview_models.add_node(data)

        form=NewRepoForm()
        if form.exec_() == QDialog.Accepted:
            repository=form.result
            worker=Worker(do_work, repository)
            worker.signals.result.connect(done_work)
            self._thread_pool.start(worker)

    def bind(self):
        self.load_images()
        self.load_models()
        self.load_labels()

    def keyPressEvent(self,event: QtGui.QKeyEvent) -> None:
        row = self.images_list_widget.currentRow()
        if event.key() == QtCore.Qt.Key_A:
            self.images_list_widget.setCurrentRow(row-1)
        if event.key() == QtCore.Qt.Key_D:
            self.images_list_widget.setCurrentRow(row+1)
        if event.key() == QtCore.Qt.Key_W:
            self.viewer.selection_mode=SELECTION_MODE.POLYGON
        if event.key() == QtCore.Qt.Key_S:
            self.viewer.selection_mode=SELECTION_MODE.BOX
        super(ImageViewerWidget,self).keyPressEvent(event)

    @gui_exception
    def trv_models_action_click_slot(self, action:  QAction):
        if action.text() == self.treeview_models.CTX_MENU_NEW_DATASET_ACTION:
            self.add_repository()
        elif action.text() == self.treeview_models.CTX_MENU_AUTO_LABEL_ACTION:
            current_node = action.data()  # model name
            parent_node = current_node.parent  # repo
            repo, model = parent_node.get_data(0),current_node.get_data(0)
            self.autolabel(repo, model)

    @gui_exception
    def trv_labels_action_click_slot(self,action: QAction):
        model  = self.treeview_labels.model()
        if action.text() == self.treeview_labels.CTX_MENU_ADD_LABEL:
            form=NewLabelForm()
            if form.exec_() == QDialog.Accepted:
                vo: LabelVo=form.result
                vo.dataset=self.image_dataset
                self._labels_dao.save(vo)
                self.treeview_labels.add_node(vo)
        elif action.text() == self.treeview_labels.CTX_MENU_DELETE_LABEL:
            index : QModelIndex = action.data()
            if index:
                #text_item: QStandardItem = model.item(index.row(),0)
                widget_item: QWidget = self.treeview_labels.indexWidget(index)
                vo : LabelVo = widget_item.property("tag")
                self._labels_dao.delete(vo.id)
                self.treeview_labels.model().removeRow(index.row())

    def autolabel(self, repo, model_name):
        def do_work():
            try:
                from PIL import Image
                from torchvision import transforms
                import torch
                model=torch.hub.load(repo,model_name,pretrained=True)
                model.eval()
                input_image=Image.open(self.image_path)
                preprocess=transforms.Compose([
                    transforms.Resize(480),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485,0.456,0.406],std=[0.229,0.224,0.225]),
                ])
                input_tensor=preprocess(input_image)
                input_batch=input_tensor.unsqueeze(0)  # create a mini-batch as expected by the model
                # move the input and model to GPU for speed if available
                if torch.cuda.is_available():
                    input_batch=input_batch.to('cuda')
                    model.to('cuda')
                with torch.no_grad():
                    output=model(input_batch)['out'][0]
                output_predictions=output.argmax(0)
                # create a color pallette, selecting a color for each class
                palette=torch.tensor([2 ** 25-1,2 ** 15-1,2 ** 21-1])
                colors=torch.as_tensor([i for i in range(21)])[:,None]*palette
                colors=(colors%255).numpy().astype("uint8")
                # plot the semantic segmentation predictions of 21 classes in each color
                predictions_array: np.ndarray=output_predictions.byte().cpu().numpy()
                predictions_image=Image.fromarray(predictions_array).resize(input_image.size)
                predictions_image.putpalette(colors)
                labels_mask=np.asarray(predictions_image)
                classes=list(filter(lambda x: x != 0,np.unique(labels_mask).tolist()))
                classes_map={c: [] for c in classes}
                for c in classes:
                    class_mask=np.zeros(labels_mask.shape,dtype=np.uint8)
                    class_mask[np.where(labels_mask == c)]=255
                    contour_list=cv2.findContours(class_mask.copy(),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
                    contour_list=imutils.grab_contours(contour_list)
                    for contour in contour_list:
                        points=np.vstack(contour).squeeze().tolist()
                        classes_map[c].append(points)
                return classes_map,None
            except Exception as ex:
                return None,ex

        def done_work(result):
            classes_map,err=result
            if err:
                return
            self._loading_dialog.close()
            for class_idx,contours in classes_map.items():
                for c in contours:
                    points=[]
                    for i in range(0,len(c),10):
                        points.append(c[i])
                    polygon=EditablePolygon()
                    self.viewer._scene.addItem(polygon)
                    bbox: QRect=self.viewer.pixmap.boundingRect()
                    offset=QPointF(bbox.width()/2,bbox.height()/2)
                    for point in points:
                        polygon.addPoint(QPoint(point[0] - offset.x(),point[1] - offset.y()))


        worker=Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)
        self._loading_dialog.exec_()

    def create_actions_bar(self):
        self.btn_enable_polygon_selection=ImageButton(icon=GUIUtilities.get_icon("polygon.png"),size=QSize(38,38))
        self.btn_enable_rectangle_selection=ImageButton(icon=GUIUtilities.get_icon("square.png"),size=QSize(38,38))
        self.btn_enable_free_selection=ImageButton(icon=GUIUtilities.get_icon("highlighter.png"),size=QSize(38,38))
        self.btn_enable_none_selection=ImageButton(icon=GUIUtilities.get_icon("cursor.png"),size=QSize(38,38))
        self.actions_layout.addWidget(self.btn_enable_rectangle_selection)
        self.actions_layout.addWidget(self.btn_enable_polygon_selection)
        self.actions_layout.addWidget(self.btn_enable_free_selection)
        self.actions_layout.addWidget(self.btn_enable_none_selection)
        self.btn_enable_polygon_selection.clicked.connect(self.btn_enable_polygon_selection_clicked_slot)
        self.btn_enable_rectangle_selection.clicked.connect(self.btn_enable_rectangle_selection_clicked_slot)
        self.btn_enable_free_selection.clicked.connect(self.btn_enable_free_selection_clicked_slot)
        self.btn_enable_none_selection.clicked.connect(self.btn_enable_none_selection_clicked_slot)

    def btn_enable_polygon_selection_clicked_slot(self):
        self.viewer.selection_mode=SELECTION_MODE.POLYGON

    def btn_enable_rectangle_selection_clicked_slot(self):
        self.viewer.selection_mode=SELECTION_MODE.BOX

    def btn_enable_none_selection_clicked_slot(self):
        self.viewer.selection_mode=SELECTION_MODE.NONE

    def btn_enable_free_selection_clicked_slot(self):
        self.viewer.selection_mode=SELECTION_MODE.FREE



