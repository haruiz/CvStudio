from PyQt5 import QtCore
from PyQt5.QtGui import QMouseEvent,QPainter,QWheelEvent,QPixmap
from PyQt5.QtWidgets import QVBoxLayout,QFrame,QDialog,QWidget,QGraphicsView,QGraphicsScene,QGraphicsPixmapItem


class ImageDialogViewer(QGraphicsView):
    def __init__(self, parent=None):
        super(ImageDialogViewer, self).__init__(parent)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        # self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._scene=QGraphicsScene(self)
        self.setScene(self._scene)
        self._pixmap=None

    @property
    def pixmap(self):
        return self._pixmap

    @pixmap.setter
    def pixmap(self, value: QPixmap):
        self._pixmap = value
        self._pixmap=QGraphicsPixmapItem()
        self._pixmap.setPixmap(value)
        size=300
        w = value.width()
        h = value.height()
        scale=size/w
        new_w,new_h=w*scale,h*scale
        self._pixmap.setOffset(-value.width()/2,-value.height()/2)
        self._pixmap.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self._scene.addItem(self._pixmap)
        self.scale(scale, scale)

    def wheelEvent(self,event: QWheelEvent):
        adj=(event.angleDelta().y()/120)*0.1
        self.scale(1+adj,1+adj)




class ImageDialog(QDialog):
    def __init__(self,image_path,  parent=None):
        super(ImageDialog,self).__init__(parent)
        position=self.cursor().pos()
        position.setX(position.x())
        position.setY(position.y())
        self.move(position)
        #self.setWindowOpacity(0.9)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.widget = QFrame()
        self.widget.setStyleSheet('''
            QFrame{
            border-style: outset;
            border-width: 1px;
            /*border-radius: 10px;*/
            border-color: #B94129;
            }
        ''')
        self.widget.setLayout(QVBoxLayout())
        self.widget.layout().setContentsMargins(0,0,0,0)
        self.setMouseTracking(True)
        self.setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.X11BypassWindowManagerHint)
        self.qgraphics_view = ImageDialogViewer()
        self.qgraphics_view.pixmap = QPixmap(image_path)
        self.widget.layout().addWidget(self.qgraphics_view)
        self.layout().addWidget(self.widget)

    def setMouseTracking(self, flag):
        def set_mouse_tracking(parent):
            for child in parent.findChildren(QtCore.QObject):
                try:
                    child.setMouseTracking(flag)
                except:
                    pass
                set_mouse_tracking(child)
        QWidget.setMouseTracking(self, flag)
        set_mouse_tracking(self)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # print('mouseMoveEvent: x=%d, y=%d' % (event.x(), event.y()))
        if not self.rect().contains(event.pos()):
            self.close()