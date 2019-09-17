# import torch.hub
# import urllib
# from PIL import Image
# from torch import Tensor,nn
# from torchvision import transforms
# import  numpy as np
# import matplotlib.pyplot as plt
# from torchvision.models import ResNet
#
# model : nn.Module = torch.hub.load('pytorch/vision', 'resnet18', pretrained=True)
# #print(model.eval())
# for m in model.modules():
#     print(model)

# url, filename = ("https://github.com/pytorch/hub/raw/master/dog.jpg", "dog.jpg")
# try: urllib.URLopener().retrieve(url, filename)
# except: urllib.request.urlretrieve(url, filename)
#
# def imshow(inp, title=None):
#     """Imshow for Tensor."""
#     inp = inp.numpy().transpose((1, 2, 0))
#     mean = np.array([0.485, 0.456, 0.406])
#     std = np.array([0.229, 0.224, 0.225])
#     inp = std * inp + mean
#     inp = np.clip(inp, 0, 1)
#     plt.imshow(inp)
#     if title is not None:
#         plt.title(title)
#     plt.pause(0.001)  # pause a bit so that plots are updated
#
# input_image = Image.open(filename)
# preprocess = transforms.Compose([
#     transforms.Resize(256),
#     transforms.CenterCrop(224),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
# ])
# input_tensor: Tensor = preprocess(input_image)
# imshow(input_tensor)
# input_batch = input_tensor.unsqueeze(0)

# models = torch.hub.list('pytorch/vision', force_reload=False)
# for m in models:
#     print(torch.hub.help('pytorch/vision', m, force_reload=True))
import typing

from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import QModelIndex,Qt,QObject,pyqtSignal,QRect,QSize
from PyQt5.QtGui import QStandardItemModel,QPixmap,QColor,QBrush
from PyQt5.QtWidgets import (QApplication,QSpinBox,QStyledItemDelegate,
                             QTableView,QStyleOptionViewItem,QLabel,QPushButton,QLineEdit,QWidget,QHBoxLayout,
                             QColorDialog,QVBoxLayout,QSizePolicy,QStyleOptionButton,QStyle,QAbstractItemView)


class ClickableLineEdit(QLineEdit, QObject):
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super(ClickableLineEdit, self).__init__(parent)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.clicked.emit()



class ColorPicker(QWidget):
    def __init__(self, parent=None):
        super(ColorPicker, self).__init__(parent)
        layout=QVBoxLayout()
        self.colorEditor=ClickableLineEdit(parent)
        self.colorEditor.setReadOnly(True)
        self.colorEditor.setCursor(QtCore.Qt.PointingHandCursor)
        self.colorEditor.clicked.connect(self.pick_color_slot)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.colorEditor.setSizePolicy(size_policy)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.colorEditor)
        self.setLayout(layout)

    def pick_color_slot(self):
        color=QColorDialog.getColor()
        if color.isValid():
            self.colorEditor.setText(color.name())

    def setText(self, value):
       self.colorEditor.setText(value)

    def text(self):
        return self.colorEditor.text()



class LabelsTableDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option: QStyleOptionViewItem, index):
        if index.column() == 1:
            editor = ColorPicker(parent)
        else:
            editor = QLineEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setText(value)

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        if index.column() == 1:
            painter.save()
            rect: QRect = option.rect
            val = index.model().data(index)
            painter.setBrush(QColor(val))
            painter.drawRect(QRect(rect.x(), rect.y(), QSize(20, rect.height())))
            painter.restore()
            #super(SpinBoxDelegate,self).paint(painter,option,index)
        else:
            super(LabelsTableDelegate,self).paint(painter,option,index)




    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, Qt.EditRole)

    # def displayText(self, value: typing.Any, locale: QtCore.QLocale) -> str:
    #     print(value)
    #     return str(value)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)





if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    model = QStandardItemModel(4, 2)
    tableView = QTableView()
    tableView.setSelectionBehavior(QAbstractItemView.SelectItems )
    tableView.setSelectionMode(QAbstractItemView.SingleSelection )
    tableView.setCursor(QtCore.Qt.PointingHandCursor)
    model.setHorizontalHeaderLabels(["name", "color"])
    tableView.setModel(model)

    delegate = LabelsTableDelegate()
    tableView.setItemDelegate(delegate)

    for row in range(4):
        #index = model.index(row, 0, QModelIndex())
        model.setData(model.index(row, 0), "cat")
        model.setData(model.index(row,1),"red")

    tableView.setWindowTitle("Spin Box Delegate")
    tableView.show()
    sys.exit(app.exec_())