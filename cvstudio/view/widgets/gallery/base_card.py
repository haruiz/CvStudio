# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'base_card.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_GalleryCard(object):
    def setupUi(self, GalleryCard):
        GalleryCard.setObjectName("GalleryCard")
        GalleryCard.resize(200, 241)
        self.verticalLayout = QtWidgets.QVBoxLayout(GalleryCard)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.thumbnail_frame = QtWidgets.QFrame(GalleryCard)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.thumbnail_frame.sizePolicy().hasHeightForWidth())
        self.thumbnail_frame.setSizePolicy(sizePolicy)
        self.thumbnail_frame.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.thumbnail_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.thumbnail_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.thumbnail_frame.setObjectName("thumbnail_frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.thumbnail_frame)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.thumbnail_layout = QtWidgets.QVBoxLayout()
        self.thumbnail_layout.setObjectName("thumbnail_layout")
        self.verticalLayout_3.addLayout(self.thumbnail_layout)
        self.verticalLayout.addWidget(self.thumbnail_frame)
        self.text_frame = QtWidgets.QFrame(GalleryCard)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.text_frame.sizePolicy().hasHeightForWidth())
        self.text_frame.setSizePolicy(sizePolicy)
        self.text_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.text_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.text_frame.setObjectName("text_frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.text_frame)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_text = QtWidgets.QLabel(self.text_frame)
        font = QtGui.QFont()
        font.setFamily("MS Gothic")
        font.setPointSize(7)
        self.label_text.setFont(font)
        self.label_text.setText("")
        self.label_text.setAlignment(QtCore.Qt.AlignCenter)
        self.label_text.setObjectName("label_text")
        self.verticalLayout_2.addWidget(self.label_text)
        self.verticalLayout.addWidget(self.text_frame)
        self.buttons_frame = QtWidgets.QFrame(GalleryCard)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.buttons_frame.sizePolicy().hasHeightForWidth())
        self.buttons_frame.setSizePolicy(sizePolicy)
        self.buttons_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.buttons_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.buttons_frame.setObjectName("buttons_frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.buttons_frame)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setObjectName("buttons_layout")
        self.horizontalLayout_3.addLayout(self.buttons_layout)
        self.verticalLayout.addWidget(self.buttons_frame)

        self.retranslateUi(GalleryCard)
        #QtCore.QMetaObject.connectSlotsByName(GalleryCard)

    def retranslateUi(self, GalleryCard):
        _translate = QtCore.QCoreApplication.translate
        GalleryCard.setWindowTitle(_translate("GalleryCard", "Form"))
