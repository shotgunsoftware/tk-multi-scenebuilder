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

delegates = sgtk.platform.import_framework("tk-framework-qtwidgets", "delegates")
ViewItemRolesMixin = delegates.ViewItemRolesMixin


class FileModel(QtGui.QStandardItemModel, ViewItemRolesMixin):
    """
    The FileModel maintains a model of all the Published Files found when querying PTR according to the settings defined
    in the config. Each Published File is represented by a row in the model where the columns are PTR fields.
    """

    _BASE_ROLE = QtCore.Qt.UserRole + 32
    (
        ACTION_ROLE,
        SG_DATA_ROLE,
        TEXT_ROLE,
        STATUS_ROLE,
        TYPE_ROLE,
        BREAKDOWN_DATA_ROLE,
        NEXT_AVAILABLE_ROLE,
    ) = range(_BASE_ROLE, _BASE_ROLE + 7)

    (STATUS_UP_TO_DATE, STATUS_OUTDATED, STATUS_NOT_LOADED, STATUS_INVALID) = range(4)

    GROUP_NAMES = {
        STATUS_UP_TO_DATE: "Loaded",
        STATUS_OUTDATED: "Out of Date",
        STATUS_NOT_LOADED: "Ready to Build",
        STATUS_INVALID: "Invalid Loaded",
    }

    STATUS_ICON_PATHS = {
        STATUS_UP_TO_DATE: ":/tk-multi-scenebuilder/uptodate.png",
        STATUS_OUTDATED: ":/tk-multi-scenebuilder/outofdate.png",
        STATUS_NOT_LOADED: ":/tk-multi-scenebuilder/toload.png",
        STATUS_INVALID: ":/tk-multi-scenebuilder/missing.png",
    }

    (
        GROUP_TYPE,
        FILE_TYPE,
    ) = range(2)

    # Signal emitted when all data loaded
    data_loaded = QtCore.Signal()

    class GroupItem(QtGui.QStandardItem):
        """Model item to group PublishedFiles together according to their status"""

        def __init__(self, status):
            """Class constructor"""
            self.__status = status
            self.__name = FileModel.GROUP_NAMES.get(status)
            super(FileModel.GroupItem, self).__init__()

        def data(self, role):
            """
            Override the :class:`sgtk.platform.qt.QtGui.QStandardItem` method.
            Return the data for the item for the specified role.

            :param role: The :class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole` role.
            :return: The data for the specified role.
            """

            if role == FileModel.TEXT_ROLE:
                return f"<b>{self.__name}</b>"

            elif role == FileModel.TYPE_ROLE:
                return FileModel.GROUP_TYPE

            elif role == FileModel.STATUS_ROLE:
                return self.__status

            return super(FileModel.GroupItem, self).data(role)

    class FileItem(QtGui.QStandardItem):
        """Model item to represent PublishedFile entry"""

        def __init__(self, sg_data):
            """Class constructor"""
            self.__sg_data = sg_data
            super(FileModel.FileItem, self).__init__()

        def data(self, role):
            """
            Override the :class:`sgtk.platform.qt.QtGui.QStandardItem` method.
            Return the data for the item for the specified role.

            :param role: The :class:`sgtk.platform.qt.QtCore.Qt.ItemDataRole` role.
            :return: The data for the specified role.
            """

            if role == FileModel.TEXT_ROLE:
                return f"""
                <span style='color: #18A7E3;'>Entity</span> {self.__sg_data.get('entity', {}).get('name')}<br/>
                <span style='color: #18A7E3;'>Name</span> {self.__sg_data.get('name', "")}<br/>
                <span style='color: #18A7E3;'>Type</span> {self.__sg_data.get('published_file_type', {}).get('name')}<br/>
                <span style='color: #18A7E3;'>Version</span> {self.__sg_data.get('version_number')}<br/>
                """

            elif role == FileModel.SG_DATA_ROLE:
                return self.__sg_data

            elif role == FileModel.TYPE_ROLE:
                return FileModel.FILE_TYPE

            return super(FileModel.FileItem, self).data(role)

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

        self._scene_objs = []
        self._pending_requests = {}
        self._parent_items = {}

        self._bundle = sgtk.platform.current_bundle()
        self._loader_app = loader_app
        self._breakdown_manager = breakdown_manager

        # sg data retriever is used to download thumbnails and perform PTR queries in the background
        self._sg_data_retriever = ShotgunDataRetriever(bg_task_manager=bg_task_manager)
        self._sg_data_retriever.work_completed.connect(
            self._on_data_retriever_work_completed
        )
        self._sg_data_retriever.work_failure.connect(
            self._on_data_retriever_work_failed
        )
        self._sg_data_retriever.start()

        # Add additional roles defined by the ViewItemRolesMixin class.
        self.NEXT_AVAILABLE_ROLE = self.initialize_roles(self.NEXT_AVAILABLE_ROLE)

    def clear(self):
        """Clear the model data"""

        self._parent_items = {}
        self._pending_requests = {}

        super(FileModel, self).clear()

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

        if not preset_name:
            return

        # scan the scene to get all the already loaded items
        # TODO: should we move this to the model constructor?
        self._scene_objs = self._breakdown_manager.scan_scene()

        for preset in self._bundle.get_setting("presets"):

            if preset["name"] != preset_name:
                continue

            for action in preset["actions"]:

                publish_type_filters = [
                    "published_file_type.PublishedFileType.code",
                    "in",
                    list(action["action_mappings"].keys()),
                ]

                # ensure we have all the PTR fields needed by the loader application to perform its actions
                fields = self._loader_app.import_module(
                    "tk_multi_loader.constants"
                ).PUBLISHED_FILES_FIELDS + ["published_file_type"]
                filters = resolve_filters(action["context"]) + [publish_type_filters]
                order = [{"field_name": "version_number", "direction": "desc"}]

                # execute PTR query in the background
                find_uid = self._sg_data_retriever.execute_find(
                    "PublishedFile", filters, fields, order
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

            # first, go through each published files to check if they have already been loaded to the scene
            # NOTE this routine depends on the published files sorted in descending order of version number,
            # e.g. latest version first, so that we can create the FileItem with the first published file
            # that is encountered
            for publish in data["sg"]:

                action_name = action_mappings.get(
                    publish["published_file_type"]["name"]
                )

                # make sure we're only keeping the latest version of each file and not the whole history
                publishes_by_task = publishes.setdefault(publish["task"]["id"], {})
                publishes_by_type = publishes_by_task.setdefault(
                    publish["published_file_type"]["id"], {}
                )
                publish_item = publishes_by_type.setdefault(publish["name"], None)

                if publish_item:
                    # We already have a publish item, make sure its status is correctly set
                    self.set_status(publish_item, publish)
                else:
                    # No publish item exists, create the FileItem with the latest version of the published file
                    publish_item = FileModel.FileItem(publish)
                    publish_item.setData(QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
                    publish_item.setData(action_name, self.ACTION_ROLE)
                    self.set_status(publish_item, publish)
                    self._set_parent(publish_item)
                    publishes_by_type[publish["name"]] = publish_item

                    # get the thumbnail
                    thumbnail_id = self._sg_data_retriever.request_thumbnail(
                        publish["image"], publish["type"], publish["id"], "image"
                    )
                    self._pending_requests[thumbnail_id] = publish_item

            # now, we need to take care of the object already loaded to the scene that is not associated to it anymore
            for obj in self._scene_objs:

                publishes_by_task = publishes.get(obj.sg_data["task"]["id"], {})
                publishes_by_type = publishes_by_task.get(
                    obj.sg_data["published_file_type"]["id"], {}
                )
                publish_item = publishes_by_type.get(obj.sg_data["name"], None)

                # the scene element doesn't have an associated publish file, we need to flag it to be removed
                if not publish_item:

                    publish_item = FileModel.FileItem(obj.sg_data)
                    publish_item.setData(QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
                    publish_item.setData(self.STATUS_INVALID, self.STATUS_ROLE)
                    self._set_parent(publish_item)

                    # get the thumbnail
                    thumbnail_id = self._sg_data_retriever.request_thumbnail(
                        publish["image"], publish["type"], publish["id"], "image"
                    )
                    self._pending_requests[thumbnail_id] = publish_item

            self.data_loaded.emit()

        elif request_type == "check_thumbnail":

            file_item = self._pending_requests.pop(uid)
            thumb_path = data.get("thumb_path")
            if thumb_path:
                file_item.setIcon(QtGui.QPixmap(thumb_path))
                file_item.emitDataChanged()

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
        self._bundle.logger.debug(
            "File Model: Failed to find sg_data for id %s: %s" % (uid, error_msg)
        )

    def set_status(self, item, sg_data=None, status=None):
        """Set the item status"""

        # Get the current item status
        item_status = item.data(self.STATUS_ROLE)

        # If no status is explicitly given, set the status of the item based on the given sg data
        if not status and sg_data:
            # Check if the new sg data is already loaded in the scene
            already_loaded, scene_obj = self._is_publish_already_loaded(sg_data["id"])
            file_item_sg_data = item.data(self.SG_DATA_ROLE)

            if file_item_sg_data["id"] == sg_data["id"]:
                # The sg data matches the current item data, set the status based on if it is
                # already loaded or not
                status = (
                    self.STATUS_UP_TO_DATE if already_loaded else self.STATUS_NOT_LOADED
                )
            elif already_loaded:
                # The file that was loaded for this item is now out of date
                status = self.STATUS_OUTDATED
                item.setData(scene_obj, self.BREAKDOWN_DATA_ROLE)
            else:
                return  # Nothing to do

        item.setData(status, self.STATUS_ROLE)

        # if the status has changed and the item is already parented, we need to update the parent as it won't
        if item_status != status and item.parent():
            self._set_parent(item)

    def _set_parent(self, item):
        """Set the item parent"""

        status = item.data(self.STATUS_ROLE)
        if status is None:
            return

        # the item is already parented to another item, we want to remove it from its parent without deleting the item
        if item.parent():

            row = item.row()
            parent_item = item.parent()
            parent_status = parent_item.data(self.STATUS_ROLE)

            if parent_status == status:
                return
            parent_item.takeChild(row)
            parent_item.removeRow(row)

            # if the parent doesn't have children anymore, remove it
            if not parent_item.hasChildren():
                self.removeRow(parent_item.row())
                del self._parent_items[parent_status]

        parent_item = self._parent_items.get(status)
        if not parent_item:
            parent_item = FileModel.GroupItem(status)
            self.invisibleRootItem().appendRow(parent_item)
            self._parent_items[status] = parent_item
        parent_item.appendRow(item)

    def _is_publish_already_loaded(self, publish_id):
        """Check if the published file is already loaded into the current scene"""
        for obj in self._scene_objs:
            if obj.sg_data["id"] == publish_id:
                return True, obj
        return False, None
