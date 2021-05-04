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

from .utils import resolve_filters

shotgun_data = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_data"
)
ShotgunDataRetriever = shotgun_data.ShotgunDataRetriever


class FileModel(QtGui.QStandardItemModel):
    """
    The FileModel maintains a model of all the Published Files found when querying SG according to the settings defined
    in the config. Each Published File is represented by a row in the model where the columns are SG fields.
    """

    _BASE_ROLE = QtCore.Qt.UserRole + 32
    (
        SG_DATA_ROLE,
        ACTION_ROLE,
        STATUS_ROLE,
        SCENE_ITEM_ROLE,
    ) = range(_BASE_ROLE, _BASE_ROLE + 4)

    (
        STATUS_UP_TO_DATE,
        STATUS_OUT_OF_SYNC,
        STATUS_NOT_LOADED
    ) = range(3)

    def __init__(self, parent, bg_task_manager, loader_app, breakdown_manager):
        """
        Class constructor.

        :param parent:          The parent QObject for this instance
        :param bg_task_manager: A BackgroundTaskManager instance that will be used for all background/threaded
                                work that needs undertaking
        :param loader_app:      Instance of the Loader application
        :param breakdown_manager:
        """

        QtGui.QStandardItemModel.__init__(self, parent)

        self._scene_items = []
        self._app = sgtk.platform.current_bundle()
        self._loader_app = loader_app
        self._breakdown_manager = breakdown_manager

        self._pending_requests = {}

        # sg data retriever is used to download thumbnails and perform SG queries in the background
        self._sg_data_retriever = ShotgunDataRetriever(bg_task_manager=bg_task_manager)
        self._sg_data_retriever.work_completed.connect(
            self._on_data_retriever_work_completed
        )
        self._sg_data_retriever.work_failure.connect(
            self._on_data_retriever_work_failed
        )
        self._sg_data_retriever.start()

        # for backwards compatibility, we need to query the entity type that this toolkit uses for its Publishes
        # as well as the field name used for the published file type
        self.publish_entity_type = sgtk.util.get_published_file_entity_type(self._app.sgtk)
        if self.publish_entity_type == "PublishedFile":
            self._publish_type_field = "published_file_type"
        else:
            self._publish_type_field = "tank_type"

        # define the columns we want to load in the model
        self.__COLUMNS = ["entity", self._publish_type_field, "version_number", "path"]

    def destroy(self):
        """
        Called to clean-up and shutdown any internal objects when the model has been finished
        with. Failure to call this may result in instability or unexpected behaviour!
        """

        # clear the model
        self.clear()

        # stop the data retriever
        if self._sg_data_retriever:
            self._sg_data_retriever.stop()
            self._sg_data_retriever.deleteLater()
            self._sg_data_retriever = None

    def load_data(self, preset_name):
        """
        Load the model data

        :param preset_name:  Name of the preset we want to load data for
        """

        self.clear()

        # scan the scene to get all the already loaded items
        self._scene_items = self._breakdown_manager.scan_scene()

        for preset in self._app.get_setting("presets"):
            if preset["title"] != preset_name:
                continue

            for action in preset["actions"]:

                publish_type_filters = [
                    "{}.PublishedFileType.code".format(self._publish_type_field),
                    "in",
                    list(action["action_mappings"].keys()),
                ]

                # ensure we have all the SG fields needed by the loader application to perform its actions
                fields = self._loader_app.import_module(
                    "tk_multi_loader.constants"
                ).PUBLISHED_FILES_FIELDS + [self._publish_type_field]
                filters = resolve_filters(action["context"]) + [publish_type_filters]
                order = [{"field_name": "version_number", "direction": "desc"}]

                # execute SG query in the background
                find_uid = self._sg_data_retriever.execute_find(
                    self.publish_entity_type, filters, fields, order
                )
                self._pending_requests[find_uid] = action["action_mappings"]

    def _on_data_retriever_work_completed(self, uid, request_type, data):
        """
        Slot triggered when the data-retriever has finished doing some work. The data retriever is currently
        just used to download thumbnails for published files so this will be triggered when a new thumbnail
        has been downloaded and loaded from disk.

        :param uid:             The unique id representing a task being executed by the data retriever
        :param request_type:    A string representing the type of request that has been completed
        :param data:            The result from completing the work
        """
        if uid not in self._pending_requests:
            return

        if request_type == "find":
            publishes = {}
            action_mappings = self._pending_requests.pop(uid)
            for publish in data["sg"]:

                row_items = []

                # in that case, we only want to keep the latest version of the published file and not all of its history
                publishes_by_task = publishes.setdefault(publish["task"]["id"], {})
                publishes_by_type = publishes_by_task.setdefault(
                    publish[self._publish_type_field]["id"], {}
                )
                # publishes_by_name = publishes_by_type.setdefault(publish["name"], {})
                publish_item = publishes_by_type.setdefault(publish["name"], None)

                if publish_item:
                    # already find a version for this file
                    if publish_item.data(self.STATUS_ROLE) == self.STATUS_UP_TO_DATE:
                        continue
                    already_loaded, scene_item = self._is_publish_already_loaded(publish["id"])
                    if already_loaded:
                        publish_item.setData(self.STATUS_OUT_OF_SYNC, self.STATUS_ROLE)
                        publish_item.setData(scene_item, self.SCENE_ITEM_ROLE)

                else:

                    # get the action to perform according to the published file type
                    action_name = action_mappings.get(
                        publish[self._publish_type_field]["name"]
                    )

                    # create an item to manage the state of the file (checked or not) in order for the user to choose if
                    # he wants this file to be loaded when building the scene
                    # we're also using this item to store important data
                    state_item = QtGui.QStandardItem()
                    state_item.setCheckable(True)
                    state_item.setCheckState(QtCore.Qt.CheckState.Checked)
                    state_item.setData(publish, self.SG_DATA_ROLE)
                    state_item.setData(action_name, self.ACTION_ROLE)
                    row_items.append(state_item)

                    status_item = QtGui.QStandardItem()
                    if self._is_publish_already_loaded(publish["id"])[0]:
                        status_item.setData(self.STATUS_UP_TO_DATE, self.STATUS_ROLE)
                    else:
                        status_item.setData(self.STATUS_NOT_LOADED, self.STATUS_ROLE)
                    row_items.append(status_item)

                    # create an item for the thumbnail and download it in a background process
                    thumbnail_item = QtGui.QStandardItem()
                    row_items.append(thumbnail_item)
                    thumbnail_id = self._sg_data_retriever.request_thumbnail(
                        publish["image"], publish["type"], publish["id"], "image"
                    )
                    self._pending_requests[thumbnail_id] = thumbnail_item

                    # finally, create an item for each SG field
                    for field_name in self.__COLUMNS:
                        if field_name in publish.keys():
                            item = QtGui.QStandardItem()
                            item.setData(publish[field_name], self.SG_DATA_ROLE)
                            row_items.append(item)

                    self.insertRow(0, row_items)

                    publishes_by_type[publish["name"]] = status_item

        elif request_type == "check_thumbnail":
            thumbnail_item = self._pending_requests.pop(uid)
            thumb_path = data.get("thumb_path")
            if thumb_path:
                thumbnail_item.setIcon(QtGui.QPixmap(thumb_path))
                thumbnail_item.emitDataChanged()

        else:
            del self._pending_requests[uid]

    def _on_data_retriever_work_failed(self, uid, error_msg):
        """
        Slot triggered when the data retriever fails to do some work!

        :param uid:         The unique id representing the task that the data retriever failed on
        :param error_msg:   The error message for the failed task
        """
        if uid in self._pending_requests:
            del self._pending_requests[uid]
        self._app.logger.debug(
            "File Model: Failed to find sg_data for id %s: %s" % (uid, error_msg)
        )

    def _is_publish_already_loaded(self, publish_id):
        """
        :param publish_id:
        :return:
        """
        for scene_item in self._scene_items:
            if scene_item.sg_data["id"] == publish_id:
                return True, scene_item
        return False, None
