# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'base_new_label_form.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_NewLabelDialog(object):
    def setupUi(self, NewLabelDialog):
        NewLabelDialog.setObjectName("NewLabelDialog")
        NewLabelDialog.resize(334, 113)
        self.verticalLayout = QtWidgets.QVBoxLayout(NewLabelDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.nameLabel = QtWidgets.QLabel(NewLabelDialog)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(NewLabelDialog)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameLineEdit)
        self.colorLabel = QtWidgets.QLabel(NewLabelDialog)
        self.colorLabel.setObjectName("colorLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.colorLabel)
        self.colorWidget = QtWidgets.QWidget(NewLabelDialog)
        self.colorWidget.setObjectName("colorWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.colorWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.colorLineEdit = QtWidgets.QLineEdit(self.colorWidget)
        self.colorLineEdit.setEnabled(False)
        self.colorLineEdit.setObjectName("colorLineEdit")
        self.horizontalLayout.addWidget(self.colorLineEdit)
        self.btn_pick_color = QtWidgets.QPushButton(self.colorWidget)
        self.btn_pick_color.setMinimumSize(QtCore.QSize(20, 0))
        self.btn_pick_color.setMaximumSize(QtCore.QSize(40, 16777215))
        self.btn_pick_color.setObjectName("btn_pick_color")
        self.horizontalLayout.addWidget(self.btn_pick_color)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.colorWidget)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(NewLabelDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(NewLabelDialog)
        self.buttonBox.accepted.connect(NewLabelDialog.accept)
        self.buttonBox.rejected.connect(NewLabelDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NewLabelDialog)

    def retranslateUi(self, NewLabelDialog):
        _translate = QtCore.QCoreApplication.translate
        NewLabelDialog.setWindowTitle(_translate("NewLabelDialog", "Dialog"))
        self.nameLabel.setText(_translate("NewLabelDialog", "Name:"))
        self.colorLabel.setText(_translate("NewLabelDialog", "Color:"))
        self.btn_pick_color.setText(_translate("NewLabelDialog", "..."))
