# Copyright (c) 2026 Autodesk Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk Inc.

import sys

from sgtk.platform.qt import QtGui

from .model import FileModel


class FileProxyModel(QtGui.QSortFilterProxyModel):
    """
    Filter out the hidden file items of a FileModel and filter the others by text,
    and sort them within their status group by entity name, upstream step rank and
    name. Status groups keep the order of the source model.
    """

    def __init__(self, parent):
        """
        Class constructor.

        :param parent: The parent QObject for this instance
        """
        super().__init__(parent)
        self._filter_text = ""
        self.setDynamicSortFilter(True)
        self.setRecursiveFilteringEnabled(True)

    def filterAcceptsRow(self, source_row, source_parent):
        """
        Override the :class:`sgtk.platform.qt.QtGui.QSortFilterProxyModel` method.
        Accept the file items that are not hidden and whose entity, name, type or
        task matches the filter text.

        :param source_row: The row of the item in the source model
        :param source_parent: The parent index of the item in the source model
        :return: True if the item is accepted, False otherwise
        """
        index = self.sourceModel().index(source_row, 0, source_parent)
        # Recursive filtering shows a group when one of its file items is accepted.
        if index.data(FileModel.TYPE_ROLE) == FileModel.GROUP_TYPE:
            return False
        if index.data(FileModel.HIDDEN_ROLE):
            return False
        if not self._filter_text:
            return True

        sg_data = index.data(FileModel.SG_DATA_ROLE) or {}
        values = [
            (sg_data.get("entity") or {}).get("name"),
            sg_data.get("name"),
            (sg_data.get("published_file_type") or {}).get("name"),
            (sg_data.get("task") or {}).get("name"),
        ]
        return any(self._filter_text in value.lower() for value in values if value)

    def lessThan(self, source_left, source_right):
        """
        Override the :class:`sgtk.platform.qt.QtGui.QSortFilterProxyModel` method.

        :param source_left: The left index in the source model
        :param source_right: The right index in the source model
        :return: True if the left item sorts before the right one, False otherwise
        """
        if source_left.data(FileModel.TYPE_ROLE) == FileModel.GROUP_TYPE:
            return source_left.row() < source_right.row()
        return self._get_sort_key(source_left) < self._get_sort_key(source_right)

    def set_filter_text(self, text):
        """
        Filter the file items by text, case-insensitively.

        :param text: The text to filter by, an empty string to show all items
        """
        self._filter_text = text.strip().lower()
        self.invalidateFilter()

    @staticmethod
    def _get_sort_key(index):
        """
        :param index: A file item index in the source model
        :return: A tuple to sort the file items by
        """
        sg_data = index.data(FileModel.SG_DATA_ROLE) or {}
        step_rank = index.data(FileModel.STEP_RANK_ROLE)
        return (
            ((sg_data.get("entity") or {}).get("name") or "").lower(),
            sys.maxsize if step_rank is None else step_rank,
            (sg_data.get("name") or "").lower(),
        )
