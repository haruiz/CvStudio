from cvstudio.pyqt import (
    QGraphicsView,
    QPainter,
    QtCore,
    QApplication,
    QtGui,
    QWheelEvent,
    QGraphicsLineItem,
    QColor,
    QPen,
    QRectF,
    QLineF,
    QBrush,
    QPointF,
)
from PIL import Image

from .image_graphicsview_items import EditableItem
from .image_viewer_scene import ImageViewerScene
from .image_pixmap import ImagePixmap
from cvstudio.decor import gui_exception

# CANVAS_GRID_COLOR = QColor(20, 20, 20, 100)
from .selection_tool import SELECTION_TOOL

CANVAS_GRID_COLOR = QColor(144, 199, 253, 30)
# CANVAS_GRID_LINES_COLOR = QColor(20, 20, 20, 255)
CANVAS_GRID_LINES_COLOR = QColor(144, 199, 253, 100)
CANVAS_BACKGROUND_COLOR = QColor(0, 0, 0, 0)


def GetRangePct(MinValue, MaxValue, Value):
    """Calculates the percentage along a line from **MinValue** to **MaxValue** that value is.

    :param MinValue: Minimum Value
    :param MaxValue: Maximum Value
    :param Value: Input value
    :returns: The percentage (from 0.0 to 1.0) betwen the two values where input value is
    """
    return (Value - MinValue) / (MaxValue - MinValue)


def lerp(start, end, alpha):
    """Performs a linear interpolation

    >>> start + alpha * (end - start)

    :param start: start the value to interpolate from
    :param end: end the value to interpolate to
    :param alpha: alpha how far to interpolate
    :returns: The result of the linear interpolation
    """
    return start + alpha * (end - start)


class ImageGraphicsView(QGraphicsView):
    _mouseWheelZoomRate = 0.0005

    def __init__(self, *args, **kwargs):
        super(ImageGraphicsView, self).__init__(*args, **kwargs)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setRenderHints(
            QPainter.Antialiasing
            | QPainter.SmoothPixmapTransform
            | QPainter.TextAntialiasing
        )

        self.factor = 1
        self._minimum_scale = 0.2
        self._maximum_scale = 3.0
        self.grid_size_huge = 100.0
        self.grid_size_fine = 24.9766
        self.canvas_switch = 4
        self.canvas_grid_color = CANVAS_GRID_COLOR
        self.canvas_grid_color_darker = CANVAS_GRID_LINES_COLOR
        self.canvas_bg_color = CANVAS_BACKGROUND_COLOR

        self._scene = ImageViewerScene(self)
        self.setScene(self._scene)

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

        self._image = None
        self._pixmap = None
        self._img_contrast = 1.0
        self._img_brightness = 50.0
        self._img_gamma = 1.0
        self._current_tool = SELECTION_TOOL.POINTER

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value
        self.update_viewer()

    @property
    def current_tool(self):
        return self._current_tool

    @current_tool.setter
    def current_tool(self, value):
        self._current_tool = value

    def view_minimum_scale(self):
        return self._minimum_scale

    def view_maximum_scale(self):
        return self._maximum_scale

    def current_view_scale(self):
        return self.transform().m22()

    def get_lod_value_from_scale(self, num_lods=5, scale=1.0):
        lod = lerp(
            num_lods,
            1,
            GetRangePct(self.view_minimum_scale(), self.view_maximum_scale(), scale),
        )
        return int(round(lod))

    def get_lod_value_from_current_scale(self, numLods=5):
        return self.get_lod_value_from_scale(numLods, self.current_view_scale())

    def get_canvas_lod_value_from_current_scale(self):
        return self.get_lod_value_from_scale(4, self.current_view_scale())

    def zoom(self, scale_factor):
        self.factor = self.transform().m22()
        future_scale = self.factor * scale_factor
        if future_scale <= self._minimum_scale:
            scale_factor = self._minimum_scale / self.factor
        if future_scale >= self._maximum_scale:
            scale_factor = (self._maximum_scale - 0.1) / self.factor
        self.scale(scale_factor, scale_factor)

    def wheelEvent(self, event: QWheelEvent) -> None:
        (xfo, invRes) = self.transform().inverted()
        top_left = xfo.map(self.rect().topLeft())
        bottom_right = xfo.map(self.rect().bottomRight())
        # center = (top_left + bottom_right) * 0.5
        zoom_factor = 1.0 + event.angleDelta().y() * self._mouseWheelZoomRate
        self.zoom(zoom_factor)

    def reset_scale(self):
        self.resetTransform()

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        super(ImageGraphicsView, self).drawBackground(painter, rect)

        lod = self.get_canvas_lod_value_from_current_scale()
        painter.fillRect(rect, QBrush(self.canvas_bg_color))
        left = int(rect.left()) - (int(rect.left()) % self.grid_size_fine)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size_fine)

        if lod < self.canvas_switch:
            # Draw horizontal fine lines
            grid_lines = []
            y = float(top)
            while y < float(rect.bottom()):
                grid_lines.append(QLineF(rect.left(), y, rect.right(), y))
                y += self.grid_size_fine
            painter.setPen(QPen(self.canvas_grid_color, 1))
            painter.drawLines(grid_lines)

            # Draw vertical fine lines
            grid_lines = []
            x = float(left)
            while x < float(rect.right()):
                grid_lines.append(QLineF(x, rect.top(), x, rect.bottom()))
                x += self.grid_size_fine
            painter.setPen(QPen(self.canvas_grid_color, 1))
            painter.drawLines(grid_lines)

        # Draw thick grid
        left = int(rect.left()) - (int(rect.left()) % self.grid_size_huge)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size_huge)

        # Draw vertical thick lines
        grid_lines = []
        painter.setPen(QPen(self.canvas_grid_color_darker, 1.5))
        x = left
        while x < rect.right():
            grid_lines.append(QLineF(x, rect.top(), x, rect.bottom()))
            x += self.grid_size_huge
        painter.drawLines(grid_lines)

        # Draw horizontal thick lines
        grid_lines = []
        painter.setPen(QPen(self.canvas_grid_color_darker, 1.5))
        y = top
        while y < rect.bottom():
            grid_lines.append(QLineF(rect.left(), y, rect.right(), y))
            y += self.grid_size_huge
        painter.drawLines(grid_lines)

        self.draw_guide_numbers(left, painter, rect, top)

    def draw_guide_numbers(self, left, painter, rect, top):
        # draw numbers
        scale = self.current_view_scale()
        f = painter.font()
        f.setPointSize(6 / min(scale, 1))
        f.setFamily("Consolas")
        text_offset = 30
        painter.setFont(f)
        y = float(top)
        while y < float(rect.bottom()):
            y += self.grid_size_huge
            inty = int(y)
            if y > top + text_offset:
                painter.setPen(QPen(self.canvas_grid_color_darker.lighter(300)))
                painter.drawText(rect.left(), y - 1.0, str(inty))
        x = float(left)
        while x < rect.right():
            x += self.grid_size_huge
            intx = int(x)
            if x > left + text_offset:
                painter.setPen(QPen(self.canvas_grid_color_darker.lighter(300)))
                painter.drawText(x, rect.top() + painter.font().pointSize(), str(intx))

    @gui_exception
    def update_viewer(self, fit_image=True):
        qpixmap_image = self.image.toqpixmap()
        x, y = -qpixmap_image.width() / 2, -qpixmap_image.height() / 2
        if self._pixmap:
            pass
        else:
            self._pixmap = ImagePixmap()
            self._pixmap.setPixmap(qpixmap_image)
            self._pixmap.setOffset(x, y)
            self._scene.addItem(self._pixmap)
            self._pixmap.signals.hoverEnterEventSgn.connect(self.pixmap_hoverEnterEvent)
            self._pixmap.signals.hoverLeaveEventSgn.connect(self.pixmap_hoverLeaveEvent)
            self._pixmap.signals.hoverMoveEventSgn.connect(self.pixmap_hoverMoveEvent)
        if fit_image:
            self.resetTransform()
            self.centerOn(
                QPointF(self.sceneRect().width() / 2, self.sceneRect().height() / 2)
            )

    def _show_guide_lines(self):
        if self.hline and self.vline:
            self.hline.show()
            self.vline.show()

    def _hide_guide_lines(self):
        if self.hline and self.vline:
            self.hline.hide()
            self.vline.hide()

    def _update_guide_lines(self, x, y):
        bbox = self._pixmap.boundingRect()
        offset = QPointF(bbox.width() / 2, bbox.height() / 2)
        self.vline.setLine(x, -offset.y(), x, bbox.height() - offset.y())
        self.vline.setZValue(1)
        self.hline.setLine(-offset.x(), y, bbox.width() - offset.x(), y)
        self.hline.setZValue(1)

    def pixmap_hoverMoveEvent(self, evt, x, y):
        self._update_guide_lines(x, y)

    def pixmap_hoverEnterEvent(self):
        self._show_guide_lines()

    def pixmap_hoverLeaveEvent(self):
        self._hide_guide_lines()

    def enable_items(self, value):
        for item in self._scene.items():
            if isinstance(item, EditableItem):
                item.setEnabled(value)
