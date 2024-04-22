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

from .model import FileModel

delegates = sgtk.platform.import_framework("tk-framework-qtwidgets", "delegates")
ViewItemDelegate = delegates.ViewItemDelegate
ViewItemAction = delegates.ViewItemAction


def create_file_delegate(view):
    """
    Create and return the ViewItemDelegate for the view.

    :param view: The view to create the delegate for.
    :return: The delegate for the view
    """

    # create the delegate
    delegate = ViewItemDelegate(view)

    view.setMouseTracking(True)

    # set the delegate properties
    delegate.selection_brush = QtCore.Qt.NoBrush
    delegate.show_hover_selection = False
    delegate.thumbnail_width = 150

    # set the delegate model data roles
    delegate.text_role = FileModel.TEXT_ROLE

    delegate.add_actions(
        [
            {
                "type": ViewItemAction.TYPE_CHECK_BOX,
                "show_always": True,
                "get_data": get_file_item_state,
            },
            {
                "icon": QtGui.QIcon(),  # The get_data callback will set the icon based on status
                "icon_size": QtCore.QSize(20, 20),
                "show_always": True,
                "features": QtGui.QStyleOptionButton.Flat,
                "get_data": get_status_icon,
            },
        ],
        ViewItemDelegate.LEFT,
    )

    return delegate


def get_file_item_state(parent, index):
    """
    Callback function triggered by the ViewItemDelegate.
    Get the state of the file item (selected vs unselected).

    :param parent: The parent of the ViewItemDelegate which triggered this callback
    :type parent: QAbstractItemView
    :param index: The index the action is for.
    :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`

    :return: The data for the action and index.
    :rtype: dict (see the ViewItemAction class attribute `get_data` for more details)
    """

    if index.data(FileModel.TYPE_ROLE) == FileModel.GROUP_TYPE:
        return {"visible": False}

    if index.data(FileModel.STATUS_ROLE) in [
        FileModel.STATUS_INVALID,
        FileModel.STATUS_UP_TO_DATE,
    ]:
        return {"visible": False}

    checkbox_state = index.data(QtCore.Qt.CheckStateRole)

    state = QtGui.QStyle.State_Active | QtGui.QStyle.State_Enabled
    if checkbox_state == QtCore.Qt.Checked:
        state |= QtGui.QStyle.State_On
    elif checkbox_state == QtCore.Qt.PartiallyChecked:
        state |= QtGui.QStyle.State_NoChange
    else:
        state |= QtGui.QStyle.State_Off

    return {
        "visible": True,
        "state": state,
    }


def get_status_icon(parent, index):
    """
    Return the action data for the status action icon, and for the given index.
    This data will determine how the action icon is displayed for the index.

    :param parent: This is the parent of the :class:`ViewItemDelegate`, which is the file view.
    :type parent: :class:`GroupItemView`
    :param index: The index the action is for.
    :type index: :class:`sgtk.platform.qt.QtCore.QModelIndex`
    :return: The data for the action and index.
    :rtype: dict, e.g.:
    """

    if index.data(FileModel.TYPE_ROLE) == FileModel.GROUP_TYPE:
        return {"visible": False}

    # get the path to the icon
    status = index.data(FileModel.STATUS_ROLE)
    icon_path = FileModel.STATUS_ICON_PATHS.get(status)
    icon = QtGui.QIcon(icon_path)

    return {"visible": True, "icon": icon}
