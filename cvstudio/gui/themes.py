from pathlib import Path

from cvstudio.pyqt import QPalette, QApplication, QtCore, QColor


def cvstudio_theme(app: QApplication):
    app.setProperty("theme", "cvstudio")
    app.setStyle("Fusion")

    assets_path = Path(__file__).parents[1].joinpath("assets")
    style_sheet = assets_path.joinpath("styles/cvstudio/style.css")
    with open(style_sheet, "r") as f:
        app.setStyleSheet(f.read())
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QPalette.Base, QColor(15, 15, 15))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QPalette.Text, QtCore.Qt.white)
    palette.setColor(QPalette.Button, QColor(20, 20, 20))
    palette.setColor(QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QPalette.Highlight, QColor(169, 3, 252).lighter())
    palette.setColor(QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)
