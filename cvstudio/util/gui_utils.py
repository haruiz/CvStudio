import os

import cv2
import numpy as np
from cvstudio.pyqt import (
    QtGui,
    QIcon,
    QImage,
    QPixmap,
    QApplication,
    QLayout,
    QMessageBox,
    qRgb,
)
from pathlib import Path


class GUIUtils:
    @staticmethod
    def get_icon(asset_file_name: str) -> QIcon:
        """
        create an icon instance based on the asset file name
        :rtype: QIcon instance
        """
        assets_folder = Path(__file__).parents[1].joinpath("assets")
        app = QApplication.instance()
        curr_theme = app.property("theme")
        asset_path = assets_folder.joinpath(f"{curr_theme}/icons/{asset_file_name}")
        return QIcon(str(asset_path))

    @staticmethod
    def get_assets_path() -> Path:
        """
        create an icon instance based on the asset file name
        :rtype: QIcon instance
        """
        assets_folder = Path(__file__).parents[1].joinpath("assets")
        app = QApplication.instance()
        curr_theme = app.property("theme")
        asset_path = assets_folder.joinpath(f"{curr_theme}")
        return asset_path

    @classmethod
    def icon_color2gray(cls, icon: QIcon) -> QIcon:
        """
        Convert a rgb icon to gray, like disable effect
        :rtype: object QIcon instance
        """
        pixmap = icon.pixmap(icon.availableSizes()[0])
        img_array = cls.qpixmap2numpy(pixmap)
        *_, alpha = cv2.split(img_array)
        gray_layer = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        gray_img = cv2.merge((gray_layer, gray_layer, gray_layer, alpha))
        height, width, channel = gray_img.shape
        bytes_per_line = 4 * width
        qImg = QImage(
            gray_img.data, width, height, bytes_per_line, QImage.Format_RGBA8888
        )
        pixmap = QtGui.QPixmap.fromImage(qImg)
        return QIcon(pixmap)

    @classmethod
    def qpixmap2numpy(cls, pixmap: QPixmap) -> np.ndarray:
        """
        convert a qpixman into a numpy array
        :rtype: object: numpy array
        """
        image = pixmap.toImage()
        channels_count = 4 if image.hasAlphaChannel() else 3
        width, height = image.width(), image.height()
        buffer = image.bits().asarray(width * height * channels_count)
        arr = np.frombuffer(buffer, dtype=np.uint8).reshape(
            (height, width, channels_count)
        )
        return arr

    @classmethod
    def clear_layout(cls, layout: QLayout):
        """
        clear a pyqt layout
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    @staticmethod
    def show_error_message(message: str, title="Error"):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    @staticmethod
    def show_info_message(message: str, title="Info"):
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
                qim = QImage(
                    im.data,
                    im.shape[1],
                    im.shape[0],
                    im.strides[0],
                    QImage.Format_Indexed8,
                )
                qim.setColorTable(gray_color_table)
                return qim.copy() if copy else qim

            elif len(im.shape) == 3:
                if im.shape[2] == 3:
                    qim = QImage(
                        im.data,
                        im.shape[1],
                        im.shape[0],
                        im.strides[0],
                        QImage.Format_RGB888,
                    )
                    return qim.copy() if copy else qim
                elif im.shape[2] == 4:
                    qim = QImage(
                        im.data,
                        im.shape[1],
                        im.shape[0],
                        im.strides[0],
                        QImage.Format_ARGB32,
                    )
                    return qim.copy() if copy else qim
