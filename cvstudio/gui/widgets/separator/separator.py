from cvstudio.pyqt import QFrame


class Separator(QFrame):
    def __init__(self, parent=None):
        super(Separator, self).__init__(parent)
        self.setFrameShape(QFrame.VLine)
        #self.setFrameShadow(QFrame.Sunken)
        self.setFixedHeight(30)