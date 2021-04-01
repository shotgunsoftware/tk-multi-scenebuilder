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
from sgtk.platform.qt import QtCore, QtGui

shotgun_model = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_model"
)
ShotgunModel = shotgun_model.ShotgunModel


class FileModel(ShotgunModel):
    """
    """

    STATE_ROLE = QtCore.Qt.UserRole + 32

    def __init__(self, parent, bg_task_manager, loader_app):
        """
        Class constructor

        :param parent:          The parent QObject for this instance
        :param bg_task_manager: A BackgroundTaskManager instance that will be used for all background/threaded
                                work that needs undertaking
        """

        ShotgunModel.__init__(self, parent, bg_task_manager=bg_task_manager)

        app = sgtk.platform.current_bundle()
        publish_entity_type = sgtk.util.get_published_file_entity_type(app.sgtk)

        if publish_entity_type == "PublishedFile":
            self._publish_type_field = "published_file_type"
        else:
            self._publish_type_field = "tank_type"

        # make sure we have all the Shotgun fields required by the Loader app
        fields = loader_app.import_module(
            "tk_multi_loader.constants"
        ).PUBLISHED_FILES_FIELDS + [self._publish_type_field]
        filters = [["entity.Asset.parents", "in", app.context.entity]]

        # get the right context according to the app setting
        context = app.get_setting("context")
        filters.append(["task.Task.content", "is", context["task"]])
        filters.append(["task.Task.step.Step.code", "is", context["step"]])

        publish_type = app.get_setting("publish_type")
        filters.append(
            [
                "{}.PublishedFileType.code".format(self._publish_type_field),
                "is",
                publish_type,
            ]
        )

        ShotgunModel._load_data(
            self,
            entity_type=publish_entity_type,
            filters=filters,
            hierarchy=["id"],
            order=[{"field_name": "version_number", "direction": "desc"}],
            fields=fields,
            columns=["entity", self._publish_type_field, "version_number", "path"],
        )

        items = []
        for r in range(self.rowCount()):
            state_item = QtGui.QStandardItem()
            state_item.setCheckable(True)
            state_item.setCheckState(QtCore.Qt.CheckState.Checked)
            items.append(state_item)
        self.insertColumn(0, items)

        self._refresh_data()

    def _before_data_processing(self, data):
        """
        Called just after data has been retrieved from Shotgun but before any
        processing takes place.

        .. note:: You can subclass this if you want to perform summaries,
            calculations and other manipulations of the data before it is
            passed on to the model class.

        :param data: A shotgun dictionary or a list of shotgun dictionary, as returned by a CRUD SG API call.
        :returns: Should return a shotgun dictionary or a list of shotgun dictionary, of the same form as the
            input.
        """

        # need to re-order the published files by task then published file type and name in order to only keep the
        # latest version of each file
        data_to_keep = []
        publishes = {}
        for publish in data:
            publishes_by_task = publishes.setdefault(publish["task"]["id"], {})
            publishes_by_type = publishes_by_task.setdefault(
                publish[self._publish_type_field]["id"], {}
            )
            publishes_by_name = publishes_by_type.setdefault(publish["name"], [])
            if publishes_by_name:
                continue
            else:
                data_to_keep.append(publish)
                publishes_by_name.append(publish)

        return data_to_keep
