import threading

import typing

from cvstudio.pyqt import QObject, Signal, QLabel, QtCore


class HoverThreadSignals(QObject):
    timeoutSignal = Signal()


class HoverThread(threading.Thread):
    def __init__(self, name="hover thread"):
        self._stop_event = threading.Event()
        self._sleep_time = 0.5
        self.timeout = 3
        self._counter = 0
        self.signals = HoverThreadSignals()
        threading.Thread.__init__(self, name=name)

    def run(self) -> None:
        while not self._stop_event.is_set():
            self._counter += 1
            print(self._counter)
            self._stop_event.wait(self._sleep_time)
            if self._counter > self.timeout:
                self._stop_event.set()
                self.signals.timeoutSignal.emit()
                return

    def join(self, timeout: typing.Optional[float] = None) -> None:
        self._stop_event.set()
        self._counter = 0
        threading.Thread.join(self, timeout)


class LabelHovered(QLabel, QObject):
    hoverTimeout = Signal(QLabel)

    def __init__(self, parent=None):
        super(LabelHovered, self).__init__(parent)
        self._hover_thread = None
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def timeout_callback(self):
        self.hoverTimeout.emit(self)

    def enterEvent(self, evt: QtCore.QEvent) -> None:
        self._hover_thread = HoverThread()
        self._hover_thread.start()
        self._hover_thread.signals.timeoutSignal.connect(self.timeout_callback)
        print("here")
        super(LabelHovered, self).enterEvent(evt)

    def leaveEvent(self, evt: QtCore.QEvent) -> None:
        if self._hover_thread:
            self._hover_thread.join()
            del self._hover_thread
            super(LabelHovered, self).leaveEvent(evt)
