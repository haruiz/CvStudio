from cvstudio.pyqt import (
    QtCore,
    QRect,
    QPoint,
    QMovie,
    QCloseEvent,
    QShowEvent,
    QDialog,
    QLabel,
    QVBoxLayout,
    QApplication,
    QWidget,
)
from cvstudio.util import GUIUtils


class LoadingDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(LoadingDialog, self).__init__(*args, **kwargs)
        self.setFixedSize(100, 100)
        # self.setWindowOpacity(0.8)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        loading_gif = GUIUtils.get_assets_path().joinpath("icons/loading.gif")
        self.movie = QMovie(str(loading_gif))
        self.label = QLabel()
        self.label.setMovie(self.movie)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)

    def center(self, host: QWidget = None):
        if host:
            hostGeometry: QRect = host.geometry()
            # dialogGeometry : QRect = self.geometry()
            centerPoint: QPoint = hostGeometry.center()
            centerPoint = host.mapToGlobal(centerPoint)
            offset = 30
            targetPoint = QPoint(centerPoint.x() - offset, centerPoint.y() - offset)
            self.move(targetPoint)
        else:
            screen = QApplication.desktop().screenNumber(
                QApplication.desktop().cursor().pos()
            )
            centerPoint = QApplication.desktop().screenGeometry(screen).center()
            self.move(centerPoint)
        return self

    def showEvent(self, e: QShowEvent):
        if self.movie.state() == QMovie.NotRunning:
            self.movie.start()

    def closeEvent(self, e: QCloseEvent):
        if self.movie.state() == QMovie.Running:
            self.movie.stop()

    def exec_(self):
        self.center()
        return QDialog.exec_(self)
