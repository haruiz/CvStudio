import mimetypes
from pathlib import Path

from cvstudio.gui.tabs.tab_media.media_grid_item import MediaDataGridItem
from cvstudio.gui.widgets import WidgetsGrid, WidgetsGridCard, ImageButton, ImageDialog
from cvstudio.util import GUIUtils
from cvstudio.pyqt import QtCore, QtGui, QObject, Signal, QSize, QWidget, QLabel
from .hover_label import LabelHovered


class MediaDataGrid(WidgetsGrid, QObject):
    files_dropped = Signal(list)
    item_double_click = Signal(object)
    item_action_click = Signal(str, QWidget)

    def __init__(self, parent=None, ncols=8):
        super(MediaDataGrid, self).__init__(parent, ncols)
        self.setAcceptDrops(True)

    def build(self, data_item: MediaDataGridItem) -> QWidget:
        card = WidgetsGridCard(debug=False)
        if data_item.enabled:
            label_image = LabelHovered()
            label_image.doubleClicked.connect(
                lambda evt: self.item_double_click.emit(card)
            )
            label_image.hoverTimeout.connect(
                lambda: self.show_image(data_item.data_item.file_path)
            )
        else:
            label_image = QLabel()
        label_image.setFixedSize(QSize(150, 150))
        label_image.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        if data_item.thumbnail:
            label_image.setPixmap(data_item.thumbnail)
        card.body = label_image
        card.title.setText(data_item.title)
        card.setProperty("data", data_item)
        card.subtitle.setText(data_item.subtitle)

        btn_delete = ImageButton(GUIUtils.get_icon("delete.png"), size=QSize(15, 15))
        btn_delete.setToolTip("Delete dataset")
        btn_delete.clicked.connect(
            lambda evt: self.item_action_click.emit("delete", card)
        )

        btn_edit = ImageButton(GUIUtils.get_icon("annotations.png"), size=QSize(15, 15))
        btn_edit.setToolTip("Annotate")
        btn_edit.clicked.connect(lambda evt: self.item_action_click.emit("edit", card))

        card.add_actions([btn_delete, btn_edit])
        btn_edit.setEnabled(data_item.enabled)
        return card

    def show_image(self, file_path):
        viewer = ImageDialog(file_path)
        viewer.exec_()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        data = event.mimeData()
        if data.hasUrls():
            if any(url.isLocalFile() for url in data.urls()):
                event.accept()
                return
        else:
            event.ignore()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            return
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        valid_files = []
        files = [Path(u.toLocalFile()) for u in event.mimeData().urls()]
        for f in files:
            if f.is_file():
                mime_type, encoding = mimetypes.guess_type(str(f))
                if mime_type.find("image") != -1:
                    valid_files.append(f)
        valid_files = sorted(valid_files, key=lambda f: f.name)
        self.files_dropped.emit(valid_files)
