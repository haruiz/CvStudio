# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'base_repo_form.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_NewRepo(object):
    def setupUi(self, NewRepo):
        NewRepo.setObjectName("NewRepo")
        NewRepo.resize(343, 97)
        self.verticalLayout = QtWidgets.QVBoxLayout(NewRepo)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setContentsMargins(10, 10, 10, 10)
        self.formLayout.setObjectName("formLayout")
        self.nameLabel = QtWidgets.QLabel(NewRepo)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(NewRepo)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameLineEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(NewRepo)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(NewRepo)
        self.buttonBox.accepted.connect(NewRepo.accept)
        self.buttonBox.rejected.connect(NewRepo.reject)
        QtCore.QMetaObject.connectSlotsByName(NewRepo)

    def retranslateUi(self, NewRepo):
        _translate = QtCore.QCoreApplication.translate
        NewRepo.setWindowTitle(_translate("NewRepo", "Dialog"))
        self.nameLabel.setText(_translate("NewRepo", "Name"))
        self.nameLineEdit.setText(_translate("NewRepo", "pytorch/vision"))
