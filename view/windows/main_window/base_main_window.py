# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'base_main_window.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(997, 795)
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_lateral_bar = QtWidgets.QFrame(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_lateral_bar.sizePolicy().hasHeightForWidth())
        self.frame_lateral_bar.setSizePolicy(sizePolicy)
        self.frame_lateral_bar.setMinimumSize(QtCore.QSize(80, 0))
        self.frame_lateral_bar.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_lateral_bar.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_lateral_bar.setObjectName("frame_lateral_bar")
        self.horizontalLayout.addWidget(self.frame_lateral_bar)
        self.tab_widget_manager = QtWidgets.QTabWidget(self.widget)
        self.tab_widget_manager.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tab_widget_manager.setDocumentMode(False)
        self.tab_widget_manager.setTabsClosable(True)
        self.tab_widget_manager.setTabBarAutoHide(False)
        self.tab_widget_manager.setObjectName("tab_widget_manager")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tab_widget_manager.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tab_widget_manager.addTab(self.tab_2, "")
        self.horizontalLayout.addWidget(self.tab_widget_manager)
        self.verticalLayout.addWidget(self.widget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 997, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tab_widget_manager.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tab_widget_manager.setTabText(self.tab_widget_manager.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.tab_widget_manager.setTabText(self.tab_widget_manager.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
