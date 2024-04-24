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
from sgtk.platform.qt import QtGui, QtCore

from .ui.dialog import Ui_Dialog
from .model import FileModel
from .delegate import create_file_delegate

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
        Class constructor.

        :param parent: The parent QWidget for this control
        """

        QtGui.QWidget.__init__(self, parent)

        self._bundle = sgtk.platform.current_bundle()

        # create a loader manager using the loader application
        # this manager will be used to perform all the "load" actions
        # this is to ensure that we'll go through the same process than if we'd
        # use the loader app
        current_engine = sgtk.platform.current_engine()
        loader_app = current_engine.apps.get("tk-multi-loader2")
        if not loader_app:
            self._bundle.logger.error(
                "Please make sure the Loader App is configured for this context."
            )
            return
        self._loader_manager = loader_app.create_loader_manager()

        # create a breakdown manager using the breakdown2 application
        # this manager will be used to scan the current scene and update references
        breakdown_app = current_engine.apps.get("tk-multi-breakdown2")
        if not breakdown_app:
            self._bundle.logger.error(
                "Please make sure the Breakdown2 App is configured for this context."
            )
            return
        self._breakdown_manager = breakdown_app.create_breakdown_manager()

        # now load in the UI that was created in the UI designer
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        # create a single instance of the task manager that manages all
        # asynchronous work/tasks
        self._bg_task_manager = BackgroundTaskManager(self, max_threads=8)
        self._bg_task_manager.start_processing()
        shotgun_globals.register_bg_task_manager(self._bg_task_manager)

        # get the presets list from the app settings
        presets = self._bundle.get_setting("presets")
        preset_names = [p["name"] for p in presets]
        self._ui.presets.addItems(preset_names)

        # finally, create the model used to retrieve the files, and connect it to the view using a custom delegate
        self._model = FileModel(
            self,
            bg_task_manager=self._bg_task_manager,
            loader_app=loader_app,
            breakdown_manager=self._breakdown_manager,
        )
        self._ui.view.setModel(self._model)
        self._model.data_loaded.connect(lambda v=self._ui.view: v.expandAll())

        self._delegate = create_file_delegate(self._ui.view)
        self._ui.view.setItemDelegate(self._delegate)

        # # widget connections
        self._ui.build_button.clicked.connect(self.build_scene)
        self._ui.presets.currentIndexChanged.connect(
            lambda idx: self._model.load_data(self._ui.presets.itemText(idx))
        )

        # finally load the model data
        self._model.load_data(self._ui.presets.currentText())

    def closeEvent(self, event):
        """
        Overriden method triggered when the widget is closed. Cleans up as much as possible
        to help the GC.

        :param event: Close event
        """

        # clear up the data model
        if self._model:
            self._model.destroy()

        # shut down the task manager
        if self._bg_task_manager:
            shotgun_globals.unregister_bg_task_manager(self._bg_task_manager)
            self._bg_task_manager.shut_down()
            self._bg_task_manager = None

        return QtGui.QWidget.closeEvent(self, event)

    def build_scene(self):
        """"""

        items_to_process = []
        hook_data = []
        items_to_be_deleted = []

        # collect all the items that are going to be processed at build time
        for row in range(self._model.rowCount()):

            group_item = self._model.item(row, 0)

            # for the files already up-to-date, we don't need to do anything
            if group_item.data(FileModel.STATUS_ROLE) == FileModel.STATUS_UP_TO_DATE:
                continue

            for sub_row in range(group_item.rowCount()):

                idx = self._model.index(sub_row, 0, parent=group_item.index())
                file_item = self._model.itemFromIndex(idx)

                # if we're dealing with the missing files, we just want to collect all of them to pass the list
                # to a hook at build time
                if group_item.data(FileModel.STATUS_ROLE) == FileModel.STATUS_INVALID:
                    items_to_be_deleted.append(
                        {
                            "sg_data": file_item.data(FileModel.SG_DATA_ROLE),
                        }
                    )

                else:

                    if file_item.data(QtCore.Qt.CheckStateRole) != QtCore.Qt.Checked:
                        continue

                    items_to_process.append(file_item)
                    hook_data.append(
                        {
                            "sg_data": file_item.data(FileModel.SG_DATA_ROLE),
                            "status": file_item.data(FileModel.STATUS_ROLE),
                            "action_name": file_item.data(FileModel.ACTION_ROLE),
                        }
                    )

        # now, it's time to launch the build process!
        self._bundle.execute_hook_method(
            "actions_hook", "pre_build_action", items=hook_data
        )

        actions_to_execute = []
        for item in items_to_process:
            if item.data(FileModel.STATUS_ROLE) == FileModel.STATUS_NOT_LOADED:
                # the file has not been loaded yet, we want to do it!
                sg_data = item.data(FileModel.SG_DATA_ROLE)
                action_name = item.data(FileModel.ACTION_ROLE)
                loader_actions = self._loader_manager.get_actions_for_publish(
                    sg_data, self._loader_manager.UI_AREA_MAIN
                )
                for action in loader_actions:
                    if action["name"] == action_name:
                        action["sg_publish_data"] = sg_data
                        actions_to_execute.append(action)
                        break
            elif item.data(FileModel.STATUS_ROLE) == FileModel.STATUS_OUTDATED:
                # the file has already been loaded, we want to update to its latest version
                scene_obj = item.data(FileModel.BREAKDOWN_DATA_ROLE)
                self._breakdown_manager.get_latest_published_file(scene_obj)
                self._breakdown_manager.update_to_latest_version(scene_obj)

        # execute all the actions
        self._loader_manager.execute_multiple_actions(actions_to_execute)
        # update the item status now that it is has been loaded/updated
        for item in items_to_process:
            self._model.set_status(item, status=FileModel.STATUS_UP_TO_DATE)

        self._bundle.execute_hook_method(
            "actions_hook", "process_missing_files", items=items_to_be_deleted
        )
        self._bundle.execute_hook_method(
            "actions_hook", "post_build_action", items=hook_data
        )

        self._ui.view.expandAll()
