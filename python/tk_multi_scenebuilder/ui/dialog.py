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
        self.best_matching_step_only = QtGui.QCheckBox(Dialog)
        self.best_matching_step_only.setObjectName("best_matching_step_only")
        self.preset_layout.addWidget(self.best_matching_step_only)
        self.verticalLayout.addLayout(self.preset_layout)
        self.filter_layout = QtGui.QHBoxLayout()
        self.filter_layout.setObjectName("filter_layout")
        self.filter = QtGui.QLineEdit(Dialog)
        self.filter.setClearButtonEnabled(True)
        self.filter.setObjectName("filter")
        self.filter_layout.addWidget(self.filter)
        self.check_all_button = QtGui.QPushButton(Dialog)
        self.check_all_button.setObjectName("check_all_button")
        self.filter_layout.addWidget(self.check_all_button)
        self.uncheck_all_button = QtGui.QPushButton(Dialog)
        self.uncheck_all_button.setObjectName("uncheck_all_button")
        self.filter_layout.addWidget(self.uncheck_all_button)
        self.verticalLayout.addLayout(self.filter_layout)
        self.view = QtGui.QTreeView(Dialog)
        self.view.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged|QtGui.QAbstractItemView.SelectedClicked)
        self.view.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.view.setObjectName("view")
        self.view.header().setVisible(False)
        self.verticalLayout.addWidget(self.view)
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        self.selection_label = QtGui.QLabel(Dialog)
        self.selection_label.setObjectName("selection_label")
        self.button_layout.addWidget(self.selection_label)
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
        self.best_matching_step_only.setToolTip(QtGui.QApplication.translate("Dialog", "For each entity, only show the files of the preferred upstream step that has files. When unchecked, the files of the other upstream steps are shown unchecked.", None, QtGui.QApplication.UnicodeUTF8))
        self.best_matching_step_only.setText(QtGui.QApplication.translate("Dialog", "Best matching step only", None, QtGui.QApplication.UnicodeUTF8))
        self.filter.setPlaceholderText(QtGui.QApplication.translate("Dialog", "Filter by entity, name, type or task", None, QtGui.QApplication.UnicodeUTF8))
        self.check_all_button.setToolTip(QtGui.QApplication.translate("Dialog", "Check the visible files", None, QtGui.QApplication.UnicodeUTF8))
        self.check_all_button.setText(QtGui.QApplication.translate("Dialog", "Check All", None, QtGui.QApplication.UnicodeUTF8))
        self.uncheck_all_button.setToolTip(QtGui.QApplication.translate("Dialog", "Uncheck the visible files", None, QtGui.QApplication.UnicodeUTF8))
        self.uncheck_all_button.setText(QtGui.QApplication.translate("Dialog", "Uncheck All", None, QtGui.QApplication.UnicodeUTF8))
        self.build_button.setText(QtGui.QApplication.translate("Dialog", "Build", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
