import os
import typing

import numpy as np

from PyQt5.QtGui import QIcon, QPixmap, QImage, qRgb
from PyQt5.QtWidgets import QLayout,QGridLayout,QLayoutItem,QMessageBox,QApplication,QMainWindow,QVBoxLayout,QGroupBox, \
    QFileDialog,QDialog,QAbstractItemView,QListView,QTreeView


class GUIUtilities:
    @staticmethod
    def get_icon(img):
        app = QApplication.instance()
        curr_theme = "light"
        if app:
            curr_theme = app.property("theme")
        resource_path = os.path.abspath("./assets/icons/{}/{}".format(curr_theme, img))

        return QIcon(resource_path)

    @staticmethod
    def get_image(img):
        app=QApplication.instance()
        curr_theme="light"
        if app:
            curr_theme=app.property("theme")
        resource_path = os.path.abspath("./assets/icons/{}/{}".format(curr_theme, img))
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

    @staticmethod
    def wrap_with_groupbox(widget,widget_title):
        groupbox=QGroupBox()
        groupbox.setTitle(widget_title)
        vlayout=QVBoxLayout()
        vlayout.addWidget(widget)
        groupbox.setLayout(vlayout)
        return groupbox

    @staticmethod
    def select_folders():
        file_dialog=QFileDialog()
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog,True)
        file_view=file_dialog.findChild(QListView,'listView')
        if file_view:
            file_view.setSelectionMode(QAbstractItemView.MultiSelection)
        f_tree_view=file_dialog.findChild(QTreeView)
        if f_tree_view:
            f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
        paths=[]
        if file_dialog.exec() == QDialog.Accepted:
            paths=file_dialog.selectedFiles()
        return paths

    @staticmethod
    def select_folder(parent=None,title="select the folder"):
        return str(QFileDialog.getExistingDirectory(None,title))

    @staticmethod
    def select_file(ext,title="select the file",parent=None):
        options=QFileDialog.Options()
        options|=QFileDialog.DontUseNativeDialog
        ext="{} Files (*{})".format(ext,ext) if isinstance(ext,str) else ";;".join(
            list(map(lambda e: "{} Files (*.{})".format(e,e),ext)))
        path,_=QFileDialog.getOpenFileName(parent,title,os.path.join(os.path.expanduser('~')),ext,options=options)
        return path

    @staticmethod
    def select_files(ext,title="select the file",parent=None):
        options=QFileDialog.Options()
        options|=QFileDialog.DontUseNativeDialog
        ext="{} Files (*{})".format(ext,ext) if isinstance(ext,str) else ";;".join(
            list(map(lambda e: "{} Files (*.{})".format(e,e),ext)))
        files,_=QFileDialog.getOpenFileNames(parent,title,os.path.join(os.path.expanduser('~')),ext,options=options)
        return files