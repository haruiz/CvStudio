from PyQt5.QtCore import QObject, pyqtSignal, QSize
from PyQt5.QtWidgets import QWidget, QFrame, QVBoxLayout
from util import GUIUtilities
from view.widgets import ImageButton
from view.widgets.switch_button import SwitchButton


class ImageViewerToolBox(QWidget, QObject):
    onAction = pyqtSignal(str)
    def __init__(self, parent=None):
        super(ImageViewerToolBox, self).__init__(parent)
        self._icon_size = QSize(28, 28)
        self._toolbox = [
            SwitchButton(icon=GUIUtilities.get_icon("polygon.png"), tag="polygon"),
            SwitchButton(icon=GUIUtilities.get_icon("square.png"), tag="box"),
            SwitchButton(icon=GUIUtilities.get_icon("circle.png"), tag="ellipse"),
            SwitchButton(icon=GUIUtilities.get_icon("highlighter.png"), tag="free"),
            SwitchButton(icon=GUIUtilities.get_icon("robotic-hand.png"), tag="points"),
            SwitchButton(icon=GUIUtilities.get_icon("cursor.png"), tag="pointer"),
            ImageButton(icon=GUIUtilities.get_icon("save-icon.png"), size=self._icon_size, tag="save"),
            ImageButton(icon=GUIUtilities.get_icon("clean.png"), size=self._icon_size, tag="clean")]
        self._layout = QVBoxLayout(self)
        for button in self._toolbox:
            self._layout.addWidget(button)
            self._layout.addWidget(SeparatorWidget())
            button.clicked.connect(self._action_toolbox_clicked_slot)

    def _action_toolbox_clicked_slot(self):
        buttons = list(filter(lambda btn: btn is not self.sender(), self._toolbox))
        for b in buttons:
            if isinstance(b, SwitchButton):
                b.setChecked(False)
        self.onAction.emit(self.sender().tag)




class SeparatorWidget(QFrame):
    def __init__(self, parent=None):
        super(SeparatorWidget, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet('''
            QFrame{
                background-color: black;
            }
        ''')