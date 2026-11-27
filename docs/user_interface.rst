User Interface
==============

The Scene Builder registers a **Scene Builder...** command in the engine menu.
The dialog lists the published files found by the selected preset, with their
thumbnail, entity, task, name, Published File Type and version.

At the top of the dialog:

- The preset selector switches between the presets configured for the current
  environment and reloads the files.
- The **Best matching step only** check box shows only the files of the
  preferred upstream step of each entity. See
  :ref:`scenebuilder-best-matching-step`.
- The filter field shows only the files whose entity, name, Published File Type
  or task contains the text, case-insensitively.
- **Check All** and **Uncheck All** check or uncheck the **Ready to Build** and
  **Out of Date** files currently shown, so they can be used together with the
  filter.

At the bottom, next to the **Build** button, a counter shows how many
**Ready to Build** and **Out of Date** files are checked. It includes the files
hidden by the filter field, but not the files hidden by the **Best matching
step only** option.

.. _scenebuilder-statuses:

File Statuses
-------------

Files are grouped by status. Within each group, they are sorted by entity name,
then by the position of their step in the ``step_dependencies`` list, then by
name.

- **Loaded**: the latest version is already in the scene. Nothing is done at
  build time.
- **Out of Date**: an older version is in the scene. When checked, it is
  updated to the latest version at build time, through Scene Breakdown.
- **Ready to Build**: the file is not in the scene yet. When checked, it is
  loaded at build time with the Loader action of its Published File Type.
- **Invalid Loaded**: the file is in the scene but is not one of the files found
  by the preset, for example because its asset was unlinked from the shot. These
  files are passed to the ``process_missing_files`` hook method at build time,
  which does nothing by default. See :ref:`scenebuilder-actions-hook`.

.. _scenebuilder-build:

Build
-----

Clicking **Build** processes every checked file, including files hidden by the
filter field. Files hidden by the **Best matching step only** option are always
unchecked, so they are not built. The build runs as follows:

#. The ``pre_build_action`` hook method is called with the checked files.
#. The checked **Ready to Build** files are loaded with their Loader actions,
   and the checked **Out of Date** files are updated to their latest version.
#. The ``process_missing_files`` hook method is called with the **Invalid
   Loaded** files.
#. The ``post_build_action`` hook method is called with the checked files, and
   the built files move to the **Loaded** group.
