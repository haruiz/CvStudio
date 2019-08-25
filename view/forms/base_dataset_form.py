# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'base_dataset_form.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Base_DatasetDialog(object):
    def setupUi(self, Base_DatasetDialog):
        Base_DatasetDialog.setObjectName("Base_DatasetDialog")
        Base_DatasetDialog.resize(357, 212)
        self.verticalLayout = QtWidgets.QVBoxLayout(Base_DatasetDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.nameLabel = QtWidgets.QLabel(Base_DatasetDialog)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(Base_DatasetDialog)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameLineEdit)
        self.label = QtWidgets.QLabel(Base_DatasetDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.descriptionEditText = QtWidgets.QPlainTextEdit(Base_DatasetDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.descriptionEditText.sizePolicy().hasHeightForWidth())
        self.descriptionEditText.setSizePolicy(sizePolicy)
        self.descriptionEditText.setMinimumSize(QtCore.QSize(0, 100))
        self.descriptionEditText.setMaximumSize(QtCore.QSize(16777215, 100))
        self.descriptionEditText.setObjectName("descriptionEditText")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.descriptionEditText)
        self.typeLabel = QtWidgets.QLabel(Base_DatasetDialog)
        self.typeLabel.setObjectName("typeLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.typeLabel)
        self.typeComboBox = QtWidgets.QComboBox(Base_DatasetDialog)
        self.typeComboBox.setObjectName("typeComboBox")
        self.typeComboBox.addItem("")
        self.typeComboBox.addItem("")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.typeComboBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonsbox = QtWidgets.QDialogButtonBox(Base_DatasetDialog)
        self.buttonsbox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonsbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonsbox.setObjectName("buttonsbox")
        self.verticalLayout.addWidget(self.buttonsbox)

        self.retranslateUi(Base_DatasetDialog)
        self.buttonsbox.accepted.connect(Base_DatasetDialog.accept)
        self.buttonsbox.rejected.connect(Base_DatasetDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Base_DatasetDialog)

    def retranslateUi(self, Base_DatasetDialog):
        _translate = QtCore.QCoreApplication.translate
        Base_DatasetDialog.setWindowTitle(_translate("Base_DatasetDialog", "Dialog"))
        self.nameLabel.setText(_translate("Base_DatasetDialog", "Name:"))
        self.label.setText(_translate("Base_DatasetDialog", "Description:"))
        self.typeLabel.setText(_translate("Base_DatasetDialog", "type:"))
        self.typeComboBox.setItemText(0, _translate("Base_DatasetDialog", "Images"))
        self.typeComboBox.setItemText(1, _translate("Base_DatasetDialog", "Videos"))
