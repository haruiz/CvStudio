import os
import typing

import numpy as np

from PyQt5.QtGui import QIcon, QPixmap, QImage, qRgb
from PyQt5.QtWidgets import QLayout, QGridLayout, QLayoutItem, QMessageBox, QApplication, QMainWindow


class GUIUtilities:
    @staticmethod
    def get_icon(img):
        resource_path = os.path.abspath("./assets/icons/dark/{}".format(img))

        return QIcon(resource_path)

    @staticmethod
    def get_image(img):
        resource_path = os.path.abspath("./assets/icons/dark/{}".format(img))

        return QPixmap(resource_path)

    @staticmethod
    def clear_layout(layout: QLayout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    @staticmethod
    def next_cell(grid_layout: QGridLayout) -> tuple:
        cols = grid_layout.columnCount()
        rows = grid_layout.rowCount()
        for r in range(rows):
            for c in range(cols):
                item: QLayoutItem = grid_layout.itemAtPosition(r, c)
                if item is None:
                    return r, c

    @staticmethod
    def show_error_message(message: str, title="Error"):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    @staticmethod
    def show_info_message(message: str, title: str = "Information"):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    @staticmethod
    def array_to_qimage(im: np.ndarray, copy=False):
        gray_color_table = [qRgb(i, i, i) for i in range(256)]
        if im is None:
            return QImage()
        if im.dtype == np.uint8:
            if len(im.shape) == 2:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
                qim.setColorTable(gray_color_table)
                return qim.copy() if copy else qim

            elif len(im.shape) == 3:
                if im.shape[2] == 3:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888);
                    return qim.copy() if copy else qim
                elif im.shape[2] == 4:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32);
                    return qim.copy() if copy else qim

    @staticmethod
    def findMainWindow() -> typing.Union[QMainWindow, None]:
        # Global function to find the (open) QMainWindow in application
        app = QApplication.instance()
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                return widget

        return None
