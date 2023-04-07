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

HookBaseClass = sgtk.get_hook_baseclass()


class ExtraBuildActions(HookBaseClass):

    ##############################################################################################################
    # public interface - to be overridden by deriving classes

    def pre_build_action(self, items):
        """
        This method is executed just before the files are loaded into the current scene.

        :param items:  List of dictionaries where each item represents a file to load. Each dictionary contains a
                       *sg_data* key to store the Shotgun data and an *action_name* refering to the name of the action
                       which is going to be used to load the file.
        """
        self.logger.debug("Running pre_build_action() method...")

    def post_build_action(self, items):
        """
        This method is executed just after the files have been loaded into the current scene.

        :param items:  List of dictionaries where each item represents a loaded file. Each dictionary contains a
                       *sg_data* key to store the Shotgun data and an *action_name* refering to the name of the action
                       used to load the file.
        """
        self.logger.debug("Running post_build_action() method...")

    def process_missing_files(self, items):
        """
        This method is called after the build process but before the post_build_action
        is executed. It allows you to perform some actions on the files that were previously loaded to the scene but
        aren't linked to the parent asset anymore.


        :param items:  List of dictionaries where each item represents a loaded file. Each dictionary contains a
                       *sg_data* key to store the Shotgun data.
        """
        self.logger.debug("Running process_missing_files() method...")
