Flow Production Tracking Scene Builder, |release|
#################################################

Overview
********

The Scene Builder app automates building a scene from the files published on
the pipeline steps the current task depends on. Instead of browsing the Loader
for each upstream file, the artist opens the Scene Builder, picks a preset and
clicks **Build**: the app finds the latest version of every matching published
file, loads the ones that are not in the scene yet and updates the ones that are
out of date.

For example, a rigger working on an asset can reference the latest Model of
that asset, and a layout artist working on a shot can reference the latest Rig
of every asset linked to the shot.

The Scene Builder relies on two other apps, which must be configured in the same
environment:

- **tk-multi-loader2** loads the published files. The Scene Builder runs the
  Loader actions named in its presets, such as ``reference`` or ``import`` in
  Maya, so files are loaded exactly as if the artist used the Loader.
- **tk-multi-breakdown2** scans the current scene to find the published files
  that are already loaded, so the Scene Builder can tell which files are up to
  date, out of date or no longer expected, and updates the out of date ones.

.. note:: Scene Breakdown matches the files loaded in the scene to published
    files by path. Published files must be stored under a storage root of the
    configuration for the Scene Builder to show them as loaded.

How it Works
============

#. When the dialog opens, Scene Breakdown scans the current scene for loaded
   published files.
#. For the selected preset, each action queries Flow Production Tracking for
   the published files matching its filters and its Published File Types.
   Filters can use tokens resolved from the current context, such as the
   current entity, task or upstream steps. See :ref:`scenebuilder-presets`.
#. Only the latest version of each published file is kept, per task, Published
   File Type and name.
#. Each file is compared with the scene and grouped by status. See
   :ref:`scenebuilder-statuses`.
#. When the artist clicks **Build**, the checked files are loaded or updated,
   with hook methods called before and after the build. See
   :ref:`scenebuilder-build`.

The following sections describe how to configure, use and customize the app.

.. toctree::
    :maxdepth: 2

    configuration
    user_interface
    customizing
