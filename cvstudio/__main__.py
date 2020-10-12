import sys

from cvstudio.dao import create_tables
from cvstudio.gui import cvstudio_theme
from cvstudio.gui.windows import MainWindow
from cvstudio.pyqt import QApplication
from cvstudio.util import GUIUtils


def main():
    try:
        create_tables(False)
        app = QApplication(sys.argv)
        cvstudio_theme(app)
        main_window = MainWindow()
        icon = GUIUtils.get_icon("polygon.png")
        main_window.setWindowIcon(icon)
        main_window.show()
        sys.exit(app.exec_())
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()
