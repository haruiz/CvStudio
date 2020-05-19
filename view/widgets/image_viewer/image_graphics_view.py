import math
from queue import Queue

import cv2
from PIL import Image
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QObject, QPoint, pyqtSignal, QPointF, QRect, QRectF, QSize
from PyQt5.QtGui import QPainter, QPen, QWheelEvent, QKeyEvent, QColor, QPalette, QPainterPath
from PyQt5.QtWidgets import QGraphicsView, QGraphicsLineItem, QRubberBand, QApplication, QGraphicsSceneHoverEvent, \
    QGraphicsPathItem

from decor import gui_exception
from util import ImageUtilities
from view.widgets.image_viewer.image_pixmap_item import ImagePixmap
from view.widgets.image_viewer.image_viewer_scene import ImageViewerScene
from view.widgets.image_viewer.items import EditableBox, EditablePolygon, EditableEllipse, EditableItem, \
    EditablePolygonPoint
from view.widgets.image_viewer.selection_mode import SELECTION_TOOL


class ImageViewer(QGraphicsView, QObject):
    points_selection_sgn = pyqtSignal(list)
    key_press_sgn = pyqtSignal(QtGui.QKeyEvent)

    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self._scene = ImageViewerScene(self)
        self.setScene(self._scene)
        self._image = None
        self._image_original = None
        self._pixmap = None
        self._img_contrast = 1.0
        self._img_brightness = 50.0
        self._img_gamma = 1.0
        self._create_grid()
        self._channels = []
        self._current_tool = SELECTION_TOOL.POINTER
        self._dataset = None

        # create grid lines
        pen_color = QColor(255, 255, 255, 255)
        pen = QPen(pen_color)
        pen.setWidth(2)
        pen.setStyle(QtCore.Qt.DotLine)
        self.vline = QGraphicsLineItem()
        self.vline.setVisible(False)
        self.vline.setPen(pen)
        self.hline = QGraphicsLineItem()
        self.hline.setVisible(False)
        self.hline.setPen(pen)
        self._scene.addItem(self.vline)
        self._scene.addItem(self.hline)
        self._current_label = None

        # rectangle selection tool
        self._rectangle_tool_origin = QPoint()
        self._rectangle_tool_picker = QRubberBand(QRubberBand.Rectangle, self)

        # polygon selection tool
        app = QApplication.instance()
        color = app.palette().color(QPalette.Highlight)
        self._polygon_guide_line_pen = QPen(color)
        self._polygon_guide_line_pen.setWidth(3)
        self._polygon_guide_line_pen.setStyle(QtCore.Qt.DotLine)
        self._polygon_guide_line = QGraphicsLineItem()
        self._polygon_guide_line.setVisible(False)
        self._polygon_guide_line.setPen(self._polygon_guide_line_pen)
        self._scene.addItem(self._polygon_guide_line)
        self._current_polygon = None

        # circle
        self._current_ellipse = None

        # free selection tool
        self._current_free_path = None
        self._is_drawing = False
        self._last_point_drawn = QPoint()
        self._last_click_point = None
        self._free_Path_pen = QPen(color)
        self._free_Path_pen.setWidth(10)

        self._extreme_points = Queue(maxsize=4)

    @property
    def current_label(self):
        return self._current_label

    @current_label.setter
    def current_label(self, value):
        self._current_label = value
        if self._current_label:
            color = QColor(self._current_label.color)
            self._free_Path_pen.setColor(color)
            self._polygon_guide_line_pen.setColor(color)
            self._polygon_guide_line.setPen(self._polygon_guide_line_pen)

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, value):
        self._dataset = value

    @property
    def img_contrast(self):
        return self._img_contrast

    @img_contrast.setter
    def img_contrast(self, value):
        self._img_contrast = value

    @property
    def img_gamma(self):
        return self._img_gamma

    @img_gamma.setter
    def img_gamma(self, value):
        self._img_gamma = value

    @property
    def img_brightness(self):
        return self._img_brightness

    @img_brightness.setter
    def img_brightness(self, value):
        self._img_brightness = value

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value
        self._image_original = value.copy()
        self.update_viewer()

    @property
    def pixmap(self) -> ImagePixmap:
        return self._pixmap

    @gui_exception
    def update_viewer(self, fit_image=True):
        rgb = cv2.cvtColor(self._image, cv2.COLOR_BGR2RGB)
        rgb = ImageUtilities.adjust_image(rgb, self._img_contrast, self._img_brightness)
        rgb = ImageUtilities.adjust_gamma(rgb, self._img_gamma)
        pil_image = Image.fromarray(rgb)
        qppixmap_image = pil_image.toqpixmap()
        x, y = -qppixmap_image.width() / 2, -qppixmap_image.height() / 2

        if self._pixmap:
            self._pixmap.resetTransform()
            self._pixmap.setPixmap(qppixmap_image)
            self._pixmap.setOffset(x, y)
        else:
            self._pixmap = ImagePixmap()
            self._pixmap.setPixmap(qppixmap_image)
            self._pixmap.setOffset(x, y)
            self._scene.addItem(self._pixmap)
            self._pixmap.signals.hoverEnterEventSgn.connect(self.pixmap_hoverEnterEvent_slot)
            self._pixmap.signals.hoverLeaveEventSgn.connect(self.pixmap_hoverLeaveEvent_slot)
            self._pixmap.signals.hoverMoveEventSgn.connect(self.pixmap_hoverMoveEvent_slot)
        self._hide_guide_lines()
        if fit_image:
            self.fit_to_window()

    @gui_exception
    def reset_viewer(self):
        self._img_contrast = 1.0
        self._img_brightness = 50.0
        self._img_gamma = 1.0
        self._image = self._image_original.copy()

    @gui_exception
    def equalize_histogram(self):
        self._image = ImageUtilities.histogram_equalization(self._image)

    @gui_exception
    def correct_lightness(self):
        self._image = ImageUtilities.correct_lightness(self._image)

    def clusterize(self, k):
        self._image = ImageUtilities.kmeans(self._image.copy(), k)

    @property
    def current_tool(self):
        return self._current_tool

    @current_tool.setter
    def current_tool(self, value):
        self._polygon_guide_line.hide()
        self._current_polygon = None
        self._current_free_path = None
        self._current_ellipse = None
        self._is_drawing = value == SELECTION_TOOL.FREE
        self._current_tool = value
        self.clear_extreme_points()
        if value == SELECTION_TOOL.POINTER:
            self.enable_items(True)
        else:
            self.enable_items(False)

    def fit_to_window(self):
        if not self._pixmap or not self._pixmap.pixmap():
            return
        self.resetTransform()
        self.setTransform(QtGui.QTransform())
        self.fitInView(self._pixmap, QtCore.Qt.KeepAspectRatio)

    def _create_grid(self, gridSize=15):
        app: QApplication = QApplication.instance()
        curr_theme = "dark"
        if app:
            curr_theme = app.property("theme")
        if curr_theme == "light":
            color1 = QtGui.QColor("white")
            color2 = QtGui.QColor(237, 237, 237)
        else:
            color1 = QtGui.QColor(20, 20, 20)
            color2 = QtGui.QColor(0, 0, 0)
        backgroundPixmap = QtGui.QPixmap(gridSize * 2, gridSize * 2)
        backgroundPixmap.fill(color1)
        painter = QtGui.QPainter(backgroundPixmap)
        painter.fillRect(0, 0, gridSize, gridSize, color2)
        painter.fillRect(gridSize, gridSize, gridSize, gridSize, color2)
        painter.end()
        self._scene.setBackgroundBrush(QtGui.QBrush(backgroundPixmap))

    def wheelEvent(self, event: QWheelEvent):
        adj = (event.angleDelta().y() / 120) * 0.1
        self.scale(1 + adj, 1 + adj)

    @gui_exception
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == QtCore.Qt.Key_Space:
            image_rect: QRectF = self._pixmap.sceneBoundingRect()
            if self.current_tool == SELECTION_TOOL.POLYGON and self._current_polygon:
                points = self._current_polygon.points
                self._polygon_guide_line.hide()
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                if len(points) <= 2:
                    self._current_polygon.delete_item()
                self.current_tool = SELECTION_TOOL.POINTER
            elif self.current_tool == SELECTION_TOOL.EXTREME_POINTS and \
                    self._extreme_points.full():
                points = []
                image_offset = QPointF(image_rect.width() / 2, image_rect.height() / 2)
                for pt in self._extreme_points.queue:
                    pt: EditablePolygonPoint
                    center = pt.sceneBoundingRect().center()
                    x = math.floor(center.x() + image_offset.x())
                    y = math.floor(center.y() + image_offset.y())
                    points.append([x, y])
                self.points_selection_sgn.emit(points)
                self.current_tool = SELECTION_TOOL.POINTER
        else:
            event.ignore()

    # guide lines events
    def _show_guide_lines(self):
        if self.hline and self.vline:
            self.hline.show()
            self.vline.show()

    def _hide_guide_lines(self):
        if self.hline and self.vline:
            self.hline.hide()
            self.vline.hide()

    def _update_guide_lines(self, x, y):
        bbox: QRect = self._pixmap.boundingRect()
        offset = QPointF(bbox.width() / 2, bbox.height() / 2)
        self.vline.setLine(x, -offset.y(), x, bbox.height() - offset.y())
        self.vline.setZValue(1)
        self.hline.setLine(-offset.x(), y, bbox.width() - offset.x(), y)
        self.hline.setZValue(1)

    def pixmap_hoverMoveEvent_slot(self, evt: QGraphicsSceneHoverEvent, x, y):
        self._update_guide_lines(x, y)

    def pixmap_hoverEnterEvent_slot(self):
        self._show_guide_lines()

    def pixmap_hoverLeaveEvent_slot(self):
        self._hide_guide_lines()

    def delete_polygon_slot(self, polygon: EditablePolygon):
        self._current_polygon = None
        self.current_tool = SELECTION_TOOL.POINTER
        self._polygon_guide_line.hide()

    @gui_exception
    def mousePressEvent(self, evt: QtGui.QMouseEvent) -> None:
        image_rect: QRectF = self._pixmap.boundingRect()
        mouse_pos = self.mapToScene(evt.pos())
        if evt.buttons() == QtCore.Qt.LeftButton:
            if self.current_tool == SELECTION_TOOL.BOX:
                # create rectangle
                self.setDragMode(QGraphicsView.NoDrag)
                self._rectangle_tool_origin = evt.pos()
                geometry = QRect(self._rectangle_tool_origin, QSize())
                self._rectangle_tool_picker.setGeometry(geometry)
                self._rectangle_tool_picker.show()
            elif self.current_tool == SELECTION_TOOL.POLYGON:
                if image_rect.contains(mouse_pos):
                    if self._current_polygon is None:
                        self._current_polygon = EditablePolygon()
                        self._current_polygon.label = self._current_label
                        self._current_polygon.tag = self._dataset
                        self._current_polygon.signals.deleted.connect(self.delete_polygon_slot)
                        self._scene.addItem(self._current_polygon)
                        self._current_polygon.addPoint(mouse_pos)
                    else:
                        self._current_polygon.addPoint(mouse_pos)
            elif self.current_tool == SELECTION_TOOL.ELLIPSE:
                if image_rect.contains(mouse_pos):
                    self.setDragMode(QGraphicsView.NoDrag)
                    ellipse_rec = QtCore.QRectF(mouse_pos.x(), mouse_pos.y(), 0, 0)
                    self._current_ellipse = EditableEllipse()
                    self._current_ellipse.tag = self.dataset
                    self._current_ellipse.label = self._current_label
                    self._current_ellipse.setRect(ellipse_rec)
                    self._scene.addItem(self._current_ellipse)

            elif self.current_tool == SELECTION_TOOL.FREE:
                # consider only the points into the image
                if image_rect.contains(mouse_pos):
                    self.setDragMode(QGraphicsView.NoDrag)
                    self._last_point_drawn = mouse_pos
                    self._current_free_path = QGraphicsPathItem()
                    self._current_free_path.setOpacity(0.6)
                    self._current_free_path.setPen(self._free_Path_pen)
                    painter = QPainterPath()
                    painter.moveTo(self._last_point_drawn)
                    self._current_free_path.setPath(painter)
                    self._scene.addItem(self._current_free_path)

            elif self.current_tool == SELECTION_TOOL.EXTREME_POINTS:
                if image_rect.contains(mouse_pos):
                    if not self._extreme_points.full():
                        def delete_point(idx):
                            del self._extreme_points.queue[idx]

                        idx = self._extreme_points.qsize()
                        editable_pt = EditablePolygonPoint(idx)
                        editable_pt.signals.deleted.connect(delete_point)
                        editable_pt.setPos(mouse_pos)
                        self._scene.addItem(editable_pt)
                        self._extreme_points.put(editable_pt)

        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super(ImageViewer, self).mousePressEvent(evt)

    @gui_exception
    def mouseMoveEvent(self, evt: QtGui.QMouseEvent) -> None:
        mouse_pos = self.mapToScene(evt.pos())
        image_rect: QRectF = self._pixmap.boundingRect()
        if self.current_tool == SELECTION_TOOL.BOX:
            if not self._rectangle_tool_origin.isNull():
                geometry = QRect(self._rectangle_tool_origin, evt.pos()).normalized()
                self._rectangle_tool_picker.setGeometry(geometry)
        elif self.current_tool == SELECTION_TOOL.POLYGON:
            if self._current_polygon and image_rect.contains(mouse_pos):
                if self._current_polygon.count > 0:
                    last_point: QPointF = self._current_polygon.last_point
                    self._polygon_guide_line.setZValue(1)
                    self._polygon_guide_line.show()
                    mouse_pos = self.mapToScene(evt.pos())
                    self._polygon_guide_line.setLine(last_point.x(), last_point.y(), mouse_pos.x(), mouse_pos.y())
            else:
                self._polygon_guide_line.hide()
        elif self.current_tool == SELECTION_TOOL.ELLIPSE:
            if self._current_ellipse and image_rect.contains(mouse_pos):
                ellipse_rect = self._current_ellipse.rect()
                ellipse_pos = QPointF(ellipse_rect.x(), ellipse_rect.y())
                distance = math.hypot(mouse_pos.x() - ellipse_pos.x(), mouse_pos.y() - ellipse_pos.y())
                ellipse_rect.setWidth(distance)
                ellipse_rect.setHeight(distance)
                self._current_ellipse.setRect(ellipse_rect)
        elif self.current_tool == SELECTION_TOOL.FREE and evt.buttons() and QtCore.Qt.LeftButton:
            if self._current_free_path and image_rect.contains(mouse_pos):
                painter: QPainterPath = self._current_free_path.path()
                self._last_point_drawn = self.mapToScene(evt.pos())
                painter.lineTo(self._last_point_drawn)
                self._current_free_path.setPath(painter)
        super(ImageViewer, self).mouseMoveEvent(evt)

    @gui_exception
    def mouseReleaseEvent(self, evt: QtGui.QMouseEvent) -> None:
        image_rect: QRectF = self._pixmap.boundingRect()
        if self.current_tool == SELECTION_TOOL.BOX:
            roi: QRect = self._rectangle_tool_picker.geometry()
            roi: QRectF = self.mapToScene(roi).boundingRect()
            self._rectangle_tool_picker.hide()
            if image_rect == roi.united(image_rect):
                rect = EditableBox(roi)
                rect.label = self.current_label
                rect.tag = self._dataset
                self._scene.addItem(rect)
                self.current_tool = SELECTION_TOOL.POINTER
                self.setDragMode(QGraphicsView.ScrollHandDrag)

        elif self.current_tool == SELECTION_TOOL.ELLIPSE and self._current_ellipse:
            roi: QRect = self._current_ellipse.boundingRect()
            if image_rect == roi.united(image_rect):
                self.current_tool = SELECTION_TOOL.POINTER
                self.setDragMode(QGraphicsView.ScrollHandDrag)
            else:
                self._current_ellipse.delete_item()
        elif self.current_tool == SELECTION_TOOL.FREE and self._current_free_path:
            # create polygon
            self._current_free_path: QGraphicsPathItem
            path_rect = self._current_free_path.boundingRect()
            if image_rect == path_rect.united(image_rect):
                path = self._current_free_path.path()
                path_polygon = EditablePolygon()
                path_polygon.tag = self.dataset
                path_polygon.label = self.current_label
                self._scene.addItem(path_polygon)
                for i in range(0, path.elementCount(), 10):
                    x, y = path.elementAt(i).x, path.elementAt(i).y
                    path_polygon.addPoint(QPointF(x, y))
            self._scene.removeItem(self._current_free_path)
            self.current_tool = SELECTION_TOOL.POINTER
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super(ImageViewer, self).mouseReleaseEvent(evt)

    def remove_annotations(self):
        for item in self._scene.items():
            if isinstance(item, EditableItem):
                item.delete_item()

    def remove_annotations_by_label(self, label_name):
        for item in self._scene.items():
            if isinstance(item, EditableItem):
                if item.label and item.label.name == label_name:
                    item.delete_item()

    def enable_items(self, value):
        for item in self._scene.items():
            if isinstance(item, EditableItem):
                item.setEnabled(value)

    def clear_extreme_points(self):
        if self._extreme_points.qsize() > 0:
            for pt in self._extreme_points.queue:
                self._scene.removeItem(pt)
            self._extreme_points.queue.clear()
