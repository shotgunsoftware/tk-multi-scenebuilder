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

views = sgtk.platform.import_framework("tk-framework-qtwidgets", "views")
EditSelectedWidgetDelegate = views.EditSelectedWidgetDelegate


class FileDelegate(EditSelectedWidgetDelegate):
    """
    Custom delegate used to display the file items in the view.
    """

    ITEM_STATUS_ICONS = {
        FileModel.STATUS_UP_TO_DATE: QtGui.QIcon(":/tk-multi-scenebuilder/uptodate.png"),
        FileModel.STATUS_OUT_OF_SYNC: QtGui.QIcon(":/tk-multi-scenebuilder/outofdate.png"),
        FileModel.STATUS_NOT_LOADED: QtGui.QIcon(":/tk-multi-scenebuilder/missing.png")
    }

    def __init__(self, view):
        """
        Class constructor.

        :param view:       The view where this delegate is being used
        """

        EditSelectedWidgetDelegate.__init__(self, view)

    def _get_painter_widget(self, model_index, parent):
        """
        Constructs a widget to act as the basis for the paint event. If
        a widget has already been instantiated for this model index, that
        widget will be reused, otherwise a new widget will be instantiated
        and cached.

        :param model_index: The index of the item in the model to return a widget for
        :type model_index:  :class:`~PySide.QtCore.QModelIndex`
        :param parent:      The parent view that the widget should be parented to
        :type parent:       :class:`~PySide.QtGui.QWidget`
        :returns:           A QWidget to be used for painting the current index
        :rtype:             :class:`~PySide.QtGui.QWidget`
        """
        if model_index.column() == 0:
            # in case of the state column, we want to use the default behavior to avoid managing the checkbox state
            return None
        else:
            return QtGui.QLabel(parent)

    def _create_editor_widget(self, model_index, style_options, parent):
        """
        Called when a cell is being edited.

        :param model_index:     The index of the item in the model to return a widget for
        :type model_index:      :class:`~PySide.QtCore.QModelIndex`

        :param style_options:   Specifies the current Qt style options for this index
        :type style_options:    :class:`~PySide.QtGui.QStyleOptionViewItem`

        :param parent:          The parent view that the widget should be parented to
        :type parent:           :class:`~PySide.QtGui.QWidget`

        :returns:               A QWidget to be used for editing the current index
        :rtype:                 :class:`~PySide.QtGui.QWidget`
        """
        return self._get_painter_widget(model_index, parent)

    def _on_before_selection(self, widget, model_index, style_options):
        """
        Called when the associated widget is selected. This method
        implements all the setting up and initialization of the widget
        that needs to take place prior to a user starting to interact with it.

        :param widget: The widget to operate on (created via _create_widget)
        :param model_index: The model index to operate on
        :param style_options: QT style options
        """
        # do std drawing first
        self._on_before_paint(widget, model_index, style_options)

    def _on_before_paint(self, widget, model_index, style_options):
        """
        Called by the base class when the associated widget should be
        painted in the view. This method should implement setting of all
        static elements (labels, pixmaps etc) but not dynamic ones (e.g. buttons)

        :param widget: The widget to operate on (created via _create_widget)
        :param model_index: The model index to operate on
        :param style_options: QT style options
        """

        # checkbox column
        if model_index.column() == 0:
            pass

        else:

            widget.setStyleSheet("margin: 5px;")

            if model_index.column() == 1:
                icon = self.ITEM_STATUS_ICONS.get(model_index.data(FileModel.STATUS_ROLE), QtGui.QIcon())
                pixmap = icon.pixmap(512)
                widget.setPixmap(pixmap)
                widget.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

            # thumbnail column
            elif model_index.column() == 2:
                widget.setMinimumSize(QtCore.QSize(96, 75))
                widget.setMaximumSize(QtCore.QSize(96, 75))
                widget.setScaledContents(True)
                icon = model_index.data(QtCore.Qt.DecorationRole)
                if icon:
                    pixmap = icon.pixmap(512)
                    widget.setPixmap(pixmap)

            # text columns
            else:

                sg_data = model_index.data(FileModel.SG_DATA_ROLE)

                if isinstance(sg_data, dict) and "local_path" in sg_data.keys():
                    data = sg_data["local_path"]
                elif isinstance(sg_data, dict) and "name" in sg_data.keys():
                    data = sg_data["name"]
                else:
                    data = sg_data

                # format some data before displaying them
                if model_index.column() == 3:
                    data = "<b style='color:#18A7E3;'>{}</b>".format(data)
                elif model_index.column() == 5:
                    data = "v%03d" % int(data)

                widget.setText(data)

    def sizeHint(self, style_options, model_index):
        """
        Specify the size of the item.

        :param style_options: QT style options
        :param model_index: Model item to operate on
        """

        if model_index.column() == 0:
            return QtCore.QSize(17, 75)
        elif model_index.column() == 1:
            return QtCore.QSize(40, 75)
        elif model_index.column() == 2:
            return QtCore.QSize(96, 75)
        elif model_index.column() == 3:
            return QtCore.QSize(150, 75)
        elif model_index.column() == 4:
            return QtCore.QSize(100, 75)
        elif model_index.column() == 5:
            return QtCore.QSize(75, 75)
        else:
            return super(FileDelegate, self).sizeHint(style_options, model_index)