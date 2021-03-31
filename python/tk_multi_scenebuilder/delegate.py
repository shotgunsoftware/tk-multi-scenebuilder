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

views = sgtk.platform.import_framework("tk-framework-qtwidgets", "views")
EditSelectedWidgetDelegate = views.EditSelectedWidgetDelegate

shotgun_model = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_model"
)


class FileDelegate(EditSelectedWidgetDelegate):
    """
    """

    def __init__(self, view):
        """
        Class constructor.

        :param view:       The view where this delegate is being used
        :param file_view:  Main file view
        :param file_model: Model used by the main file view
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
            return QtGui.QCheckBox(parent)
        elif model_index.column() == 4:
            return QtGui.QComboBox(parent)
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

        widget.setStyleSheet("margin:5px;")

        # checkbox column
        if model_index.column() == 0:
            widget.setStyleSheet("margin-left:10px;")
            widget.setChecked(True)

        # thumbnail column
        elif model_index.column() == 1:
            widget.setMinimumSize(QtCore.QSize(96, 75))
            widget.setMaximumSize(QtCore.QSize(96, 75))
            widget.setScaledContents(True)
            icon = shotgun_model.get_sanitized_data(
                model_index, QtCore.Qt.DecorationRole
            )
            if icon:
                pixmap = icon.pixmap(512)
                widget.setPixmap(pixmap)

        # text and combobox columns
        else:
            data = model_index.data()
            sg_data = model_index.data(
                shotgun_model.ShotgunModel.SG_ASSOCIATED_FIELD_ROLE
            )

            # combobox column
            if model_index.column() == 4:
                widget.addItem(data)
                widget.setFixedHeight(50)
                widget.setStyleSheet("margin-top:25px;")
            else:
                if "local_path" in sg_data.keys():
                    widget.setText(sg_data["local_path"])
                else:
                    widget.setText(data)
