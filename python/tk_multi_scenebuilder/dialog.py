# Copyright (c) 2021 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk import TankError
from sgtk.platform.qt import QtGui, QtCore

from .ui.dialog import Ui_Dialog
from .model import FileModel
from .delegate import FileDelegate

task_manager = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "task_manager"
)
BackgroundTaskManager = task_manager.BackgroundTaskManager

shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_globals"
)


class AppDialog(QtGui.QWidget):
    def __init__(self, parent=None):
        """
        :param parent: The parent QWidget for this control
        """

        QtGui.QWidget.__init__(self, parent)

        self._bundle = sgtk.platform.current_bundle()

        # now load in the UI that was created in the UI designer
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        # create a single instance of the task manager that manages all
        # asynchronous work/tasks
        self._bg_task_manager = BackgroundTaskManager(self, max_threads=8)
        self._bg_task_manager.start_processing()

        current_engine = sgtk.platform.current_engine()
        loader_app = current_engine.apps.get("tk-multi-loader2")
        if not loader_app:
            raise TankError(
                "Please make sure the Loader App is configured for this context."
            )
        self._loader_manager = loader_app.create_loader_manager()

        shotgun_globals.register_bg_task_manager(self._bg_task_manager)

        self._model = FileModel(
            self, bg_task_manager=self._bg_task_manager, loader_app=loader_app
        )
        self._ui.view.setModel(self._model)

        self._delegate = FileDelegate(self._ui.view)
        self._ui.view.setItemDelegate(self._delegate)

        self._ui.view.resizeColumnsToContents()
        self._ui.view.horizontalHeader().setStretchLastSection(True)
        self._ui.view.setColumnWidth(1, 96)
        self._ui.view.setColumnWidth(2, 150)

        self._ui.build_button.clicked.connect(self.test_fn)

    def closeEvent(self, event):
        """
        Overriden method triggered when the widget is closed.  Cleans up as much as possible
        to help the GC.

        :param event: Close event
        """

        # and shut down the task manager
        if self._bg_task_manager:
            shotgun_globals.unregister_bg_task_manager(self._bg_task_manager)
            self._bg_task_manager.shut_down()
            self._bg_task_manager = None

        return QtGui.QWidget.closeEvent(self, event)

    def test_fn(self):
        """
        :return:
        """
        self._bundle.logger.info(
            "[DEBUG BARBARA] columnCount: {}".format(self._model.columnCount())
        )
        self._bundle.logger.info(
            "[DEBUG BARBARA] rowCount: {}".format(self._model.rowCount())
        )
