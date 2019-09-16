from PyQt5 import QtCore
from PyQt5.QtCore import QObject,pyqtSignal
from PyQt5.QtWidgets import QLabel

from view.widgets.gallery.hover_thread import HoverThread


class LabelHovered(QLabel, QObject):
    hoverTimeout = pyqtSignal(QLabel)
    def __init__(self,parent=None):
        super(LabelHovered, self).__init__(parent)
        self._hover_thread =None

    def timeout_callback(self):
        self.hoverTimeout.emit(self)

    def enterEvent(self, evt: QtCore.QEvent) -> None:
        self._hover_thread = HoverThread()
        self._hover_thread.start()
        self._hover_thread.signals.timeoutSignal.connect(self.timeout_callback)
        super(LabelHovered, self).enterEvent(evt)

    def leaveEvent(self, evt: QtCore.QEvent) -> None:
        if self._hover_thread:
            self._hover_thread.join()
            del self._hover_thread
            super(LabelHovered, self).leaveEvent(evt)