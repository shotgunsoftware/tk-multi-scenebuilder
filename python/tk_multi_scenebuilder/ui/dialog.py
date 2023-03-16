# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Y:\SGTK\devs\SynologyDrive\tk-multi-scenebuilder\resources\dialog.ui'
#
# Created: Thu Mar 16 11:00:06 2023
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from sgtk.platform.qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1161, 463)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.preset_layout = QtGui.QHBoxLayout()
        self.preset_layout.setObjectName("preset_layout")
        self.preset_label = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.preset_label.sizePolicy().hasHeightForWidth())
        self.preset_label.setSizePolicy(sizePolicy)
        self.preset_label.setObjectName("preset_label")
        self.preset_layout.addWidget(self.preset_label)
        self.presets = QtGui.QComboBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.presets.sizePolicy().hasHeightForWidth())
        self.presets.setSizePolicy(sizePolicy)
        self.presets.setObjectName("presets")
        self.preset_layout.addWidget(self.presets)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.preset_layout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.preset_layout)
        self.view = QtGui.QTreeView(Dialog)
        self.view.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged|QtGui.QAbstractItemView.SelectedClicked)
        self.view.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.view.setObjectName("view")
        self.view.header().setVisible(False)
        self.verticalLayout.addWidget(self.view)
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.button_layout.addItem(spacerItem1)
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
        self.preset_label.setText(QtGui.QApplication.translate("Dialog", "Presets:", None, QtGui.QApplication.UnicodeUTF8))
        self.build_button.setText(QtGui.QApplication.translate("Dialog", "Build", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
