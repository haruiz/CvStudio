import threading
import typing

from PyQt5.QtCore import QObject,pyqtSignal


class HoverThreadSignals(QObject):
    timeoutSignal = pyqtSignal()


class HoverThread(threading.Thread):

    def __init__(self, name="hover thread"):
        self._stopevent = threading.Event()
        self._sleeptime =0.5
        self.timeout = 1
        self._counter = 0
        self.signals = HoverThreadSignals()
        threading.Thread.__init__(self, name=name)


    def run(self) -> None:
        while not  self._stopevent.is_set():
            self._counter += 1
            self._stopevent.wait(self._sleeptime)
            if self._counter > self.timeout:
                self._stopevent.set()
                self.signals.timeoutSignal.emit()
                return

    def join(self,timeout: typing.Optional[float] = None) -> None:
        self._stopevent.set()
        self._counter = 0
        threading.Thread.join(self, timeout)