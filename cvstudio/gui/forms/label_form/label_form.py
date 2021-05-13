from cvstudio.pyqt import (
    QDialog,
    QLineEdit,
    QTextEdit,
    QFormLayout,
    QDialogButtonBox,
    Qt,
    QPushButton,
    QMouseEvent,
    QColorDialog,
    QWidget,
    QHBoxLayout,
    QColor,
    Property,
)

from cvstudio.util import GUIUtils


class QColorEditWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(QColorEditWidget, self).__init__(*args, **kwargs)
        self.layout = QHBoxLayout(self)
        self.txt_color = QLineEdit()
        self.txt_color.setReadOnly(True)
        self.btn_pick_color = QPushButton("...")
        self.btn_pick_color.setFixedWidth(20)
        self.btn_pick_color.setCursor(Qt.PointingHandCursor)
        self.btn_pick_color.clicked.connect(self.pick_color)
        self.layout.addWidget(self.txt_color)
        self.layout.addWidget(self.btn_pick_color)
        self._color = None

    @Property(QColor)
    def color(self):
        return self._color

    def pick_color(self, evt: QMouseEvent) -> None:
        color = QColorDialog.getColor(
            options=QColorDialog.DontUseNativeDialog | QColorDialog.ShowAlphaChannel
        )
        if color.isValid():
            color_name = color.name()
            self.txt_color.setText(color_name)
            self.setStyleSheet(f"background-color: {color_name};")
            self._color = color


class LabelForm(QDialog):
    def __init__(self, parent=None):
        super(LabelForm, self).__init__(parent)
        # self.resize(361, 150)
        window_icon = GUIUtils.get_icon("polygon.png")
        self.setWindowIcon(window_icon)
        self.setWindowTitle("New Label")

        txt_name = QLineEdit()
        txt_name.setObjectName("txt_name")

        color_widget = QColorEditWidget()
        color_widget.setObjectName("color_picker")

        layout = QFormLayout(self)
        layout.addRow(self.tr("Name:"), txt_name)
        layout.addRow(self.tr("Color:"), color_widget)

        buttons_box = QDialogButtonBox()
        buttons_box.setOrientation(Qt.Horizontal)
        buttons_box.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        layout.addWidget(buttons_box)
        buttons_box.accepted.connect(self.accept)
        buttons_box.rejected.connect(self.reject)

    name = GUIUtils.bind("txt_name", "text", str)
    color = GUIUtils.bind("color_picker", "color", QColor)

    def accept(self) -> None:
        if not self.name:
            GUIUtils.show_error_message("Field name is required", "Info")
            return
        return super(LabelForm, self).accept()

    def reject(self) -> None:
        return super(LabelForm, self).reject()
