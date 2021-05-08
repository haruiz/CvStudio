from hurry.filesize import size, alternative
from cvstudio.gui.widgets import WidgetsGrid, WidgetsGridCard, ImageButton
from cvstudio.util import GUIUtils
from cvstudio.vo import DatasetVO
from cvstudio.pyqt import Signal, QObject, QWidget, QSize


class DatasetsGrid(WidgetsGrid, QObject):
    item_action_click = Signal(str, QWidget)
    item_double_click = Signal(QWidget)

    def __init__(self, parent=None, ncols=8):
        super(DatasetsGrid, self).__init__(parent, ncols)

    def build(self, data_item: DatasetVO) -> QWidget:
        card = WidgetsGridCard(debug=False)
        icon_file = "folder_empty.png"
        icon = GUIUtils.get_icon(icon_file)
        card.body = ImageButton(icon)
        card.title = f"{data_item.name}"
        card.tag = data_item
        label_size = (
            size(data_item.size, system=alternative) if data_item.size else "0 MB"
        )
        card.subtitle = f"{data_item.count} files " f"\n ({label_size})"
        btn_delete = ImageButton(GUIUtils.get_icon("delete.png"), size=QSize(15, 15))
        btn_delete.setToolTip("Delete dataset")
        btn_delete.clicked.connect(
            lambda evt: self.item_action_click.emit("delete", card)
        )

        btn_edit = ImageButton(GUIUtils.get_icon("edit.png"), size=QSize(15, 15))
        btn_edit.setToolTip("Edit dataset")
        btn_edit.clicked.connect(lambda evt: self.item_action_click.emit("edit", card))

        btn_refresh = ImageButton(GUIUtils.get_icon("refresh.png"), size=QSize(15, 15))
        btn_refresh.setToolTip("Refresh dataset")
        btn_refresh.clicked.connect(
            lambda evt: self.item_action_click.emit("refresh", card)
        )

        icon = GUIUtils.get_icon("download.png")
        btn_export_annotations = ImageButton(icon, size=QSize(15, 15))
        btn_export_annotations.setToolTip("Export annotations")
        btn_export_annotations.clicked.connect(
            lambda evt: self.item_action_click.emit("export", card)
        )

        icon = GUIUtils.get_icon("upload.png")
        btn_import_annotations = ImageButton(icon, size=QSize(15, 15))
        btn_import_annotations.setToolTip("Import annotations")
        btn_import_annotations.clicked.connect(
            lambda evt: self.item_action_click.emit("import", card)
        )

        card.add_actions(
            [
                btn_delete,
                btn_edit,
                btn_refresh,
                btn_export_annotations,
                btn_import_annotations,
            ]
        )
        card.body.doubleClicked.connect(lambda evt: self.item_double_click.emit(card))
        return card
