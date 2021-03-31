# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Y:\SGTK\devs\tk-multi-scenebuilder\resources\dialog.ui'
#
# Created: Tue Mar 30 16:17:33 2021
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from sgtk.platform.qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1161, 463)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.view = QtGui.QTableView(Dialog)
        self.view.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged|QtGui.QAbstractItemView.SelectedClicked)
        self.view.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.view.setShowGrid(False)
        self.view.setObjectName("view")
        self.view.horizontalHeader().setVisible(False)
        self.view.verticalHeader().setVisible(False)
        self.view.verticalHeader().setDefaultSectionSize(75)
        self.verticalLayout.addWidget(self.view)
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        self.build_button = QtGui.QPushButton(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.build_button.sizePolicy().hasHeightForWidth())
        self.build_button.setSizePolicy(sizePolicy)
        self.build_button.setObjectName("build_button")
        self.button_layout.addWidget(self.build_button)
        self.verticalLayout.addLayout(self.button_layout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.build_button.setText(QtGui.QApplication.translate("Dialog", "Build!", None, QtGui.QApplication.UnicodeUTF8))

