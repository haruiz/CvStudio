#!/usr/bin/env python
# $RCSfile: imageviewer.py,v $ $Revision: 527a78cd8251 $ $Date: 2010/10/18 20:47:58 $

"""
This module contains the following classes:

+ :class:`SynchableGraphicsView`
+ :class:`ImageViewer`
+ :class:`MainWindow`

"""

# ====================================================================


import os
import sys

# ====================================================================
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QGraphicsView, QFrame, QMainWindow, QApplication, QGraphicsScene, QGridLayout, QLabel, \
    QGraphicsPixmapItem, QAction, QMenu


# ====================================================================


class SynchableGraphicsView(QGraphicsView):
    """|QGraphicsView| that can synchronize panning & zooming of multiple
    instances.

    Also adds support for various scrolling operations and mouse wheel
    zooming."""

    def __init__(self, scene=None, parent=None):
        """:param scene: initial |QGraphicsScene|
        :type scene: QGraphicsScene or None
        :param QWidget: parent widget
        :type QWidget: QWidget or None"""
        if scene:
            super(SynchableGraphicsView, self).__init__(scene, parent)
        else:
            super(SynchableGraphicsView, self).__init__(parent)

        self._handDrag = False  # disable panning view by dragging
        self.clearTransformChanges()
        self.connectSbarSignals(self.scrollChanged)

    # ------------------------------------------------------------------

    # Signals

    transformChanged = QtCore.pyqtSignal()
    """Transformed Changed **Signal**.

    Emitted whenever the |QGraphicsView| Transform matrix has been
    changed."""

    scrollChanged = QtCore.pyqtSignal()
    """Scroll Changed **Signal**.

    Emitted whenever the scrollbar position or range has changed."""

    wheelNotches = QtCore.pyqtSignal(float)
    """Wheel Notches **Signal**.

    Emitted whenever the mouse wheel has been rolled. A wheelnotch is
    equal to wheel delta / 240"""

    def connectSbarSignals(self, slot):
        """Connect to scrollbar changed signals to synchronize panning.

        :param slot: slot to connect scrollbar signals to."""
        sbar = self.horizontalScrollBar()
        sbar.valueChanged.connect(slot, type=QtCore.Qt.UniqueConnection)
        # sbar.sliderMoved.connect(slot, type=QtCore.Qt.UniqueConnection)
        sbar.rangeChanged.connect(slot, type=QtCore.Qt.UniqueConnection)

        sbar = self.verticalScrollBar()
        sbar.valueChanged.connect(slot, type=QtCore.Qt.UniqueConnection)
        # sbar.sliderMoved.connect(slot, type=QtCore.Qt.UniqueConnection)
        sbar.rangeChanged.connect(slot, type=QtCore.Qt.UniqueConnection)

        # self.scrollChanged.connect(slot, type=QtCore.Qt.UniqueConnection)

    def disconnectSbarSignals(self):
        """Disconnect from scrollbar changed signals."""
        sbar = self.horizontalScrollBar()
        sbar.valueChanged.disconnect()
        # sbar.sliderMoved.disconnect()
        sbar.rangeChanged.disconnect()

        sbar = self.verticalScrollBar()
        sbar.valueChanged.disconnect()
        # sbar.sliderMoved.disconnect()
        sbar.rangeChanged.disconnect()

    @property
    def handDragging(self):
        """Hand dragging state (*bool*)"""
        return self._handDrag

    @property
    def scrollState(self):
        """Tuple of percentage of scene extents
        *(sceneWidthPercent, sceneHeightPercent)*"""
        centerPoint = self.mapToScene(self.viewport().width() / 2,
                                      self.viewport().height() / 2)
        sceneRect = self.sceneRect()
        centerWidth = centerPoint.x() - sceneRect.left()
        centerHeight = centerPoint.y() - sceneRect.top()
        sceneWidth = sceneRect.width()
        sceneHeight = sceneRect.height()

        sceneWidthPercent = centerWidth / sceneWidth if sceneWidth != 0 else 0
        sceneHeightPercent = centerHeight / sceneHeight if sceneHeight != 0 else 0
        return (sceneWidthPercent, sceneHeightPercent)

    @scrollState.setter
    def scrollState(self, state):
        sceneWidthPercent, sceneHeightPercent = state
        x = (sceneWidthPercent * self.sceneRect().width() +
             self.sceneRect().left())
        y = (sceneHeightPercent * self.sceneRect().height() +
             self.sceneRect().top())
        self.centerOn(x, y)

    @property
    def zoomFactor(self):
        """Zoom scale value (*float*)."""
        return self.transform().m11()

    @zoomFactor.setter
    def zoomFactor(self, newZoomFactor):
        newZoomFactor = newZoomFactor / self.zoomFactor
        self.scale(newZoomFactor, newZoomFactor)

    def wheelEvent(self, wheelEvent):
        """Overrides the wheelEvent to handle zooming.

        :param QWheelEvent wheelEvent: instance of |QWheelEvent|"""
        assert isinstance(wheelEvent, QtGui.QWheelEvent)
        if wheelEvent.modifiers() & QtCore.Qt.ControlModifier:
            self.wheelNotches.emit(wheelEvent.angleDelta().y() / 240.0)
            wheelEvent.accept()
        else:
            super(SynchableGraphicsView, self).wheelEvent(wheelEvent)

    def keyReleaseEvent(self, keyEvent):
        """Overrides to make sure key release passed on to other classes.

        :param QKeyEvent keyEvent: instance of |QKeyEvent|"""
        assert isinstance(keyEvent, QtGui.QKeyEvent)
        # print("graphicsView keyRelease count=%d, autoRepeat=%s" %
        # (keyEvent.count(), keyEvent.isAutoRepeat()))
        keyEvent.ignore()
        # super(SynchableGraphicsView, self).keyReleaseEvent(keyEvent)

    def checkTransformChanged(self):
        """Return True if view transform has changed.

        Overkill. For current implementation really only need to check
        if ``m11()`` has changed.

        :rtype: bool"""
        delta = 0.001
        result = False

        def different(t, u):
            if u == 0.0:
                d = abs(t - u)
            else:
                d = abs((t - u) / u)
            return d > delta

        t = self.transform()
        u = self._transform

        if (different(t.m11(), u.m11()) or
                different(t.m22(), u.m22()) or
                different(t.m12(), u.m12()) or
                different(t.m21(), u.m21()) or
                different(t.m31(), u.m31()) or
                different(t.m32(), u.m32())):
            self._transform = t
            self.transformChanged.emit()
            result = True
        return result

    def clearTransformChanges(self):
        """Reset view transform changed info."""
        self._transform = self.transform()

    def scrollToTop(self):
        """Scroll view to top."""
        sbar = self.verticalScrollBar()
        sbar.setValue(sbar.minimum())

    def scrollToBottom(self):
        """Scroll view to bottom."""
        sbar = self.verticalScrollBar()
        sbar.setValue(sbar.maximum())

    def scrollToBegin(self):
        """Scroll view to left edge."""
        sbar = self.horizontalScrollBar()
        sbar.setValue(sbar.minimum())

    def scrollToEnd(self):
        """Scroll view to right edge."""
        sbar = self.horizontalScrollBar()
        sbar.setValue(sbar.maximum())

    def centerView(self):
        """Center view."""
        sbar = self.verticalScrollBar()
        sbar.setValue((sbar.maximum() + sbar.minimum()) / 2)
        sbar = self.horizontalScrollBar()
        sbar.setValue((sbar.maximum() + sbar.minimum()) / 2)

    def enableScrollBars(self, enable):
        """Set visiblility of the view's scrollbars.

        :param bool enable: True to enable the scrollbars """
        if enable:
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        else:
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def enableHandDrag(self, enable):
        """Set whether dragging the view with the hand cursor is allowed.

        :param bool enable: True to enable hand dragging """
        if enable:
            if not self._handDrag:
                self._handDrag = True
                self.setDragMode(QGraphicsView.ScrollHandDrag)
        else:
            if self._handDrag:
                self._handDrag = False
                self.setDragMode(QGraphicsView.NoDrag)

    def dumpTransform(self, t, padding=""):
        """Dump the transform t to stdout.

        :param t: the transform to dump
        :param str padding: each line is preceded by padding"""
        print("%s%5.3f %5.3f %5.3f" % (padding, t.m11(), t.m12(), t.m13()))
        print("%s%5.3f %5.3f %5.3f" % (padding, t.m21(), t.m22(), t.m23()))
        print("%s%5.3f %5.3f %5.3f" % (padding, t.m31(), t.m32(), t.m33()))


class ImageViewer(QFrame):
    """Image Viewer than can pan & zoom images (|QPixmap|\ s)."""

    def __init__(self, pixmap=None, name=None):
        """:param pixmap: |QPixmap| to display
        :type pixmap: |QPixmap| or None
        :param name: name associated with this ImageViewer
        :type name: str or None"""
        super(ImageViewer, self).__init__()

        # self.setFrameStyle(QtGui.QFrame.Sunken | QtGui.QFrame.StyledPanel)
        self.setFrameStyle(QFrame.NoFrame)

        self._relativeScale = 1.0  # scale relative to other ImageViewer instances
        self._zoomFactorDelta = 1.25

        self._scene = QGraphicsScene()
        self._view = SynchableGraphicsView(self._scene)

        self._view.setInteractive(False)
        # self._view.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self._view.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)
        # self._view.setViewportUpdateMode(QtGui.QGraphicsView.SmartViewportUpdate)
        # self._view.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        self._view.setTransformationAnchor(QGraphicsView.AnchorViewCenter)

        # pass along underlying signals
        self._scene.changed.connect(self.sceneChanged)
        self._view.transformChanged.connect(self.transformChanged)
        self._view.scrollChanged.connect(self.scrollChanged)
        self._view.wheelNotches.connect(self.handleWheelNotches)

        gridSize = 10
        backgroundPixmap = QtGui.QPixmap(gridSize * 2, gridSize * 2)
        backgroundPixmap.fill(QtGui.QColor("powderblue"))
        painter = QtGui.QPainter(backgroundPixmap)
        backgroundColor = QtGui.QColor("palegoldenrod")
        painter.fillRect(0, 0, gridSize, gridSize, backgroundColor)
        painter.fillRect(gridSize, gridSize, gridSize, gridSize, backgroundColor)
        painter.end()

        self._scene.setBackgroundBrush(QtGui.QBrush(backgroundPixmap))
        self._view.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)

        self._pixmapItem = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmapItem)
        if pixmap:
            self.pixmap = pixmap

        rect = self._scene.addRect(QtCore.QRectF(0, 0, 100, 100),
                                   QtGui.QPen(QtGui.QColor("red")))
        rect.setZValue(1.0)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(0)

        self._label = QLabel()
        # self._label.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        self._label.setFrameStyle(QFrame.Panel)
        self._label.setAutoFillBackground(True);
        self._label.setBackgroundRole(QtGui.QPalette.ToolTipBase)
        self.viewName = name

        layout.addWidget(self._view, 0, 0)
        layout.addWidget(self._label, 0, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.setLayout(layout)

        self.enableScrollBars(True)
        self._view.show()

    # ------------------------------------------------------------------

    sceneChanged = QtCore.pyqtSignal('QList<QRectF>')
    """Scene Changed **Signal**.

    Emitted whenever the |QGraphicsScene| content changes."""

    transformChanged = QtCore.pyqtSignal()
    """Transformed Changed **Signal**.

    Emitted whenever the |QGraphicsView| Transform matrix has been changed."""

    scrollChanged = QtCore.pyqtSignal()
    """Scroll Changed **Signal**.

    Emitted whenever the scrollbar position or range has changed."""

    def connectSbarSignals(self, slot):
        """Connect to scrollbar changed signals.

        :param slot: slot to connect scrollbar signals to."""
        self._view.connectSbarSignals(slot)

    def disconnectSbarSignals(self):
        self._view.disconnectSbarSignals()

    @property
    def pixmap(self):
        """The currently viewed |QPixmap| (*QPixmap*)."""
        return self._pixmapItem.pixmap()

    @pixmap.setter
    def pixmap(self, pixmap):
        assert isinstance(pixmap, QtGui.QPixmap)
        self._pixmapItem.setPixmap(pixmap)
        self._pixmapItem.setOffset(-pixmap.width() / 2.0, -pixmap.height() / 2.0)
        self._pixmapItem.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self.fitToWindow()

    @property
    def viewName(self):
        """The name associated with ImageViewer (*str*)."""
        return self._name

    @viewName.setter
    def viewName(self, name):
        if name:
            self._label.setText("<b>%s</b>" % name)
            self._label.show()
        else:
            self._label.setText("")
            self._label.hide()
        self._name = name

    @property
    def handDragging(self):
        """Hand dragging state (*bool*)"""
        return self._view.handDragging

    @property
    def scrollState(self):
        """Tuple of percentage of scene extents
        *(sceneWidthPercent, sceneHeightPercent)*"""
        return self._view.scrollState

    @scrollState.setter
    def scrollState(self, state):
        self._view.scrollState = state

    @property
    def zoomFactor(self):
        """Zoom scale value (*float*)."""
        return self._view.zoomFactor

    @zoomFactor.setter
    def zoomFactor(self, newZoomFactor):
        if newZoomFactor < 1.0:
            self._pixmapItem.setTransformationMode(QtCore.Qt.SmoothTransformation)
        else:
            self._pixmapItem.setTransformationMode(QtCore.Qt.FastTransformation)
        self._view.zoomFactor = newZoomFactor

    @property
    def _horizontalScrollBar(self):
        """Get the ImageViewer horizontal scrollbar widget (*QScrollBar*).

        (Only used for debugging purposes)"""
        return self._view.horizontalScrollBar()

    @property
    def _verticalScrollBar(self):
        """Get the ImageViewer vertical scrollbar widget (*QScrollBar*).

        (Only used for debugging purposes)"""
        return self._view.verticalScrollBar()

    @property
    def _sceneRect(self):
        """Get the ImageViewer sceneRect (*QRectF*).

        (Only used for debugging purposes)"""
        return self._view.sceneRect()

    @QtCore.pyqtSlot()
    def scrollToTop(self):
        """Scroll to top of image."""
        self._view.scrollToTop()

    @QtCore.pyqtSlot()
    def scrollToBottom(self):
        """Scroll to bottom of image."""
        self._view.scrollToBottom()

    @QtCore.pyqtSlot()
    def scrollToBegin(self):
        """Scroll to left side of image."""
        self._view.scrollToBegin()

    @QtCore.pyqtSlot()
    def scrollToEnd(self):
        """Scroll to right side of image."""
        self._view.scrollToEnd()

    @QtCore.pyqtSlot()
    def centerView(self):
        """Center image in view."""
        self._view.centerView()

    @QtCore.pyqtSlot(bool)
    def enableScrollBars(self, enable):
        """Set visiblility of the view's scrollbars.

        :param bool enable: True to enable the scrollbars """
        self._view.enableScrollBars(enable)

    @QtCore.pyqtSlot(bool)
    def enableHandDrag(self, enable):
        """Set whether dragging the view with the hand cursor is allowed.

        :param bool enable: True to enable hand dragging """
        self._view.enableHandDrag(enable)

    @QtCore.pyqtSlot()
    def zoomIn(self):
        """Zoom in on image."""
        self.scaleImage(self._zoomFactorDelta)

    @QtCore.pyqtSlot()
    def zoomOut(self):
        """Zoom out on image."""
        self.scaleImage(1 / self._zoomFactorDelta)

    @QtCore.pyqtSlot()
    def actualSize(self):
        """Change zoom to show image at actual size.

        (image pixel is equal to screen pixel)"""
        self.scaleImage(1.0, combine=False)

    @QtCore.pyqtSlot()
    def fitToWindow(self):
        """Fit image within view."""
        if not self._pixmapItem.pixmap():
            return
        self._pixmapItem.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self._view.fitInView(self._pixmapItem, QtCore.Qt.KeepAspectRatio)
        self._view.checkTransformChanged()

    @QtCore.pyqtSlot()
    def fitWidth(self):
        """Fit image width to view width."""
        if not self._pixmapItem.pixmap():
            return
        margin = 2
        viewRect = self._view.viewport().rect().adjusted(margin, margin,
                                                         -margin, -margin)
        factor = viewRect.width() / self._pixmapItem.pixmap().width()
        self.scaleImage(factor, combine=False)

    @QtCore.pyqtSlot()
    def fitHeight(self):
        """Fit image height to view height."""
        if not self._pixmapItem.pixmap():
            return
        margin = 2
        viewRect = self._view.viewport().rect().adjusted(margin, margin,
                                                         -margin, -margin)
        factor = viewRect.height() / self._pixmapItem.pixmap().height()
        self.scaleImage(factor, combine=False)

    def handleWheelNotches(self, notches):
        """Handle wheel notch event from underlying |QGraphicsView|.

        :param float notches: Mouse wheel notches"""
        self.scaleImage(self._zoomFactorDelta ** notches)

    def closeEvent(self, event):
        """Overriden in order to disconnect scrollbar signals before
        closing.

        :param QEvent event: instance of a |QEvent|

        If this isn't done Python crashes!"""
        # self.scrollChanged.disconnect() #doesn't prevent crash
        self.disconnectSbarSignals()
        super(ImageViewer, self).closeEvent(event)

    def scaleImage(self, factor, combine=True):
        """Scale image by value.

        :param float factor: either new :attr:`zoomFactor` or amount to scale
                             current :attr:`zoomFactor`

        :param bool combine: if ``True`` scales the current
                             :attr:`zoomFactor` by value.  Otherwise
                             just sets :attr:`zoomFactor` to value"""
        if not self._pixmapItem.pixmap():
            return

        if combine:
            self.zoomFactor = self.zoomFactor * factor
        else:
            self.zoomFactor = factor
        self._view.checkTransformChanged()

    def dumpTransform(self):
        """Dump view transform to stdout."""
        self._view.dumpTransform(self._view.transform(), " " * 4)


class MainWindow(QMainWindow):
    """Sample app to test the :class:`ImageViewer` class."""

    def __init__(self, pixmap):
        """:param QPixmap pixmap: |QPixmap| to display"""
        super(MainWindow, self).__init__()

        self._imageViewer = ImageViewer(pixmap, "View 1")
        self.setCentralWidget(self._imageViewer)

        # self._imageViewer.sceneChanged.connect(self.sceneChanged)
        self._imageViewer.transformChanged.connect(self.transformChanged)
        self._imageViewer.scrollChanged.connect(self.scrollChanged)

        # self._imageViewer.enableScrollBars(True)
        # self._imageViewer.enableHandDrag(True)

        self.createActions()
        self.createMenus()

        self.eventCounter = 0

    def createActions(self):
        """Create actions for the menus."""

        # File Actions
        self.exitAct = QAction(
            "E&xit", self,
            shortcut=QKeySequence.Quit,
            statusTip="Exit the application")

        # view actions
        self.scrollToTopAct = QAction(
            "&Top", self,
            shortcut=QKeySequence.MoveToStartOfDocument,
            triggered=self._imageViewer.scrollToTop)

        self.scrollToBottomAct = QAction(
            "&Bottom", self,
            shortcut=QKeySequence.MoveToEndOfDocument,
            triggered=self._imageViewer.scrollToBottom)

        self.scrollToBeginAct = QAction(
            "&Left Edge", self,
            shortcut=QKeySequence.MoveToStartOfLine,
            triggered=self._imageViewer.scrollToBegin)

        self.scrollToEndAct = QAction(
            "&Right Edge", self,
            shortcut=QKeySequence.MoveToEndOfLine,
            triggered=self._imageViewer.scrollToEnd)

        self.centerView = QAction(
            "&Center", self,
            shortcut="5",
            triggered=self._imageViewer.centerView)

        # zoom actions
        self.zoomInAct = QAction(
            "Zoo&m In (25%)", self,
            shortcut=QKeySequence.ZoomIn,
            triggered=self._imageViewer.zoomIn)

        self.zoomOutAct = QAction(
            "Zoom &Out (25%)", self,
            shortcut=QKeySequence.ZoomOut,
            triggered=self._imageViewer.zoomOut)

        self.actualSizeAct = QAction(
            "Actual &Size", self,
            shortcut="/",
            triggered=self._imageViewer.actualSize)

        self.fitToWindowAct = QAction(
            "Fit &Image", self,
            shortcut="*",
            triggered=self._imageViewer.fitToWindow)

        self.fitWidthAct = QAction(
            "Fit &Width", self,
            shortcut="Alt+Right",
            triggered=self._imageViewer.fitWidth)

        self.fitHeightAct = QAction(
            "Fit &Height", self,
            shortcut="Alt+Down",
            triggered=self._imageViewer.fitHeight)

        self.zoomToAct = QAction(
            "&Zoom To...", self,
            shortcut="Z"
        )

    def createMenus(self):
        """Create the menus."""

        # Create File Menu
        self.fileMenu = QMenu("&File")
        self.fileMenu.addAction(self.exitAct)

        # Create Scroll Menu
        self.scrollMenu = QMenu("&Scroll", self)
        self.scrollMenu.addAction(self.scrollToTopAct)
        self.scrollMenu.addAction(self.scrollToBottomAct)
        self.scrollMenu.addAction(self.scrollToBeginAct)
        self.scrollMenu.addAction(self.scrollToEndAct)
        self.scrollMenu.addAction(self.centerView)

        # Create Zoom Menu
        self.zoomMenu = QMenu("&Zoom", self)
        self.zoomMenu.addAction(self.zoomInAct)
        self.zoomMenu.addAction(self.zoomOutAct)
        self.zoomMenu.addSeparator()
        self.zoomMenu.addAction(self.actualSizeAct)
        self.zoomMenu.addAction(self.fitToWindowAct)
        self.zoomMenu.addAction(self.fitWidthAct)
        self.zoomMenu.addAction(self.fitHeightAct)
        # self.zoomMenu.addSeparator()
        # self.zoomMenu.addAction(self.zoomToAct)

        # Add menus to menubar
        menubar = self.menuBar()
        menubar.addMenu(self.fileMenu)
        menubar.addMenu(self.scrollMenu)
        menubar.addMenu(self.zoomMenu)

    # ------------------------------------------------------------------

    @QtCore.pyqtSlot(list)
    def sceneChanged(self, rects):
        """Triggered when the underlying graphics scene has changed.

        :param list rects: scene rectangles that indicate the area that
                           has been changed."""
        r = self._imageViewer._sceneRect
        print("%3d Scene changed = (%.2f,%.2f,%.2f,%.2f %.2fx%.2f)" %
              (self.eventCounter, r.left(), r.top(), r.right(), r.bottom(),
               r.width(), r.height()))
        self.eventCounter += 1

    @QtCore.pyqtSlot()
    def transformChanged(self):
        """Triggered when the underlying view has been scaled, translated,
        or rotated.

        In practice, only scaling occurs."""
        print("%3d transform changed = " % self.eventCounter)
        self._imageViewer.dumpTransform()
        self.eventCounter += 1

    @QtCore.pyqtSlot()
    def scrollChanged(self):
        """Triggered when the views scrollbars have changed."""
        hbar = self._imageViewer._horizontalScrollBar
        hpos = hbar.value()
        hmin = hbar.minimum()
        hmax = hbar.maximum()

        vbar = self._imageViewer._verticalScrollBar
        vpos = vbar.value()
        vmin = vbar.minimum()
        vmax = vbar.maximum()

        print("%3d scroll changed h=(%d,%d,%d) v=(%d,%d,%d)" %
              (self.eventCounter, hpos, hmin, hmax, vpos, vmin, vmax))
        self.eventCounter += 1

    def keyPressEvent(self, keyEvent):
        """Overrides to enable panning while dragging.

        :param QKeyEvent keyEvent: instance of |QKeyEvent|"""
        assert isinstance(keyEvent, QtGui.QKeyEvent)
        if keyEvent.key() == QtCore.Qt.Key_Space:
            if (not keyEvent.isAutoRepeat() and
                    not self._imageViewer.handDragging):
                self._imageViewer.enableHandDrag(True)
            keyEvent.accept()
        else:
            keyEvent.ignore()
            super(MainWindow, self).keyPressEvent(keyEvent)

    def keyReleaseEvent(self, keyEvent):
        """Overrides to disable panning while dragging.

        :param QKeyEvent keyEvent: instance of |QKeyEvent|"""
        assert isinstance(keyEvent, QtGui.QKeyEvent)
        if keyEvent.key() == QtCore.Qt.Key_Space:
            if not keyEvent.isAutoRepeat() and self._imageViewer.handDragging:
                self._imageViewer.enableHandDrag(False)
            keyEvent.accept()
        else:
            keyEvent.ignore()
            super(MainWindow, self).keyReleaseEvent(keyEvent)

    def closeEvent(self, event):
        """Overrides close event to save application settings.

        :param QEvent event: instance of |QEvent|"""
        self.writeSettings()
        event.accept()

    def writeSettings(self):
        """Write application settings."""
        settings = QtCore.QSettings()
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
        settings.setValue('windowgeometry', self.saveGeometry())
        settings.setValue('windowstate', self.saveState())

    def readSettings(self):
        """Read application settings."""
        settings = QtCore.QSettings()
        pos = settings.value('pos', QtCore.QPoint(200, 200))
        size = settings.value('size', QtCore.QSize(400, 400))
        self.move(pos)
        self.resize(size)
        if settings.contains('windowgeometry'):
            self.restoreGeometry(settings.value('windowgeometry'))
        if settings.contains('windowstate'):
            self.restoreState(settings.value('windowstate'))


def main():
    """Test app to run from command line.

    **Usage**::

      python26 imageviewer.py imagefilename
    """

    COMPANY = "TPWorks"
    DOMAIN = "dummy-tpworks.com"
    APPNAME = "Image Viewer Test"

    app = QApplication(sys.argv)
    imageFilename = r"D:\images\00a8b82f9944ae6c.jpg"  # app.arguments()[-1]
    if not os.path.exists(imageFilename):
        print('File "%s" does not exist.' % imageFilename)
        return

    pixmap = QtGui.QPixmap(imageFilename)
    if (not pixmap or
            pixmap.width() == 0 or pixmap.height == 0):
        print('File "%s" is not an image file that Qt can open.' % imageFilename)
        return

    QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)
    app.setOrganizationName(COMPANY)
    app.setOrganizationDomain(DOMAIN)
    app.setApplicationName(APPNAME)
    app.setWindowIcon(QtGui.QIcon(":/icon.png"))

    mainWin = MainWindow(pixmap)
    mainWin.setWindowTitle(APPNAME)
    mainWin.readSettings()
    mainWin.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
