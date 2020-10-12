from hurry.filesize import size, alternative
from cvstudio.gui.widgets import WidgetsGrid, WidgetsGridCard, ImageButton
from cvstudio.util import GUIUtils
from cvstudio.vo import DatasetVO
from cvstudio.pyqt import Signal, QObject, QWidget, QSize


class DatasetsGrid(WidgetsGrid, QObject):
    action_signal = Signal(str, DatasetVO)
    double_click_action_signal = Signal(DatasetVO)

    def __init__(self, parent=None, ncols=8):
        super(DatasetsGrid, self).__init__(parent, ncols)

    def create_widget(self, item: DatasetVO) -> QWidget:
        card = WidgetsGridCard(debug=False)
        icon_file = "folder_empty.png"
        icon = GUIUtils.get_icon(icon_file)
        card.body = ImageButton(icon)
        card.label = "{}".format(item.name)
        card.label2 = "{} files \n {} ".format(
            item.count,
            size(item.size, system=alternative) if item.size else "0 MB"
        )
        btn_delete = ImageButton(GUIUtils.get_icon("delete.png"), size=QSize(15, 15))
        btn_delete.setToolTip("Delete dataset")
        btn_edit = ImageButton(GUIUtils.get_icon("edit.png"), size=QSize(15, 15))
        btn_edit.setToolTip("Edit dataset")
        btn_refresh = ImageButton(GUIUtils.get_icon("refresh.png"), size=QSize(15, 15))
        btn_refresh.setToolTip("Refresh dataset")
        btn_export_annotations = ImageButton(
            GUIUtils.get_icon("download.png"), size=QSize(15, 15)
        )
        btn_export_annotations.setToolTip("Export annotations")
        btn_import_annotations = ImageButton(
            GUIUtils.get_icon("upload.png"), size=QSize(15, 15)
        )
        btn_import_annotations.setToolTip("Import annotations")
        card.add_buttons(
            [
                btn_delete,
                btn_edit,
                btn_refresh,
                btn_export_annotations,
                btn_import_annotations,
            ]
        )
        btn_delete.clicked.connect(lambda: self.action_signal.emit("delete", item))
        btn_edit.clicked.connect(lambda: self.action_signal.emit("edit", item))
        btn_refresh.clicked.connect(lambda: self.action_signal.emit("refresh", item))
        btn_export_annotations.clicked.connect(
            lambda: self.action_signal.emit("export_annotations", item)
        )
        btn_import_annotations.clicked.connect(
            lambda: self.action_signal.emit("import_annotations", item)
        )
        card.body.doubleClicked.connect(lambda evt: self.double_click_action_signal.emit(item))
        return card
