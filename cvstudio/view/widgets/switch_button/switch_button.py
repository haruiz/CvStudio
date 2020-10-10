from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QCursor,QIcon,QMouseEvent,QImage
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect
import sys

from cvstudio.util import GUIUtilities
from cvstudio.view.widgets import ImageButton


class SwitchButton(ImageButton):
    def __init__(self, icon: QIcon = QIcon(), size: QSize = QSize(28, 28), tag=None, tooltip=None, parent=None):
        super(SwitchButton, self).__init__(icon, size, tag, tooltip, parent)
        self.setCheckable(True)
        self.setChecked(False)
        self._checked_icon = icon
        self._unchecked_icon = GUIUtilities.color_icon2gray_icon(self._checked_icon)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        if self.isChecked():
            self.setIcon(self._checked_icon)
        else:
            self.setIcon(self._unchecked_icon)
        super(SwitchButton, self).paintEvent(e)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        super(SwitchButton, self).mousePressEvent(e)

    def enterEvent(self, evt: QtCore.QEvent) -> None:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setColor(QtGui.QColor(76, 35, 45).lighter())
        shadow.setOffset(4)
        self.setGraphicsEffect(shadow)
        super(SwitchButton, self).enterEvent(evt)

    def leaveEvent(self, evt: QtCore.QEvent) -> None:
        self.setGraphicsEffect(self._effect)
        super(SwitchButton, self).leaveEvent(evt)