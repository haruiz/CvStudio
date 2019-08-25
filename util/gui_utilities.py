import os

from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtWidgets import QLayout,QGridLayout,QLayoutItem,QMessageBox


class GUIUtilities:
    @staticmethod
    def get_icon(img):
        resource_path=os.path.abspath("./assets/icons/dark/{}".format(img))
        return QIcon(resource_path)

    @staticmethod
    def get_image(img):
        resource_path=os.path.abspath("./assets/icons/dark/{}".format(img))
        return QPixmap(resource_path)

    @staticmethod
    def clear_layout( layout: QLayout):
        while layout.count():
            child=layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    @staticmethod
    def next_cell(grid_layout: QGridLayout)-> tuple:
        cols = grid_layout.columnCount()
        rows = grid_layout.rowCount()
        for r in range(rows):
            for c in range(cols):
                item : QLayoutItem = grid_layout.itemAtPosition(r,c)
                if item is None:
                    return r,c

    @staticmethod
    def show_error_message(message : str,title="Error"):
        msg=QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        # msg.setInformativeText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    @staticmethod
    def show_info_message(message: str, title: str= "Information"):
        msg=QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        # msg.setInformativeText(message)
        msg.setWindowTitle(title)
        msg.exec_()