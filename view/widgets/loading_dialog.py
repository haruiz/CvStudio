import os

from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import QRect,QPointF,QPoint
from PyQt5.QtGui import QMovie,QCloseEvent,QShowEvent
from PyQt5.QtWidgets import QDialog,QLabel,QVBoxLayout,QDesktopWidget,QApplication,QWidget


class QLoadingDialog(QDialog):
    def __init__(self,gif_file: str = os.path.abspath("./assets/icons/dark/loading.gif"), parent=None):
        super(QLoadingDialog, self).__init__(parent)
        #self.setFixedSize(300,300)
        #self.setWindowOpacity(0.8)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.movie= QMovie(gif_file)
        self.label = QLabel()
        self.label.setMovie(self.movie)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)


    def center(self, host: QWidget=None):
        if host:
            hostGeometry : QRect = host.geometry()
            #dialogGeometry : QRect = self.geometry()
            centerPoint : QPoint = hostGeometry.center()
            centerPoint=host.mapToGlobal(centerPoint)
            offset = 30
            targetPoint = QPoint(centerPoint.x() - offset, centerPoint.y() - offset)
            self.move(targetPoint)
        else:
            screen=QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
            centerPoint=QApplication.desktop().screenGeometry(screen).center()
            self.move(centerPoint)
        return self


    def showEvent(self, e: QShowEvent):
        if self.movie.state() == QMovie.NotRunning:
            self.movie.start()

    def closeEvent(self, e : QCloseEvent):
        if self.movie.state() == QMovie.Running:
            self.movie.stop()

    def exec_(self):
        self.center()
        return QDialog.exec_(self)

