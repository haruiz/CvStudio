# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'base_dataset_form.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtWidgets


class Ui_Base_DatasetDialog(object):
    def setupUi(self, Base_DatasetDialog):
        Base_DatasetDialog.setObjectName("Base_DatasetDialog")
        Base_DatasetDialog.resize(341, 146)
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
        self.descriptionEditText.setMinimumSize(QtCore.QSize(0, 60))
        self.descriptionEditText.setMaximumSize(QtCore.QSize(16777215, 50))
        self.descriptionEditText.setObjectName("descriptionEditText")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.descriptionEditText)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonsbox = QtWidgets.QDialogButtonBox(Base_DatasetDialog)
        self.buttonsbox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonsbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
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
