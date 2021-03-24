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


class SceneBuilderApp(sgtk.platform.Application):
    """
    """

    def init_app(self):
        """
        Called as the application is being initialized
        """

        self.engine.register_command(
            "Scene Builder...", self.run_app, {"short_name": "scene_builder"}
        )

    def run_app(self):
        """
        :return:
        """
        self.logger.debug("Running Scene Builder app...")