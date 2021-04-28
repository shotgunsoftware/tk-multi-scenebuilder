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
        Class constructor.

        :param parent: The parent QWidget for this control
        """

        QtGui.QWidget.__init__(self, parent)

        self._bundle = sgtk.platform.current_bundle()

        # for backwards compatibility, we need to query the entity type that this toolkit uses for its Publishes
        # as well as the field name used for the published file type
        publish_entity_type = sgtk.util.get_published_file_entity_type(
            self._bundle.sgtk
        )
        if publish_entity_type == "PublishedFile":
            self._publish_type_field = "published_file_type"
        else:
            self._publish_type_field = "tank_type"

        # now load in the UI that was created in the UI designer
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        # create a single instance of the task manager that manages all
        # asynchronous work/tasks
        self._bg_task_manager = BackgroundTaskManager(self, max_threads=8)
        self._bg_task_manager.start_processing()
        shotgun_globals.register_bg_task_manager(self._bg_task_manager)

        # create a loader manager using the loader application
        # this manager will be used to perform all the "load" actions
        # this is to ensure that we'll go through the same process than if we'd
        # use the loader app
        current_engine = sgtk.platform.current_engine()
        loader_app = current_engine.apps.get("tk-multi-loader2")
        if not loader_app:
            raise TankError(
                "Please make sure the Loader App is configured for this context."
            )
        self._loader_manager = loader_app.create_loader_manager()

        # get the presets list from the app settings
        presets = self._bundle.get_setting("presets")
        preset_titles = [p["title"] for p in presets]
        self._ui.presets.addItems(preset_titles)

        # finally, create the model used to retrieve the files, and connect it to the view using a custom delegate
        self._model = FileModel(
            self, bg_task_manager=self._bg_task_manager, loader_app=loader_app
        )
        self._ui.view.setModel(self._model)

        self._delegate = FileDelegate(self._ui.view)
        self._ui.view.setItemDelegate(self._delegate)

        self._ui.view.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.ResizeToContents)
        self._ui.view.horizontalHeader().setMinimumSectionSize(0)

        # widget connections
        self._ui.build_button.clicked.connect(self.build_scene)
        self._ui.presets.currentIndexChanged.connect(self._load_model_data)

        # finally load the model data
        self._load_model_data()

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
        """
        Load all the selected files into the current scene.
        The "load" actions are determined by the publish file type and what has been defined inside the configuration
        """

        # collect all the items we're using to build the scene
        items = []
        for row in range(self._model.rowCount()):

            # only load the selected items
            state_item = self._model.item(row, 0)
            if state_item.checkState() == QtCore.Qt.CheckState.Checked:

                sg_data = state_item.data(FileModel.SG_DATA_ROLE)
                action_name = state_item.data(FileModel.ACTION_ROLE)

                items.append({"sg_data": sg_data, "action_name": action_name})

        # then run the pre-build actions, load the files and finally execute the post-build actions
        self._bundle.execute_hook_method("actions_hook", "pre_build_action", items=items)

        for item in items:
            # use the loader manager to perform the load actions
            loader_actions = self._loader_manager.get_actions_for_publish(
                item["sg_data"], self._loader_manager.UI_AREA_MAIN
            )
            for action in loader_actions:
                if action["name"] == item["action_name"]:
                    self._loader_manager.execute_action(item["sg_data"], action)

        self._bundle.execute_hook_method("actions_hook", "post_build_action", items=items)

    def _load_model_data(self):
        """
        Ask the model to refresh its data according to the selected preset
        """
        preset_name = self._ui.presets.currentText()
        self._model.load_data(preset_name)
