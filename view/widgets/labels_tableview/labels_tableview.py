from PyQt5 import QtCore
from PyQt5.QtCore import QObject,QSize,pyqtSignal,QModelIndex,QThreadPool,QRect
from PyQt5.QtGui import QStandardItemModel,QContextMenuEvent,QIcon,QStandardItem,QPainter,QColor,QMouseEvent
from PyQt5.QtWidgets import QTreeView,QLabel,QAction,QMenu,QAbstractItemView,QTableView,QHeaderView,QWidget, \
    QStyleOptionViewItem,QStyledItemDelegate,QLineEdit,QVBoxLayout,QSizePolicy,QColorDialog

from util import GUIUtilities
from view.widgets.common import CustomModel,CustomNode
from view.widgets.common.treeview_model import WidgetDelegate
from view.widgets.loading_dialog import QLoadingDialog
from vo import LabelVO


class ClickableLineEdit(QLineEdit, QObject):
    clicked = pyqtSignal()
    def __init__(self, parent=None):
        super(ClickableLineEdit, self).__init__(parent)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
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
        value = index.model().data(index, QtCore.Qt.EditRole)
        editor.setText(value)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        if index.column() == 1:
            painter.save()
            rect: QRect = option.rect
            val = index.model().data(index)
            painter.setBrush(QColor(val))
            #painter.drawRect(QRect(rect.topLeft(),QSize(20,rect.height())))
            painter.drawRect(rect)
            painter.restore()
            #super(SpinBoxDelegate,self).paint(painter,option,index)
        else:
            super(LabelsTableDelegate,self).paint(painter,option,index)

    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class LabelsTableView(QTableView,QObject):
    action_click=pyqtSignal(QAction)
    CTX_MENU_ADD_LABEL="Add Label"
    CTX_MENU_DELETE_LABEL="Delete Label"
    def __init__(self, parent=None):
        super(LabelsTableView,self).__init__(parent)
        self._model=QStandardItemModel(0,3)
        self._model.setHorizontalHeaderLabels(["name","color"])
        self.setModel(self._model)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        delegate=LabelsTableDelegate()
        self.setItemDelegate(delegate)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        header=self.horizontalHeader()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header.setSectionResizeMode(0,QHeaderView.Stretch)
        header.setSectionResizeMode(1,QHeaderView.Stretch)
        self.setColumnHidden(2,True)

    def add_row(self,vo: LabelVO):
        row = self._model.rowCount(QModelIndex())
        self._model.insertRow(row)
        self._model.setData(self._model.index(row,0),vo.name)
        self._model.setData(self._model.index(row,1),vo.color)
        self._model.setData(self._model.index(row,2),vo)


    def contextMenuEvent(self, evt: QContextMenuEvent) -> None:
        menu=QMenu()
        menu.triggered.connect(self.context_menu_actions_handler)
        index: QModelIndex = self.indexAt(evt.pos())
        if index.isValid():
            icon: QIcon=GUIUtilities.get_icon('delete_label.png')
            action=menu.addAction(icon,self.CTX_MENU_DELETE_LABEL)
            action.setData(index)
        else:
            icon: QIcon=GUIUtilities.get_icon('new_label.png')
            menu.addAction(icon,self.CTX_MENU_ADD_LABEL)
        menu.exec_(self.mapToGlobal(evt.pos()))

    def context_menu_actions_handler(self, action: QAction):
        self.action_click.emit(action)



