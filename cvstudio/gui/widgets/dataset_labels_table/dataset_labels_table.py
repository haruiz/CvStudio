from cvstudio.dao import LabelDao
from cvstudio.vo import LabelVO
from cvstudio.decor import gui_exception, work_exception
from cvstudio.gui.forms import LabelForm
from cvstudio.pyqt import (
    QtCore,
    QObject,
    Signal,
    QModelIndex,
    QRect,
    QStandardItemModel,
    QContextMenuEvent,
    QPainter,
    QColor,
    QMouseEvent,
    QAction,
    QMenu,
    QAbstractItemView,
    QTableView,
    QHeaderView,
    QWidget,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QLineEdit,
    QVBoxLayout,
    QSizePolicy,
    QColorDialog,
    QThreadPool,
    QDialog,
    QMessageBox,
)
from cvstudio.util import GUIUtils, Worker


class ClickableLineEdit(QLineEdit, QObject):
    clicked = Signal()

    def __init__(self, parent=None):
        super(ClickableLineEdit, self).__init__(parent)

    def mousePressEvent(self, evt: QMouseEvent) -> None:
        self.clicked.emit()


class ColorPicker(QWidget):
    def __init__(self, parent=None):
        super(ColorPicker, self).__init__(parent)
        layout = QVBoxLayout()
        self.colorEditor = ClickableLineEdit(parent)
        self.colorEditor.setReadOnly(True)
        self.colorEditor.setCursor(QtCore.Qt.PointingHandCursor)
        self.colorEditor.clicked.connect(self.pick_color_slot)
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.colorEditor.setSizePolicy(size_policy)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.colorEditor)
        self.setLayout(layout)

    def pick_color_slot(self):
        color = QColorDialog.getColor()
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

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QtCore.QModelIndex
    ) -> None:
        if index.column() == 1:
            painter.save()
            rect: QRect = option.rect
            val = index.model().data(index)
            painter.setBrush(QColor(val))
            # painter.drawRect(QRect(rect.topLeft(),QSize(20,rect.height())))
            painter.drawRect(rect)
            painter.restore()
            # super(SpinBoxDelegate,self).paint(painter,option,index)
        else:
            super(LabelsTableDelegate, self).paint(painter, option, index)

    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class DatasetLabelsTable(QTableView, QObject):
    def __init__(self, dataset_id, *args, **kwargs):
        super(DatasetLabelsTable, self).__init__(*args, **kwargs)
        self._model = QStandardItemModel(0, 3)
        self._model.setHorizontalHeaderLabels(["name", "color"])
        self.setModel(self._model)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        delegate = LabelsTableDelegate()
        self.setItemDelegate(delegate)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        header = self.horizontalHeader()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.setColumnHidden(2, True)
        self._dataset_id = dataset_id
        self._labels_dao = LabelDao()
        self._thread_pool = QThreadPool()
        self.load_data()

    def add_row(self, label_id, label_name, label_color):
        row = self._model.rowCount(QModelIndex())
        self._model.insertRow(row)
        self._model.setData(self._model.index(row, 0), label_name)
        self._model.setData(self._model.index(row, 1), label_color)
        self._model.setData(self._model.index(row, 2), label_id)

    @gui_exception
    def load_data(self):
        @work_exception
        def do_work():
            labels = self._labels_dao.fetch_all(self._dataset_id)
            return labels, None

        @gui_exception
        def done_work(args):
            labels, error = args
            if error:
                raise error
            for lbl_vo in labels:
                self.add_row(lbl_vo.id, lbl_vo.name, lbl_vo.color)

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)

    def contextMenuEvent(self, evt: QContextMenuEvent) -> None:
        menu = QMenu()
        index: QModelIndex = self.indexAt(evt.pos())
        icon = GUIUtils.get_icon("new_label.png")
        new_label_action = QAction(icon, "New Label")
        icon = GUIUtils.get_icon("delete_label.png")
        delete_label_action = QAction(icon, "Delete Label")
        if index.isValid():
            menu.addAction(delete_label_action)
        else:
            menu.addAction(new_label_action)
        clicked_action = menu.exec_(self.mapToGlobal(evt.pos()))
        if clicked_action == new_label_action:
            form = LabelForm()
            if form.exec_() == QDialog.Accepted:
                color_vo = LabelVO()
                color_vo.dataset = self._dataset_id
                color_vo.name = form.name
                color_vo.color = form.color.name()
                color_vo = self._labels_dao.save(color_vo)
                self.add_row(color_vo.id, color_vo.name, color_vo.color)
        elif clicked_action == delete_label_action:
            reply = QMessageBox.question(
                self,
                "Delete Label",
                "Are you sure?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                label_id = self._model.index(index.row(), 2).data()
                self._labels_dao.delete(label_id)
                self._model.removeRow(index.row())
                # TODO: Delete annotation for this label
