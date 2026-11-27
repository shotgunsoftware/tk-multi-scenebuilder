Customizing
===========

.. _scenebuilder-actions-hook:

Actions Hook
------------

The ``actions_hook`` setting points to a hook called during the build, by
default ``{self}/extra_build_actions.py``. Its methods do nothing by default
except logging. Studios can take it over to run their own logic around the
build, for example to group the loaded references or to remove the files that
are no longer expected in the scene.

.. note:: For more information on how to take over, subclass, and manage hooks,
    see the :ref:`Hooks <sgtk_hook_docs>` documentation.

Each method receives a list of dictionaries, one per file, with the following
keys:

- ``sg_data``: the Flow Production Tracking data of the published file.
- ``status``: the status of the file before the build, one of the
  ``STATUS_*`` values of the app's file model. Not set for
  ``process_missing_files``.
- ``action_name``: the name of the Loader action used to load the file. Not set
  for ``process_missing_files``.

.. py:class:: ExtraBuildActions

    .. py:method:: pre_build_action(items)

        Called just before the checked files are loaded or updated.

        :param list items: The checked files.

    .. py:method:: process_missing_files(items)

        Called after the files are loaded or updated, and before
        ``post_build_action``, with the files that are loaded in the scene but
        no longer match the selected preset.

        :param list items: The **Invalid Loaded** files.

    .. py:method:: post_build_action(items)

        Called just after the checked files are loaded or updated.

        :param list items: The checked files.

The example below logs the name of each file before it is built:

.. code-block:: python

    import sgtk

    HookBaseClass = sgtk.get_hook_baseclass()


    class ExtraBuildActions(HookBaseClass):
        def pre_build_action(self, items):
            for item in items:
                self.logger.info(
                    "Building %s with %s"
                    % (item["sg_data"]["name"], item["action_name"])
                )
