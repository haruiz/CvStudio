from PyQt5 import QtGui,QtCore
from PyQt5.QtCore import QObject,QPoint,QRect,QPointF,QSize,QRectF
from PyQt5.QtGui import QPainter,QPen,QPixmap,QColor,QWheelEvent,QPainterPath
from PyQt5.QtWidgets import QGraphicsView,QGraphicsLineItem,QRubberBand,QGraphicsSceneHoverEvent,QGraphicsPathItem

from view.widgets.image_viewer.box_item import EditableBox
from view.widgets.image_viewer.image_pixmap_item import ImagePixmap
from view.widgets.image_viewer.image_viewer_scene import ImageViewerScene
from view.widgets.image_viewer.polygon_item import EditablePolygon
from view.widgets.image_viewer.selection_mode import SELECTION_MODE


class ImageViewer(QGraphicsView,QObject):

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
    def current_label(self):
        return self._current_label

    @current_label.setter
    def current_label(self, value):
        self._current_label = value

    @property
    def pixmap(self)-> ImagePixmap:
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
        #self._pixmap.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self._pixmap.signals.hoverEnterEventSgn.connect(self.pixmap_hoverEnterEvent_slot)
        self._pixmap.signals.hoverLeaveEventSgn.connect(self.pixmap_hoverLeaveEvent_slot)
        self._pixmap.signals.hoverMoveEventSgn.connect(self.pixmap_hoverMoveEvent_slot)
        self._scene.addItem(self._pixmap)
        # rect=self._scene.addRect(QtCore.QRectF(0,0,100,100), QtGui.QPen(QtGui.QColor("red")))
        # rect.setZValue(1.0)
        #self.fit_to_window()

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

    def remove_annotations(self):
        for item in self._scene.items():
            if isinstance(item, EditableBox):
                self._scene.removeItem(item)
            elif isinstance(item, EditablePolygon):
                item.delete_polygon()

    def remove_annotations_by_label(self, label_name):
        for item in self._scene.items():
            if isinstance(item, EditableBox):
                if item.label and item.label.name == label_name:
                    self._scene.removeItem(item)
            elif isinstance(item, EditablePolygon):
                if item.label and item.label.name == label_name:
                    item.delete_polygon()

    def enable_items(self, value):
        for item in self._scene.items():
            if isinstance(item,EditablePolygon) or isinstance(item,EditableBox):
                item.setEnabled(value)

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
                    rect.label=self.current_label
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
                    path_polygon.label = self.current_label
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
            self._current_polygon.label=self.current_label
            self._current_polygon=None
            self.selection_mode = SELECTION_MODE.NONE
            self._polygon_guide_line.hide()
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super(ImageViewer, self).keyPressEvent(event)

    def delete_polygon_slot(self,polygon: EditablePolygon):
        self._current_polygon=None
        self.selection_mode=SELECTION_MODE.NONE
        self._polygon_guide_line.hide()