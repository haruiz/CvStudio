import math

from PyQt5 import QtCore
from PyQt5.QtCore import QUrl, QObject, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QSlider, QGraphicsDropShadowEffect, QFrame

from cvstudio.util import VideoUtilities


class VideoPlayerWidgetSignals(QObject):
    video_position_changed_signal = pyqtSignal(int, int)
    video_duration_changed_signal = pyqtSignal(int)


class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)
        self._source = None
        self._total_duration = 0
        self.widget_layout = QVBoxLayout()
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_player = QVideoWidget()
        self.widget_layout.addWidget(self.video_player)
        self.media_player.setVideoOutput(self.video_player)
        # self.media_player.stateChanged.connect(self.mediaStateChanged)
        self.media_player.positionChanged.connect(self.on_positionChanged)
        self.signals = VideoPlayerWidgetSignals()
        self.media_player.durationChanged.connect(self.on_durationChanged)
        self.setLayout(self.widget_layout)
        print(self.media_player.duration())

    @property
    def total_duration(self):
        return self._total_duration

    @total_duration.setter
    def total_duration(self, val):
        self._total_duration = val

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self._total_duration = math.floor(VideoUtilities.duration(self.source))

    def play(self):
        if self._source:
            self.media_player.setMedia(
                QMediaContent(QUrl.fromLocalFile(self._source)))
            self.media_player.play()

    def resume(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def stop(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()

    def go_to(self, second: int):
        if self.media_player:
            self.media_player.setPosition(second * 1000)

    @QtCore.pyqtSlot('qint64')
    def on_positionChanged(self, position):
        self.signals.video_position_changed_signal.emit(math.floor(position / 1000), self.total_duration)
        if self.media_player.state() == QMediaPlayer.StoppedState:
            if 0 <= position <= self.total_duration * 1000:
                self.media_player.play()

    @QtCore.pyqtSlot('qint64')
    def on_durationChanged(self, duration):
        self.signals.video_duration_changed_signal.emit(math.floor(duration / 1000))


class VideoViewerContainer(QWidget):
    def __init__(self, window: QDialog, parent=None):
        super(VideoViewerContainer, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.resize(1024, 580)
        layout = QVBoxLayout(self)
        layout.addWidget(window)
        layout.setContentsMargins(0, 0, 6, 6)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(50)
        self.shadow.setColor(QColor(138, 145, 140))
        self.shadow.setOffset(8)
        window.setGraphicsEffect(self.shadow)


class VideoDialog(QDialog):
    def __init__(self, video_path, parent=None):
        super(VideoDialog, self).__init__(parent)
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.resize(400, 400)
        position = self.cursor().pos()
        position.setX(position.x())
        position.setY(position.y())
        self.move(position)
        # self.setWindowOpacity(0.9)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.widget = QFrame()
        self.widget.setStyleSheet('''
            QFrame{
            border-style: outset;
            border-width: 1px;
            /*border-radius: 10px;*/
            border-color: #B94129;
            }
        ''')
        # self.widget.setFrameStyle(QFrame.Box)
        self.widget.setLayout(QVBoxLayout())
        self.widget.layout().setContentsMargins(10, 10, 10, 10)

        self.video_player = VideoPlayer()
        self.video_player.source = video_path
        self.video_player.play()
        self.video_player.signals.video_position_changed_signal.connect(self.video_position_changed)
        duration = self.video_player.total_duration

        self.video_duration_slider = QSlider(orientation=QtCore.Qt.Horizontal)
        self.video_duration_slider.setRange(0, duration)
        self.video_duration_slider.setTickInterval(5)
        self.video_duration_slider.sliderMoved.connect(self.slider_changed_handler)
        # self.video_duration_slider.setTickPosition(QSlider.TicksBelow)

        self.setMouseTracking(True)
        self.setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.WindowStaysOnTopHint
                            | QtCore.Qt.FramelessWindowHint
                            | QtCore.Qt.X11BypassWindowManagerHint)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.widget.layout().addWidget(self.video_player)
        self.widget.layout().addWidget(self.video_duration_slider)
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

    def slider_changed_handler(self, change):
        self.video_player.go_to(change)

    def video_position_changed(self, current, total):
        self.video_duration_slider.setValue(current)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # print('mouseMoveEvent: x=%d, y=%d' % (event.x(), event.y()))
        if not self.rect().contains(event.pos()):
            self.close()
